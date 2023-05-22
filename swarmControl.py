import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

import logging
import math
import time

from threading import Event

from collections import namedtuple

import ReadWriteCalibration

FlightZone = namedtuple("FlightZone", "x y z floorOffset")


class SwarmControl:
    """
    Controller class for setting up, managing, and shutting down swarms
    """
    
    def __init__(self, 
                 uris, 
                 flightZone,
                 configFileName) -> None:
        self.uris = uris

        if type(flightZone) is FlightZone:
            self.flightZone = flightZone
        else:
            raise ValueError("flightZone type should be namedtuple FlightZone")

        cflib.crtp.init_drivers()
        factory = CachedCfFactory(rw_cache='./cache')

        self.swarm = Swarm(uris, factory=factory)
    
        self.deck_attached_event = Event()

        self.swarm.open_links()

        #TODO: Make it possible to switch between reading from file and reading directly from drone
        geo_dict, calib_dict = ReadWriteCalibration.ReadFromFile(configFileName)

        args = {}
        for uri in self.uris:
            args[uri] = [geo_dict, calib_dict]

        self.swarm.parallel_safe(ReadWriteCalibration.WriteMem, args)

        self.safety_checks()

        self.swarm_flying = False

    def __del__(self):
        print("Deleting")
        if self.swarm_flying:
            self.swarm_land()
            time.sleep(2)
            self.swarm_flying = False
        
        self.swarm.close_links()

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
            self.swarm.parallel_safe(self.__land)
            self.swarm_flying = False
        else:
            raise RuntimeError("Swarm has already landed!")
        
    def distribute_swarm(self):
        """
        Distributes the swarm inside the flight zone in a way that should avoid mid-air collision.
        Requires the swarm to be flying
        """

        if not self.swarm_flying:
            raise RuntimeError("Cannot distribute swarm across flight zone, swarm is not flying!")

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
        'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        'radio://0/80/2M/E7E7E7E7E3',
        'radio://0/80/2M/E7E7E7E7E4',
        'radio://0/80/2M/E7E7E7E7E5',
        'radio://0/80/2M/E7E7E7E7E6',
        #'radio://0/80/2M/E7E7E7E7E7',
        'radio://0/80/2M/E7E7E7E7E8',
    }
    
    logging.basicConfig(level=logging.ERROR)
    s = SwarmControl(uris, 
                     FlightZone(2.0, 3.0, 1.75, 0.2), 
                     "4-lighthouses.yaml")
    
    try:
        print("Taking off")
        s.swarm_take_off()
        time.sleep(2)
        print("Distributing swarm")
        s.distribute_swarm()
        time.sleep(2)
        print("Landing")
        s.swarm_land()
        print("Landed")
    except Exception as e:
        print(e)
        print("Landing swarm!")
        s.swarm_land()
    finally:
        s.swarm.close_links()
        del s