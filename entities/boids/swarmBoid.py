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
                 polination_rate: int,
                 home: any) -> None:
        super().__init__(flight_zone=flight_zone,
                         uid=uid,
                         separation=1)
        self.polination_rate = polination_rate

        self.alignment = 1
        self.cohesion = 1
        self.visual_range = 0.5
        self.sensory_range = 1.0

        self.polination_range = 0.2

        self.home = home
        self.at_home = True

        self.detected_open_flowers = []
        self.detected_swarm_boids = []

        self._state = self._States.ROAMING
        self._type = BoidTypes.SWARM

    @property
    def state(self) -> any:
        return self._state

    def pollinate(self, flower: any) -> None:
        flower.pollen_level += self.polination_rate

    def perceive(self, boids: list, vegetation: list) -> None:
        super().perceive(boids, vegetation)

        self.detected_swarm_boids = self.get_entities_of_type(
            self.detected_boids, self.type)

        detected_flowers = self.get_entities_of_type(
            self.detected_vegetation, VegetationTypes.FLOWER)

        self.detected_open_flowers = sorted(
            filter(lambda f: f.open, detected_flowers),
            key=lambda f: self.distance_to_point(f.position))

    def update(self, delta_time: float) -> None:
        fly_towards_center(self, self.detected_swarm_boids, delta_time)
        match_velocity(self, self.detected_swarm_boids, delta_time)

        if self.detected_open_flowers:
            move_towards_point(
                self, self.detected_open_flowers[0].position, 1)

            if self.distance_to_point(self.detected_open_flowers[0]) < self.pollination_range:
                self.polinate(self.detected_open_flowers[0])

        super().update(delta_time)
