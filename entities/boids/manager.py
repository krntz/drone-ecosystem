import logging
import time

logger = logging.getLogger(__name__)

"""
Manages the boids and runs the control loop.

Can handle either physical (drones) or virtual (3d or text-based) representations.
"""


class BoidManager:
    def __init__(self,
                 update_rate: float,
                 controller: any,
                 flight_zone: any,
                 boids: list) -> None:
        """
        :param update_rate: the rate at which the main loop is run
        :param controller: controller interface object
        :param flight_zone: dimensions of the flight zone
        :param boids: List of boid-objects
        """
        self._update_rate = update_rate
        self.controller = controller

        self.flight_zone = flight_zone

        self.flying = False

        self.boids = boids

    def __del__(self) -> None:
        for boid in self.boids:
            del boid

    @property
    def velocities(self) -> dict:
        return {boid.uid: boid.velocity for boid in self.boids}

    @property
    def positions(self) -> dict:
        return {boid.uid: boid.position for boid in self.boids}

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

    def boid_loop(self) -> None:
        """
        Starts the control loop that runs the boid behaviour
        """

        if self.controller.PHYSICAL:
            logger.info("Using physical system")
        else:
            logger.info("Using virtual system")

        self.flying = True

        last_tick = time.time()

        while self.flying:
            start = time.time()
            delta_time = start - last_tick

            current_positions = self.controller.positions

            # TODO: 2023-06-12 This feels inefficient...

            for boid in self.boids:
                boid.position = current_positions[boid.uid]

            for boid in self.boids:
                # TODO: Make parallel

                boid.perceive(self.boids)
                boid.update(delta_time)

            # set the boids moving
            self.update_velocities(self.velocities, 0)

            last_tick = time.time()
            time.sleep(max(self._update_rate - (time.time() - start), 0))
