from entities.boids.boid import Boid, BoidTypes
from entities.boids.rules import (fly_towards_center, match_velocity,
                                  move_towards_point)


class SwarmBoid(Boid):
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

        self.polination_rate = 1
        self.sensory_range = 1.0

        self.home = home
        self.at_home = True

        self.detected_inactive_flowers = []

        self._type = BoidTypes.SWARM

    def update(self, time_step: float) -> None:
        other_swarm_boids = [
            boid for boid in self.other_boids if (boid.type == self.type) and (self.distance_to_point(boid.position) <= self.visual_range)]
        fly_towards_center(self, other_swarm_boids)

        match_velocity(self, other_swarm_boids)

        if detected_inactive_flowers:
            # find the closest inactive flower and move towards that
            pass

        super().update(time_step)
