#!/usr/bin/env python3

import logging
import time

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"

logger = logging.getLogger(__name__)

"""
Manages the boids and runs the control loop.

Can handle either physical (drones or other robots) or
virtual (3d or text-based) representations.
"""


class WorldManager:
    def __init__(self,
                 update_rate: float,
                 controller: any,
                 flight_zone: any,
                 boids: list,
                 vegetation: list) -> None:
        """
        :param update_rate: the rate at which the main loop is run
        :param controller: controller interface object
        :param flight_zone: dimensions of the flight zone
        :param boids: List of boid-objects
        :param vegetation: List of vegetation-objects
        """
        self._update_rate = update_rate
        self.controller = controller

        self.flight_zone = flight_zone

        self.boids = boids
        self.vegetation = vegetation

    def __del__(self) -> None:
        for boid in self.boids:
            del boid

        for vegetation in self.vegetation:
            del vegetation

    @property
    def boid_velocities(self) -> dict:
        return {boid.uid: boid.velocity for boid in self.boids}

    @property
    def boid_positions(self) -> dict:
        return {boid.uid: boid.position for boid in self.boids}

    @property
    def vegetation_positions(self) -> dict:
        return {vegetation.uid: vegetation.position for vegetation in self.vegetation}

    def update_positions(self,
                         positions: list,
                         yaw: float,
                         relative: bool = False,
                         time_to_move: float | None = None) -> None:
        """
        Updates the positions of the boids
        """

        self.controller.swarm_move(positions, yaw, time_to_move, relative)

    def update_velocities(self, velocities: list, yaw_rate: float) -> None:
        """
        Updates the velocities of the boids
        """

        self.controller.set_swarm_velocities(velocities, yaw_rate)

    def world_loop(self) -> None:
        """
        Starts the control loop that runs the boid behaviour
        """

        if self.controller.PHYSICAL:
            logger.info("Using physical system")
        else:
            logger.info("Using virtual system")

        last_tick = time.time()

        while True:
            start = time.time()
            delta_time = start - last_tick
            current_positions = self.controller.positions

            # TODO: 2023-06-12 Looping over self.boids twice feels inefficient

            # TODO: 2023-06-12 These loops can (I think) be run in parallel.
            # That might require large changes to the swarm controller though...

            # TODO: 2023-06-16 Re parallelization: Rather than running this
            # synchronously, it may be a better idea to run the entities async
            # and have the WorldManager broadcast new world states. Each entity
            # would then run its own update loop. That would mean the boids would
            # need to communicate with the controller to update their positions
            # independently though.

            for boid in self.boids:
                boid.position = current_positions[boid.uid]

            for boid in self.boids:
                boid.perceive(self.boids, self.vegetation)
                boid.update(delta_time)

            for vegetation in self.vegetation:
                vegetation.update(time_step)

            # set the boids moving
            self.update_velocities(self.boid_velocities, 0)

            last_tick = time.time()
            time.sleep(max(self._update_rate - (time.time() - start), 0))
