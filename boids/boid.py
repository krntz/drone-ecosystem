"""
Based on Ben Eater's Javascript implementation of Boids: https://github.com/beneater/boids/blob/master/boids.js
"""

import logging
import math

import numpy as np
from numpy.random import default_rng

from boids.rules import (avoid_others, fly_towards_center, keep_within_bounds,
                         limit_velocity, match_velocity)

logger = logging.getLogger(__name__)


class Boid:
    def __init__(self,
                 flight_zone,
                 uid,
                 boid_separation,
                 boid_alignment,
                 boid_cohesion,
                 visual_range):

        self.flight_zone = flight_zone
        self._uid = uid

        self._position = np.zeros(3)
        self.yaw = 0

        self._velocity = np.zeros(3)
        self.yaw_rate = 0

        self.boid_separation = boid_separation  # Percentage
        self.minimum_distance = 0.3

        self.boid_alignment = boid_alignment
        self.boid_cohesion = boid_cohesion

        self.visual_range = visual_range

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

    def distance_to_boid(self, boid_position):
        return math.sqrt(np.sum((self.position - boid_position) ** 2))

    def distance_to_swarm(self, boid_positions):
        """
        Returns list of distances to all other drones
        """

        return [self.distance_to_boid(boid.position) for boid in boids]

    @property
    def uid(self):
        return self._uid

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = velocity

    def set_new_velocity(self, other_boids, time_step):
        """
        Takes the positions of all boids in the swarm, converts them to distances
        to the current boid, and figures out how to change the position
        for the next time step
        """

        logger.debug("Running rules for boid with id " + self.uid)
        # Rule 1
        fly_towards_center(self, other_boids)
        # Rule 2
        avoid_others(self, other_boids)
        # Rule 3
        match_velocity(self, other_boids)

        keep_within_bounds(self)
        limit_velocity(self)

        self.position += self.velocity
        self.yaw = self.yaw

        logger.debug("New velocity for boid with id " + self.uid)
        logger.debug(self.velocity)

        logger.debug("New position for boid with id " + self.uid)
        logger.debug(self.position)
