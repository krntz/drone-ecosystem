import logging
import math
from enum import Enum, unique

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
        super().__init__(uid)

        self._flight_zone = flight_zone

        self.yaw = 0

        self.velocity = np.zeros(3)
        self.yaw_rate = 0

        self.separation = separation

        # This should be considered the absolute minimum distance for the boids to prevent collisions
        self.minimum_distance = 0.3

        self.other_boids = []

        self._type = BoidTypes.UNDEFINED

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def flight_zone(self) -> any:
        return self._flight_zone

    @property
    def type(self) -> int:
        return self._type

    def random_init(self):
        rng = default_rng()

        self.position = rng.random(3) * np.array([
            (self.flight_zone.x - 0.2) - (self.flight_zone.x - 0.2) / 2,
            (self.flight_zone.y - 0.2) - (self.flight_zone.y - 0.2) / 2,
            self.flight_zone.z + self.flight_zone.floor_offset
        ])

        self.yaw = 0

        self.velocity = rng.random(3) * (0.75 - (0.75 / 2))
        self.yaw_rate = 0

    def distance_to_point(self, point):
        """
        Returns euclidean distance between the Boid's own position and some point
        """

        return math.sqrt(np.sum((self.position - point) ** 2))

    def distance_to_swarm(self, positions):
        """
        Returns list of distances to all other drones
        """

        return [self.distance_to_point(boid.position) for boid in boids]

    def update(self, time_step) -> None:
        avoid_others(self, self.other_boids)
        keep_within_bounds(self)
        limit_velocity(self)
