from entities.boids.boid import Boid, BoidTypes
from entities.boids.rules import (fly_towards_center, match_velocity,
                                  move_towards_point)


class HarvesterBoid(Boid):
    def __init__(self,
                 flight_zone: any,
                 uid: str,
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

        self._type = BoidTypes.HARVESTER

    def update(self, time_step: float) -> None:
        other_harvester_boids = [
            boid for boid in self.other_boids if (boid.type == self.type) and (self.distance_to_point(boid.position) <= self.visual_range)]

        fly_towards_center(self, other_harvester_boids)

        match_velocity(self, other_harvester_boids)

        if detected_active_flowers:
            # find the closest active flower and move towards that
            pass

        super().update(time_step)
