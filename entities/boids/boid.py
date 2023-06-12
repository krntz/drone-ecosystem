import logging
import math
from enum import Enum, auto, unique

import numpy as np
from entities.boids.rules import (avoid_others, keep_within_bounds,
                                  limit_velocity)
from entities.entity import Entity
from numpy.random import default_rng

logger = logging.getLogger(__name__)

# TODO: Maybe Boids should have a "perception" function to figure out what it can perceive?


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
        super().__init__(uid, 0.05)

        self._flight_zone = flight_zone

        rng = default_rng()

        self.position = np.zeros(3)
        self.yaw = 0

        self.velocity = rng.random(3) * (0.25 - (0.25 * 2))
        self.yaw_rate = 0

        self.min_speed = 0.0001
        self.max_speed = 0.25

        self.separation = separation
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

    def update_detected_boids(self, boids: list) -> None:
        """
        The boid is only able to perceive other boids within its
        limited visual range.
        """
        other_boids = filter(lambda b: b.uid is not self.uid, boids)

        self.detected_boids = list(filter(self.is_boid_in_range, other_boids))

    def get_detected_boids_of_type(self, boid_type: any) -> list:
        return list(filter(lambda b: b.type is boid_type, self.detected_boids))

    def is_boid_in_range(self, boid: any) -> bool:
        """
        Returns true if Euclidean distance to other
        boid is less than visual range. False otherise.
        """

        return self.distance_to_point(boid.position) < self.visual_range

    def distance_to_point(self, point: any) -> float:
        """
        Returns euclidean distance between the Boid's own position and some point
        """

        return np.linalg.norm(self.position - point)

    def distance_to_swarm(self, swarm: list) -> list:
        """
        Returns list of distances to all other drones
        """

        return [self.distance_to_point(boid.position) for boid in swarm]

    def perceive(self, boids: list) -> None:
        """
        Updates the boids perception of the world state.

        Should be run *at least* once per time step.
        """

        self.update_detected_boids(boids)

    def update(self, delta_time: float) -> None:
        """
        Updates the boids state based on the current world state.

        Should be run *at least* once per time step.
        """

        avoid_others(self, delta_time)
        avoid_vegetation(self, delta_time)
        keep_within_bounds(self, delta_time)
        limit_velocity(self)
