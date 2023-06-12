import logging
import time

logger = logging.getLogger(__name__)

"""
Manages the boids and runs the control loop.

Can handle either physical (drones) or virtual (3d or text-based) representations.
"""


class BoidManager:
    def __init__(self,
                 controller: any,
                 flight_zone: any,
                 boids: list) -> None:
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

        self.boids = boids

        for boid in self.boids:
            boid.random_init()

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

    def boid_loop(self, time_step: float | None = None) -> None:
        """
        Starts the control loop that runs the boid behaviour
        """

        if self.controller.PHYSICAL:
            logger.info("Using physical system")
            # self.distribute_swarm()
        else:
            logger.info("Using virtual system")
            # self.update_positions(self.positions, 0)

        self.flying = True

        while self.flying:
            current_positions = self.controller.swarm_positions

            # TODO: 2023-06-12 This feels inefficient...

            for boid in self.boids:
                boid.position = current_positions[boid.uid]

            for boid in self.boids:
                # TODO: Make parallel

                boid.perceive(self.boids)
                boid.update(self.boids, time_step)

            # set the boids moving
            self.update_velocities(self.velocities, 0)

            if time_step is not None:
                time.sleep(time_step)
