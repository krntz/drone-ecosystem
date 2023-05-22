import ReadWriteLighthouseCalibration

import logging, math, time

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

from threading import Event

from collections import namedtuple

FlightZone = namedtuple("FlightZone", "x y z floorOffset")

class SwarmControl:
    """
    Controller class for setting up, managing, and shutting down swarms
    """
    
    def __init__(self, 
                 uris, 
                 flightZone,
                 config,
                 DEBUG = False) -> None:
        self.uris = uris
        self.DEBUG = DEBUG
        self.swarm_flying = False

        if type(flightZone) is not FlightZone:
            raise TypeError("flightZone type should be namedtuple FlightZone")
        
        self.flightZone = flightZone

        cflib.crtp.init_drivers()

        # Grab calibration data directly from drone
        # if there is a file with saved calibration data, use that instead
        if config.startswith("radio://"):
            self.dprint("Getting calibration data from drone with URI: " + config)
            mem = ReadWriteLighthouseCalibration.ReadMem(config)
            geo_dict, calib_dict = mem.getGeoAndCalib()
        else:
            self.dprint("Getting calibration data from file: " + config)
            geo_dict, calib_dict = ReadWriteLighthouseCalibration.ReadFromFile(config)

        factory = CachedCfFactory(rw_cache='./cache')

        self.swarm = Swarm(uris, factory=factory)

        self.swarm.open_links()

        # Write calibration data to swarm
        self.dprint("Writing calibration data to swarm")
        args = {}
        for uri in self.uris:
            args[uri] = [geo_dict, calib_dict]

        self.swarm.parallel_safe(ReadWriteLighthouseCalibration.WriteMem, args)

        self.safety_checks()

        self.swarm_flying = False

    def __del__(self):
        self.dprint("Deleting")

        # Assume the swarm is flying when garbage collecting to prevent
        # flying without control software
        self.swarm_land()
        time.sleep(2)
        self.swarm_flying = False
        
        self.swarm.close_links()

    def dprint(self, message):
        """
        Only print message if we're in debug mode
        """
        if self.DEBUG:
            print(message)

    def safety_checks(self):
        """
        Performs the following pre-flight checks:
        1. Light check - Turns lights red, check for connectivity
        2. Deck check - Makes sure Lighthouse decks are installed and working
        3. Resets estimators and waits for good lock on positions
        """
        print("Running pre-flight safety checks")
        print("Running light check. Ensure red light on all connected drones.")
        self.swarm.parallel_safe(self.__light_check)

        ## TODO: This aint working for some reason...
        #print("Checking for Lighthouse deck")
        #self.swarm.parallel_safe(self.__deck_check)

        print("Resetting estimators. Will block until good lock on position.")
        self.swarm.reset_estimators()
    
    def __light_check(self, scf):
        scf.cf.param.set_value('led.bitmask', 255)
        time.sleep(2)
        scf.cf.param.set_value('led.bitmask', 0)
        time.sleep(2)

    def __param_deck_lighthouse(self, _, value_str):
        value = int(value_str)

        if value:
            self.deck_attached_event.set()

    def __deck_check(self, scf):

        self.deck_attached_event = Event()

        scf.cf.param.add_update_callback(group="deck", 
                                         name="bcLighthouse4", 
                                         cb=self.__param_deck_lighthouse)
        time.sleep(1)

        if not self.deck_attached_event.wait(timeout=5):
            raise RuntimeError("Lighthouse deck not detected!")

    def __take_off(self, scf):
        commander = scf.cf.high_level_commander

        commander.takeoff(self.flightZone.floorOffset, 2.0)
        time.sleep(3)

    def swarm_take_off(self):
        self.dprint("Swarm is taking off")
        if not self.swarm_flying:
            self.swarm.parallel_safe(self.__take_off)
            self.swarm_flying = True
        else:
            raise RuntimeError("Swarm is already flying!")
    
    def __land(self, scf):
        commander = scf.cf.high_level_commander

        commander.land(0.0, 2.0)
        time.sleep(2)
        commander.stop()

    def swarm_land(self):
        if self.swarm_flying:
            self.dprint("Landing swarm")
            self.swarm.parallel_safe(self.__land)
            self.swarm_flying = False
        else:
            raise RuntimeError("Swarm has already landed!")
        
    def distribute_swarm(self):
        """
        Distributes the swarm inside the flight zone in a way that should avoid
        mid-air collision.

        Requires the swarm to be flying.
        """

        #TODO: Might want to distribute along XY-plane as well?

        if not self.swarm_flying:
            raise RuntimeError("Cannot distribute swarm across flight zone, swarm is not flying!")

        self.dprint("Distributing swarm across the height of the flight zone")

        numDrones = len(self.uris)
        
        zoneWidth = self.flightZone.x
        zoneLength = self.flightZone.y
        zoneHeight = self.flightZone.z

        heightFragmentSize = zoneHeight/numDrones

        positions = self.swarm.get_estimated_positions()

        args = {}
        for i, uri in enumerate(self.uris):
            args[uri] = [positions[uri].x, 
                         positions[uri].y, 
                         self.flightZone.floorOffset + (i * heightFragmentSize)
                         ]
        
        self.swarm.parallel_safe(self.__move, args)
        time.sleep(2)

    def __move(self, scf, x, y, z):
        commander = scf.cf.high_level_commander

        commander.go_to(x, y, z, 0, 2)
        time.sleep(2)

if __name__ == '__main__':
    uris = {
        'radio://0/80/2M/E7E7E7E7E0',
        #'radio://0/80/2M/E7E7E7E7E1',
        #'radio://0/80/2M/E7E7E7E7E2',
        #'radio://0/80/2M/E7E7E7E7E3',
        #'radio://0/80/2M/E7E7E7E7E4',
        #'radio://0/80/2M/E7E7E7E7E5',
        #'radio://0/80/2M/E7E7E7E7E6',
        ##'radio://0/80/2M/E7E7E7E7E7',
        #'radio://0/80/2M/E7E7E7E7E8',
    }
    
    logging.basicConfig(level=logging.ERROR)
    s = SwarmControl(uris, 
                     FlightZone(2.0, 3.0, 1.75, 0.2),
                     'radio://0/80/2M/E7E7E7E7E0',
                     DEBUG = True)
    
    try:
        s.swarm_take_off()
        time.sleep(2)
        s.distribute_swarm()
        time.sleep(2)
        s.swarm_land()
    except Exception as e:
        print(e)
        s.swarm_land()
    finally:
        s.swarm.close_links()
        del s
