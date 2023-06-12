#!/usr/bin/env python3

from enum import Enum, auto, unique

from entities.boids.boid import Boid, BoidTypes
from entities.boids.rules import (fly_towards_center, match_velocity,
                                  move_towards_point)

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garret", "Joseph La Delpha"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class SwarmBoid(Boid):
    @unique
    class States(Enum):
        ROAMING: int = auto()
        POLLINATING: int = auto()

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

        self.polination_rate = 1
        self.sensory_range = 1.0

        self.home = home
        self.at_home = True

        self.detected_inactive_flowers = []
        self.detected_swarm_boids = []

        self._type = BoidTypes.SWARM
        self._state = self.States.ROAMING

    def deposit_pollen(self, flower: any) -> None:
        # is called when we are within a certain distance of a flower
        pass

    def perceive(self, boids: list) -> None:
        self.update_detected_boids(boids)

        self.detected_harvester_boids = self.get_detected_boids_of_type(
            self.type)

        # TODO: Perceive flowers

    def update(self, delta_time: float) -> None:
        fly_towards_center(self, self.detected_swarm_boids, delta_time)

        match_velocity(self, self.detected_swarm_boids, delta_time)

        if self.detected_inactive_flowers:
            # find the closest inactive flower and move towards that

            # if we are close enough to the flower, start pollinating it
            pass

        super().update(delta_time)
