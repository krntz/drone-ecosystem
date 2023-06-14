#!/usr/bin/env python3

import logging
import math
from enum import Enum, auto, unique

import numpy as np
from entities.boids.rules import (avoid_boids, keep_within_bounds,
                                  limit_velocity)
from entities.entity import Entity
from numpy.random import default_rng

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa", "Ben Eater"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"

logger = logging.getLogger(__name__)


@unique
class BoidTypes(Enum):
    UNDEFINED: int = auto()
    STANDARD: int = auto()
    HARVESTER: int = auto()
    SWARM: int = auto()
    HERMIT: int = auto()


class Boid(Entity):
    def __init__(self,
                 uid: str,
                 flight_zone: any,
                 separation: float) -> None:
        super().__init__(uid=uid, collision_radius=0.05)

        self._flight_zone = flight_zone

        # used to detect other boids
        self.visual_range = math.inf

        # this is mainly used to detect vegetation
        # not all boids may be "equipped" with a sensory_range,
        # in which case it's the same as the visual range
        self.sensory_range = self.visual_range

        self.position = np.zeros(3)
        self.yaw = 0

        rng = default_rng()
        self.velocity = rng.random(3) * (0.25 - (0.25 * 2))
        self.yaw_rate = 0

        self.min_speed = 0.0001
        self.max_speed = 0.25

        self.separation = separation
        # Vegetation separation must be higher since the vegetation doesn't move
        self.vegetation_separation = self.separation * 2

        # This should be considered the absolute minimum distance for the boids to prevent collisions
        self.minimum_distance = 0.3

        self.detected_boids = []

        self.detected_vegetation = []

        self._type = BoidTypes.UNDEFINED

    # We need to be able to set the positions for the boids
    @Entity.position.setter
    def position(self, position: any) -> None:
        self._position = position

    @property
    def flight_zone(self) -> any:
        return self._flight_zone

    @property
    def type(self) -> any:
        return self._type

    def get_entities_of_type(self, entities: list, entity_type: any) -> list:
        return list(filter(lambda e: e.type is entity_type, entities))

    def get_entities_in_range(self,
                              entities: list,
                              detection_range: float) -> list:

        return list(filter(lambda e: self.is_entity_in_range(e, self.detection_range), entities))

    def is_entity_in_range(self,
                           entity: any,
                           detection_range: float) -> bool:
        """
        Returns true if Euclidean distance to other
        entity is less than the specified detection range. False otherwise.
        """

        return self.distance_to_point(entity.position) < detection_range

    def distance_to_point(self, point: any) -> float:
        """
        Returns euclidean distance between the entity's own position and some point
        """

        return np.linalg.norm(self.position - point)

    def distance_to_entities(self, entities: list) -> dict:
        """
        Returns list of distances to all other drones
        """

        return {entity.uid: self.distance_to_point(entity.position) for entity in entities}

    def perceive(self, boids: list, vegetation: list) -> None:
        """
        Updates the boids perception of the world state.

        Should be run *at least* once per time step.
        """

        # TODO: I would like to generalize this to take in an arbitrary world state that
        # is made sense of using the abilities of each boid, rather than sending lists

        other_boids = filter(lambda b: b.uid is not self.uid, boids)
        self.detected_boids = self.get_entities_in_range(other_boids,
                                                         self.visual_range)

        self.detected_vegetation = self.get_entities_in_range(vegetation,
                                                              self.sensory_range)

    def update(self, delta_time: float) -> None:
        """
        Updates the boids state based on the current world state.

        Should be run *at least* once per time step.
        """

        avoid_boids(self, delta_time)
        avoid_vegetation(self, delta_time)
        keep_within_bounds(self, delta_time)
        limit_velocity(self)
