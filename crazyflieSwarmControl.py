import time
from threading import Event

import cflib.crtp
import numpy as np
from cflib.crazyflie.swarm import CachedCfFactory, Swarm

import ReadWriteLighthouseCalibration
from utils import FlightZone

import logging

logger = logging.getLogger(__name__)

"""
Interface with Bitcraze's Crazyflie drones
"""


class CrazyflieSwarmControl:
    """
    Controller class for setting up, managing, and shutting down swarms of Crazyflies
    """

    def __init__(self,
                 uris,
                 flight_zone,
                 config):
        self.uris = uris            # the resource identifiers of all drones
        self.swarm_flying = False
        self._PHYSICAL = True       # REQUIRED! Denotes for the boid manager whether the system is using a physical representation or not

        if type(flight_zone) is not FlightZone:
            raise TypeError("flight_zone type should be namedtuple FlightZone")

        self.flight_zone = flight_zone

        cflib.crtp.init_drivers()

        # Grab calibration data directly from drone
        # if there is a file with saved calibration data, use that instead

        if len(self.uris) > 1:
            try:
                if config.startswith("radio://"):
                    logger.info(
                        "Getting calibration data from drone with URI: " + config)
                    mem = ReadWriteLighthouseCalibration.ReadMem(config)
                    geo_dict, calib_dict = mem.getGeoAndCalib()
                else:
                    logger.info(
                        "Getting calibration data from file: " + config)
                    geo_dict, calib_dict = ReadWriteLighthouseCalibration.ReadFromFile(
                        config)
            except Exception as e:
                raise e
        else:
            logger.info("Only one drone found, assuming it is calibrated")

        factory = CachedCfFactory(rw_cache='./cache')

        self.swarm = Swarm(uris, factory=factory)

        self.swarm.open_links()

        # Write calibration data to swarm

        if len(self.uris) > 1:
            logger.info("Writing calibration data to swarm")
            args = {}

            for uri in self.uris:
                args[uri] = [geo_dict, calib_dict]

            self.swarm.parallel_safe(
                ReadWriteLighthouseCalibration.WriteMem, args)

        self.safety_checks()

        self.swarm_flying = False

        self.swarm_take_off()

    def __del__(self):
        logger.info("Deleting Crazyflie swarm")

        # Assume the swarm is flying when garbage collecting to prevent
        # flying without control software

        if hasattr(self, 'swarm'):
            self.swarm.parallel_safe(self.__land)
            time.sleep(2)

            self.swarm.close_links()

        self.swarm_flying = False

    @property
    def PHYSICAL(self):
        return self._PHYSICAL

    def safety_checks(self):
        """
        Performs the following pre-flight checks:
        1. Light check - Turns lights red, check for connectivity
        2. Deck check - Makes sure Lighthouse decks are installed and working
        3. Resets estimators and waits for good lock on positions
        """
        logger.info("Running pre-flight safety checks")
        logger.info("Running light check. Ensure red light on all connected drones.")
        self.swarm.parallel_safe(self.__light_check)

        # TODO: This aint working for some reason...
        # logger.info("Checking for Lighthouse deck")
        # self.swarm.parallel_safe(self.__deck_check)

        logger.info("Resetting estimators. Will block until good lock on position.")
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
        logger.info("Swarm is taking off")

        if not self.swarm_flying:
            self.swarm.sequential(self.__take_off)
            self.swarm_flying = True
            time.sleep(2)
        else:
            raise RuntimeError("Swarm is already flying!")

    def __land(self, scf):
        commander = scf.cf.high_level_commander

        commander.land(0.0, 4.0)
        time.sleep(3)
        commander.stop()

    def swarm_land(self, emergency_land=False):
        if self.swarm_flying or emergency_land:
            logger.info("Landing swarm")
            self.swarm.parallel_safe(self.__land)
            self.swarm_flying = False
        else:
            raise RuntimeError("Swarm has already landed!")

    def __move(self, scf, x, y, z, yaw, time_to_move, relative):
        commander = scf.cf.high_level_commander

        commander.go_to(x, y, z, yaw, time_to_move, relative)

    def swarm_move(self, positions, yaw, time_to_move, relative):
        if not self.swarm_flying:
            raise RuntimeError("Swarm must be flying to be moved")

        if time_to_move == None:
            raise ValueError("time_to_move must be set for physical systems")

        logger.info("Moving swarm")

        args = {uri: [pos[0], pos[1], pos[2], yaw, time_to_move, relative]
                for uri, pos in positions.items()}

        self.swarm.parallel_safe(self.__move, args)
        time.sleep(time_to_move)

    def __set_velocity(self, scf, vx, vy, vz, yaw_rate):
        commander = scf.cf.commander

        commander.send_velocity_world_setpoint(vx, vy, vz, yaw_rate)

    def set_swarm_velocities(self, velocities, yaw_rate):
        """
        Sets the velocity of each drone in the swarm

        :param velocities: Dict of URIs and corresponding velocities
        """

        if not self.swarm_flying:
            raise RuntimeError("Swarm must be flying")

        args = {uri: [vel[0], vel[1], vel[2], yaw_rate]
                for uri, vel in velocities.items()}

        self.swarm.parallel_safe(self.__set_velocity, args)

    def get_swarm_positions(self):
        """
        Returns a dict, keyed by URI, containing the xyz-coords for the drone swarm
        """
        positions = self.swarm.get_estimated_positions()

        return {uri: np.array([pos.x, pos.y, pos.z]) for uri, pos in positions.items()}
