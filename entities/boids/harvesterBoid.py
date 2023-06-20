#!/usr/bin/env python3

from entities.boids.boid import Boid, BoidTypes
from entities.boids.rules import (fly_towards_center, match_velocity,
                                  move_towards_point)

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class HarvesterBoid(Boid):
    def __init__(self,
                 uid: str,
                 flight_zone: any,
                 home: any,
                 harvesting_rate: int,
                 deposit_rate: int) -> None:
        super().__init__(flight_zone=flight_zone,
                         uid=uid,
                         separation=1)

        self._deposit_rate = deposit_rate
        self._harvesting_rate = harvesting_rate
        self._home = home

        self._alignment = 1
        self._cohesion = 1
        self._visual_range = 0.5
        self._sensory_range = 1.0

        self._harvesting_range = 0.2
        self._carrying_capacity = 10
        self._current_energy = 0

        self._detected_flowering_flowers = []
        self._detected_harvester_boids = []

        self._type = BoidTypes.HARVESTER

    def deposit_energy(self) -> None:
        pass

    def harvest_energy(self, flower: any) -> None:
        self._current_energy += flower.release_energy()

    def perceive(self, boids: list, vegetation: list) -> None:
        """
        The HarvesterBoid's "sense of perception".

        Other than the standard Boid perception system, the HarvesterBoid is
        also able to detect which Boids are belonging to its swarm, and which
        Flowers are closed.
        """

        super().perceive(boids, vegetation)

        self.detected_harvester_boids = self.get_entities_of_type(
            self._detected_boids, self._type)

        # TODO: 2023-06-19 This is a very naive and inefficient way of finding
        # a target flower. Might be more interesting/efficient methods of
        # doing it? (Similar code in swarmBoid)
        detected_flowers = self.get_entities_of_type(
            self._detected_vegetation, VegetationTypes.FLOWER)

        self._detected_flowering_flowers = sorted(
            filter(lambda f: f.flowering, detected_flowers),
            key=lambda f: self.distance_to_point(f.position))

    def update(self, delta_time: float) -> None:
        """
        The HarvesterBoid harvests energy from Flowers when they have finished
        synthesising. The energy is delivered to the HarvesterBoids hive.
        """

        fly_towards_center(self, self.detected_harvester_boids, delta_time)
        match_velocity(self, self.detected_harvester_boids, delta_time)

        has_space = self._current_energy < self._carrying_capactiy

        if has_space and self._detected_flowering_flowers:

            target_flower = self._detected_flowering_flowers[0]

            move_towards_point(self, target_flower.position, 1)

            if self.distance_to_point(target_flower.position) < self._harvesting_range:
                self.harvest_energy(target_flower)
        else:
            move_towards_point(self, self._home.position, 1)

            if self.distance_to_point(self._home.position) < self._home.activation_radius:
                self.deposit_energy()

        super().update(delta_time)
