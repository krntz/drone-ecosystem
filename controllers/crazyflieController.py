#!/usr/bin/env python3

import logging
import time
from threading import Event

import cflib.crtp
import numpy as np
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.swarm import CachedCfFactory, Swarm
from utils.lighthouseDataHelper import LighthouseDataHelper
from utils.utils import FlightZone

from controllers.controller import Controller

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garret", "Joseph La Delpha", "Bitcraze AB"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"

logger = logging.getLogger(__name__)

"""
Interface with Bitcraze's Crazyflie drones
"""


class CrazyflieController(Controller):
    """
    Controller class for setting up, managing, and shutting down swarms of Crazyflies
    """

    def __init__(self,
                 uris,
                 flight_zone,
                 config):
        super().__init__(uris, flight_zone)

        self.swarm_flying = False

        # REQUIRED! Denotes for the manager whether the system is using a physical representation or not
        self._PHYSICAL = True

        cflib.crtp.init_drivers()

        factory = CachedCfFactory(rw_cache='./cache')

        self.swarm = Swarm(uris, factory=factory)

        self.swarm.open_links()

        if len(self.uris) > 1:
            data_helper = LighthouseDataHelper()

            input_is_drone = config.startswith("radio://")

            if input_is_drone:
                data_helper.read_from_drone(self.swarm._cfs[config])
            else:
                data_helper.read_from_file(config)

            # TODO: 2023-06-27 This write operation *should* be possible to do
            # in parallel, but I think there's some sort of race condition.
            # Sequential is fine for small swarms (~10 drones) so I haven't
            # bothered fixing it, but for large swarms it might be
            # worth looking into.
            self.swarm.sequential(data_helper.write_to_drone)
        else:
            logger.debug("Only one drone found, assuming it is calibrated")

    def __enter__(self):
        logger.debug("Starting swarm")

        self.safety_checks()

        self.swarm_flying = False

        self.swarm_take_off()

        self.swarm.parallel_safe(self.__start_position_logging)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Shutting down swarm")
        self.swarm.parallel_safe(self.__land)
        time.sleep(2)

        self.swarm.close_links()

        self.swarm_flying = False

    def safety_checks(self):
        """
        Performs the following pre-flight checks:
        1. Light check - Turns lights red, check for connectivity
        2. Deck check - Makes sure Lighthouse decks are installed and working
        3. Resets estimators and waits for good lock on positions
        """
        logger.info("Running pre-flight safety checks")
        logger.info(
            "Running light check. Ensure red light on all connected drones.")
        self.swarm.parallel_safe(self.__light_check)

        # TODO: This aint working for some reason...
        # logger.info("Checking for Lighthouse deck")
        # self.swarm.parallel_safe(self.__deck_check)

        logger.info(
            "Resetting estimators. Will block until good lock on position.")
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
        time.sleep(2)

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

    def __position_callback(self, timestamp, data, log_conf):
        self.positions[log_conf.cf.link_uri] = np.array(
            [data['kalman.stateX'], data['kalman.stateY'], data['kalman.stateZ']])

    def __start_position_logging(self, scf):
        log_conf = LogConfig(name='Position', period_in_ms=10)
        log_conf.add_variable('kalman.stateX', 'float')
        log_conf.add_variable('kalman.stateY', 'float')
        log_conf.add_variable('kalman.stateZ', 'float')

        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(self.__position_callback)
        log_conf.start()
