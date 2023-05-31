import logging
import time
from threading import Event

import cflib.crtp
import numpy as np
from cflib.crazyflie.swarm import CachedCfFactory, Swarm

import ReadWriteLighthouseCalibration
from boid import Boid
from utils import FlightZone


class SwarmControl:
    """
    Controller class for setting up, managing, and shutting down swarms
    """

    def __init__(self,
                 uris,
                 flight_zone,
                 config,
                 DEBUG=False) -> None:
        self.uris = uris
        self.DEBUG = DEBUG
        self.swarm_flying = False

        if type(flight_zone) is not FlightZone:
            raise TypeError("flight_zone type should be namedtuple FlightZone")

        self.flight_zone = flight_zone

        cflib.crtp.init_drivers()

        # Grab calibration data directly from drone
        # if there is a file with saved calibration data, use that instead

        if len(self.uris) > 1:
            try:
                if config.startswith("radio://"):
                    self.dprint(
                        "Getting calibration data from drone with URI: " + config)
                    mem = ReadWriteLighthouseCalibration.ReadMem(config)
                    geo_dict, calib_dict = mem.getGeoAndCalib()
                else:
                    self.dprint(
                        "Getting calibration data from file: " + config)
                    geo_dict, calib_dict = ReadWriteLighthouseCalibration.ReadFromFile(
                        config)
            except Exception as e:
                raise e
        else:
            self.dprint("Only one drone found, assuming it is calibrated")

        factory = CachedCfFactory(rw_cache='./cache')

        self.swarm = Swarm(uris, factory=factory)

        self.swarm.open_links()

        # Write calibration data to swarm

        if len(self.uris) > 1:
            self.dprint("Writing calibration data to swarm")
            args = {}

            for uri in self.uris:
                args[uri] = [geo_dict, calib_dict]

            self.swarm.parallel_safe(
                ReadWriteLighthouseCalibration.WriteMem, args)

        self.safety_checks()

        self.swarm_flying = False

    def __del__(self):
        self.dprint("Deleting")

        # Assume the swarm is flying when garbage collecting to prevent
        # flying without control software

        if hasattr(self, 'swarm'):
            self.swarm.parallel_safe(self.__land)
            time.sleep(2)

            self.swarm.close_links()

        self.swarm_flying = False

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

        # TODO: This aint working for some reason...
        # print("Checking for Lighthouse deck")
        # self.swarm.parallel_safe(self.__deck_check)

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

        commander.takeoff(self.flight_zone.floor_offset, 2.0)
        time.sleep(3)

    def swarm_take_off(self):
        self.dprint("Swarm is taking off")

        if not self.swarm_flying:
            self.swarm.sequential(self.__take_off)
            self.swarm_flying = True
        else:
            raise RuntimeError("Swarm is already flying!")

    def __land(self, scf):
        commander = scf.cf.high_level_commander

        commander.land(0.0, 4.0)
        time.sleep(3)
        commander.stop()

    def swarm_land(self, emergency_land=False):
        if self.swarm_flying or emergency_land:
            self.dprint("Landing swarm")
            self.swarm.parallel_safe(self.__land)
            self.swarm_flying = False
        else:
            raise RuntimeError("Swarm has already landed!")

    def distribute_swarm(self, drones):
        """
        Moves the swarm to their positions in a way that *should* avoid mid-air collisions.

        Requires the swarm to be flying.
        """

        if not self.swarm_flying:
            raise RuntimeError(
                "Cannot distribute swarm across flight zone, swarm is not flying!")

        self.dprint("Distributing swarm across the height of the flight zone")

        num_drones = len(drones)

        zone_width = self.flight_zone.x
        zone_length = self.flight_zone.y
        zone_height = self.flight_zone.z

        height_fragment_size = zone_height/num_drones

        current_positions = self.get_positions()
        new_positions = {uri: drone.get_position()
                         for uri, drone in drones.items()}

        self.dprint("Separating drones on Z-axis")
        positions = {uri: np.array([pos[0],
                                    pos[1],
                                    self.flight_zone.floor_offset +
                                    (i * height_fragment_size)])

                     for i, (uri, pos) in enumerate(current_positions.items())}

        self.swarm_move(positions, 0, 2)
        time.sleep(2)

        self.dprint("Moving drones to final XY-positions")
        positions = {uri: np.array([pos[0],
                                    pos[1],
                                    self.flight_zone.floor_offset +
                                    (i * height_fragment_size)])

                     for i, (uri, pos) in enumerate(current_positions.items())}

        self.swarm_move(positions, 0, 2)
        time.sleep(2)

        self.dprint("Moving drones to final Z-positions")

        self.swarm_move(new_positions, 0, 2)
        time.sleep(2)

    def __move(self, scf, x, y, z, yaw, t, relative):
        commander = scf.cf.high_level_commander

        commander.go_to(x, y, z, yaw, t, relative)

    def swarm_move(self, positions, yaw, t, relative=False):
        if not self.swarm_flying:
            raise RuntimeError("Swarm must be flying to be moved")
        # TODO: Would be awesome if this function let you leave some coordinates unchanged

        self.dprint("Moving swarm")

        args = {uri: [pos[0], pos[1], pos[2], yaw, t, relative]
                for uri, pos in positions.items()}

        self.swarm.parallel_safe(self.__move, args)

<<<<<<< HEAD
    def move_drones(self, drones, t):
        positions = {uri: drone.get_position()
                     for uri, drone in drones.items()}

        self.swarm_move(positions, 0, t, False)

    def __set_velocity(self, scf, vx, vy, vz, yawrate):
        commander = scf.cf.commander

        commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)

    def set_swarm_velocities(self, velocities):
        if not self.swarm_flying:
            raise RuntimeError("Swarm must be flying")

        args = {uri: [vel[0], vel[1], vel[2], 0]
                for uri, vel in velocities.items()}

        self.swarm.parallel_safe(self.__set_velocity, args)

    def set_drone_velocities(self, drones):
        velocities = {uri: drone.get_velocity()
                      for uri, drone in drones.items()}

        self.set_swarm_velocities(velocities)

    def get_positions(self):
        positions = self.swarm.get_estimated_positions()

        return {k: np.array([pos.x, pos.y, pos.z]) for uri, pos in positions.items()}

if __name__ == '__main__':
    DEBUG = True

    uris = {
        'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        # 'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        # 'radio://0/80/2M/E7E7E7E7E7',
        # 'radio://0/80/2M/E7E7E7E7E8',
    }

    logging.basicConfig(level=logging.INFO)
    flight_zone = FlightZone(2.0, 3.0, 1.25, 0.30)
    s = SwarmControl(uris,
                     flight_zone,
                     'radio://0/80/2M/E7E7E7E7E0',
                     DEBUG=DEBUG)

    try:
        time_step = 1

        boid_separation = 0.05
        boid_alignment = 0.05
        boid_cohesion = 0.005
        visual_range = 0.5

        drones = {}

        for uri in uris:
            drones[uri] = Boid(flight_zone,
                               uri,
                               DEBUG,
                               boid_separation,
                               boid_alignment,
                               boid_cohesion,
                               visual_range
                               )

        for _, d in drones.items():
            d.random_init()

        s.swarm_take_off()
        time.sleep(2)

        if len(uris) > 1:
            s.distribute_swarm(drones)
            time.sleep(2)
        else:
            s.move_drones(drones, 2)

        flying = True

        drone_positions = s.get_positions()

        for i, d in drones.items():
            d.set_position(drone_positions[i])
            d.set_velocity(np.array([0.2, -0.2, 0.1]))

        while flying:
            # update the positions of the drones

            # for d in drones:
            #    d.set_position(drone_positions[d.get_uri()])

            # calculate new velocities

            for uri, drone in drones.items():
                other_drones = [d for u, d in drones.items() if u is not uri]
                drone.set_new_velocity(other_drones, time_step)

            # set the drones moving
            s.set_drone_velocities(drones)

            time.sleep(time_step)

        s.swarm_land()
    except KeyboardInterrupt:
        print("Exiting")
        s.swarm_land(emergency_land=True)
    except Exception as e:
        s.swarm_land(emergency_land=True)
        raise e
    finally:
        if hasattr(s, 'swarm'):
            s.swarm.close_links()
        del s
