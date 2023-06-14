#!/usr/bin/env python3

from enum import Enum, auto, unique

from entities.boids.boid import Boid, BoidTypes
from entities.boids.rules import (fly_towards_center, match_velocity,
                                  move_towards_point)
from entities.vegetation.vegetation import VegetationTypes

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class SwarmBoid(Boid):
    @unique
    class _States(Enum):
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

        self._state = self._States.ROAMING
        self._type = BoidTypes.SWARM

    @property
    def state(self) -> any:
        return self._state

    def deposit_pollen(self, flower: any) -> None:
        # is called when we are within a certain distance of a flower
        pass

    def perceive(self, boids: list, vegetation: list) -> None:
        super().perceive(boids, vegetation)

        self.detected_harvester_boids = self.get_entities_of_type(self.detected_boids,
                                                                  self.type)

        detected_flowers = self.get_entities_of_type(self.detected_vegetation,
                                                     VegetationTypes.FLOWER)
        self.detected_inactive_flowers = list(
            filter(lambda f: not f.active, detected_flowers))

    def update(self, delta_time: float) -> None:
        if self.detected_swarm_boids:
            fly_towards_center(self, self.detected_swarm_boids, delta_time)
            match_velocity(self, self.detected_swarm_boids, delta_time)

        if self.detected_inactive_flowers:
            # find the closest inactive flower and move towards that
            distance_to_flowers = self.distance_to_entities(
                self.detected_inactive_flowers)

            closest_flower = min(distance_to_flowers,
                                 key=distance_to_flowers.get())

            # if we are close enough to the flower, start pollinating it

        super().update(delta_time)
