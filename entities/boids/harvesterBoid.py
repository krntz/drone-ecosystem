from entities.boids.boid import Boid, BoidTypes
from entities.boids.rules import (fly_towards_center, match_velocity,
                                  move_towards_point)


class HarvesterBoid(Boid):
    def __init__(self,
                 uid: str,
                 flight_zone: any,
                 home: any) -> None:
        super().__init__(flight_zone=flight_zone,
                         uid=uid,
                         separation=1)
        self.alignment = 1
        self.cohesion = 1
        self.visual_range = 0.5

        self.polination_factor = 1
        self.sensory_range = 1.0

        self.carrying_capacity = 10
        self.current_food = 0

        self.harvesting_rate = 1

        self.deposit_rate = 2

        self.depositing = False

        self.home = home
        self.at_home = True

        self.detected_active_flowers = []
        self.detected_harvester_boids = []

        self._type = BoidTypes.HARVESTER

    def perceive(self, boids: list) -> None:
        self.update_detected_boids(boids)

        self.detected_harvester_boids = self.get_detected_boids_of_type(
            self.type)

        # TODO: Perceive flowers

    def update(self, time_step: float) -> None:
        fly_towards_center(self, self.detected_harvester_boids)

        match_velocity(self, self.detected_harvester_boids)

        if self.detected_active_flowers:
            # find the closest active flower and move towards that
            pass

        super().update(time_step)
