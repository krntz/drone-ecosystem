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
                 update_rate,
                 boid_separation,
                 boid_alignment,
                 boid_cohesion,
                 visual_range):

        self.flight_zone = flight_zone
        self._uid = uid
        self.update_rate = update_rate

        self.position = np.zeros(3)
        self.yaw = 0

        self.velocity = np.zeros(3)
        self.yaw_rate = 0

        self.min_speed = 0.001
        self.max_speed = 0.25

        self.minimum_distance = 0.3

        self.boid_separation = boid_separation
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

        self.velocity = (rng.random(3) * self.max_speed) - (self.max_speed * 2)
        self.yaw_rate = 0

    def distance_to_boid(self, boid_position):
        return np.linalg.norm(self.position - boid_position)

    def distance_to_swarm(self, boid_positions):
        """
        Returns list of distances to all other drones
        """

        return [self.distance_to_boid(boid.position) for boid in boids]

    @property
    def uid(self):
        return self._uid

    def set_new_velocity(self, other_boids, delta_time):
        """
        Takes the positions of all boids in the swarm, converts them to distances
        to the current boid, and figures out how to change the position
        for the next time step
        """

        logger.debug("Running rules for boid with id " + self.uid)
        # Rule 1
        fly_towards_center(self, other_boids, delta_time)
        # Rule 2
        avoid_others(self, other_boids, delta_time)
        # Rule 3
        match_velocity(self, other_boids, delta_time)

        keep_within_bounds(self, delta_time)
        limit_velocity(self)

        logger.debug(
            f"New velocity for boid with id {self.uid}: {self.velocity}")
