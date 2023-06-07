import logging
import time

import numpy as np

logger = logging.getLogger(__name__)

"""
Manages the boids and runs the control loop.

Can handle either physical (drones) or virtual (3d or text-based) representations.
"""


class BoidManager:
    def __init__(self, controller, flight_zone, boids, time_step=None):
        """
        :param controller: controller interface object
        :param flight_zone: dimensions of the flight zone
        :param boids: List of boid-objects
        """
        self.controller = controller

        # if the controller does not provide the attribute PHYSICAL,
        # we do not know if the system should use a physical representation or not.
        # physical representations require assumptions about movement times, etc.
        if not hasattr(self.controller, 'PHYSICAL'):
            raise Exception(
                "Controller {} does not contain required information about physicallity of the system, exiting...".format(self.controller.__name___))

        self.flight_zone = flight_zone

        self.flying = False

        self.time_step = time_step

        self.boids = boids

        for boid in self.boids:
            boid.random_init()

    @property
    def velocities(self):
        return {boid.uid: boid.velocity for boid in self.boids}

    @property
    def positions(self):
        return {boid.uid: boid.position for boid in self.boids}

    def update_positions(self, positions, yaw, relative=False, time_to_move=None):
        """
        Updates the positions of the boids
        """

        self.controller.swarm_move(positions, yaw, time_to_move, relative)

    def update_velocities(self, velocities, yaw_rate):
        """
        Updates the velocities of the boids
        """

        # convert velocities from m/time_step to m/s

        if self.time_step is not None:
            velocities = {uid: vel * (1 / self.time_step) for uid, vel in velocities.items()}

        self.controller.set_swarm_velocities(velocities, yaw_rate)

    def distribute_swarm(self):
        """
        Moves the swarm to their positions in a way that *should* avoid mid-air collisions.

        Only really useful for physical systems.
        """

        logger.info("Distributing swarm across the height of the flight zone")

        num_boids = len(self.boids)

        height_fragment_size = self.flight_zone.z/num_boids

        logger.info("Separating drones on Z-axis")
        positions = {boid.uid: np.array([0, 0, i * height_fragment_size])
                     for i, boid in enumerate(self.boids)}
        logger.debug("Using the following posistions:")
        logger.debug(positions)

        self.update_positions(positions, 0, time_to_move=2, relative=True)
        time.sleep(1)

        logger.info("Moving drones to final XY-positions")
        # TODO: This cannot be a relative move
        positions = {boid.uid: np.array([boid.position[0],
                                         boid.position[1],
                                         0])

                     for boid in self.boids}
        logger.debug("Using the following posistions:")
        logger.debug(positions)

        self.update_positions(positions, 0, time_to_move=2)
        time.sleep(1)

        logger.info("Moving drones to final Z-positions")
        logger.debug("Using the following posistions:")
        logger.debug(self.positions)

        self.update_positions(self.positions, 0, time_to_move=2)
        time.sleep(1)

    def boid_loop(self):
        """
        Starts the control loop that runs the boid behaviour
        """

        if self.controller.PHYSICAL:
            logger.info("Using physical system")
            #self.distribute_swarm()
        else:
            logger.info("Using virtual system")
            #self.update_positions(self.positions, 0)

        self.flying = True

        while self.flying:
            current_positions = self.controller.swarm_positions

            for boid in self.boids:
                boid.position = current_positions[boid.uid]

            for boid in self.boids:
                # TODO: Make parallel

                other_boids = [
                    other_boid for other_boid in self.boids if other_boid.uid is not boid.uid]

                boid.set_new_velocity(other_boids, self.time_step)

            # set the boids moving
            self.update_velocities(self.velocities, 0)

            if self.time_step is not None:
                time.sleep(self.time_step)