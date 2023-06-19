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
        POLLINATING: int = auto()
        AT_HOME: int = auto()
        MOVING: int = auto()

    def __init__(self,
                 uid: str,
                 flight_zone: any,
                 polination_rate: int,
                 home: any) -> None:
        super().__init__(flight_zone=flight_zone,
                         uid=uid,
                         separation=1)

        # TODO: 2023-06-19 The real-world starting position of the boid should
        # be saved and used as the SwarmBoids home position.
        # (Should be used if/when we want the SwarmBoids to acually land at home)

        self._polination_rate = polination_rate
        self._current_pollen = 0

        self.alignment = 1
        self.cohesion = 1
        self.visual_range = 0.5
        self.sensory_range = 1.0

        self._polination_range = 0.2

        self._home = home

        self._detected_open_flowers = []
        self._detected_swarm_boids = []

        self._state = self._States.AT_HOME
        self._type = BoidTypes.SWARM

    @property
    def state(self) -> any:
        return self._state

    def deposit_pollen(self, flower: any) -> None:
        # TODO: 2023-06-19 Maybe this should be AOE, rather than single-target?
        # The amount of pollen distributed could decrease with distance from
        # the boid.

        if (self._pollen_level - self._polination_rate) < 0:
            self._pollen_level = 0
            flower.pollen_level += self._pollen_level
        else:
            self._pollen_level -= self._polination_rate
            flower.pollen_level += self._polination_rate

    def collect_pollen(self) -> None:
        self._pollen_level += self._home.deposit_pollen()

    def perceive(self, boids: list, vegetation: list) -> None:
        """
        The SwarmBoid's "sense of perception".

        Other than the standard Boid perception system, the SwarmBoid is also
        able to detect which Boids are belonging to its swarm, and which
        Flowers are open.
        """

        super().perceive(boids, vegetation)

        self._detected_swarm_boids = self.get_entities_of_type(
            self.detected_boids, self.type)

        detected_flowers = self.get_entities_of_type(
            self.detected_vegetation, VegetationTypes.FLOWER)

        self._detected_open_flowers = sorted(
            filter(lambda f: f.open, detected_flowers),
            key=lambda f: self.distance_to_point(f.position))

    def update(self, delta_time: float) -> None:
        """
        The SwarmBoid moves pollen from its home to nearby inactive Flowers.

        The SwarmBoid returns to its home if it has either run out of pollen,
        or if it cannot detect any more inactive Flowers in its vicinity.

        """

        # TODO: 2023-06-19 Might be cool if the SwarmBoid was able to roam a
        # bit, but preferred to stay close to its home?

        fly_towards_center(self, self.detected_swarm_boids, delta_time)
        match_velocity(self, self.detected_swarm_boids, delta_time)

        if self._detected_open_flowers and self._current_pollen > 0:
            # 2023-06-19 This is quite naive. The SwarmBoid will move towards
            # the closest open flower as long as it has pollen. There might be
            # more interesting ways of implementing this behaviour?

            move_towards_point(
                self, self._detected_open_flowers[0].position, 1, delta_time)

            if self.distance_to_point(self._detected_open_flowers[0]) < self._pollination_range:
                self.deposit_pollen(self._detected_open_flowers[0])
        else:
            # 2023-06-19 Perhaps the SwarmBoid should "hunt around" for new
            # Flowers if it still has pollen left but cannot detect any open
            # Flowers? Might be some cool exploration vs. exploitation behaviours?

            move_towards_point(self, self._home.position, 1, delta_time)

            if self.distance_to_point(self._home.position) < self._home.activation_radius:
                self.collect_pollen()

        super().update(delta_time)
