"""
Based on Ben Eater's Javascript implementation of Boids: https://github.com/beneater/boids/blob/master/boids.js
"""

import math

import numpy as np

from drone import Drone

import logging

logger = logging.getLogger(__name__)


class Boid(Drone):
    def __init__(self,
                 flight_zone,
                 uid,
                 boid_separation,
                 boid_alignment,
                 boid_cohesion,
                 visual_range):
        super().__init__(flight_zone, uid)

        self.boid_separation = boid_separation
        self.minimum_distance = 0.2

        self.boid_alignment = boid_alignment
        self.boid_cohesion = boid_cohesion

        self.visual_range = visual_range

    def set_new_velocity(self, other_boids, time_step):
        """
        Takes the positions of all boids in the swarm, converts them to distances
        to the current boid, and figures out how to change the position
        for the next time step
        """

        logger.debug("Running rules for boid with id " + self.uid)
        # Rule 1
        self.fly_towards_center(other_boids)
        # Rule 2
        self.avoid_others(other_boids)
        # Rule 3
        self.match_velocity(other_boids)

        self.keep_within_bounds()
        self.limit_velocity()

        # new_yawrate = math.mod(
        #    180 * math.atan2(new_velocity.vx, new_velocity.vy) / math.pi, 360)

        # new_velocity = new_velocity._replace(yawrate=new_yawrate)

        self.position += self.velocity
        self.yaw = self.yaw

        logger.debug("New velocity for boid with id " + self.uid)
        logger.debug(self.velocity)

        logger.debug("New position for boid with id " + self.uid)
        logger.debug(self.position)

    def fly_towards_center(self, other_boids):
        """
        Rule 1 in the standard boids model

        Boids should fly towards the center of their swarm
        """

        center = np.zeros(3)
        num_neighbours = 0

        for boid in other_boids:
            boid_pos = boid.position

            if self.distance_to_boid(boid_pos) < self.visual_range:
                center += boid_pos
                num_neighbours += 1

        if num_neighbours > 0:
            center /= num_neighbours

            self.velocity += (center - self.position) * self.boid_cohesion
            self.yaw_rate = self.yaw_rate

    def avoid_others(self, other_boids):
        """
        Rule 2 in the standard boids model

        Keeps a distance between the boid and other boids to prevent mid-air collisions
        """

        move = np.zeros(3)

        for boid in other_boids:
            boid_pos = boid.position

            if self.distance_to_boid(boid_pos) < self.minimum_distance:
                move += self.postition - boid_pos

        self.velocity += move * self.boid_separation
        self.yaw_rate = self.yaw_rate

    def match_velocity(self, other_boids):
        """
        Rule 3 in the standard boids model

        Matches velocity (speed and direction) of the swarm
        """

        average_velocity = np.zeros(3)
        num_neighbours = 0

        for boid in other_boids:
            boid_pos = boid.position

            if self.distance_to_boid(boid_pos) < self.visual_range:
                average_velocity += boid.velocity

                num_neighbours += 1

        if num_neighbours > 1:
            average_velocity /= num_neighbours
            self.velocity += (average_velocity -
                              boid.velocity) * self.boid_alignment

    def limit_velocity(self):
        """
        Should take into account the time per each step to ensure we aren't trying to move too fast
        """

        speed_limit = 0.25

        speed = math.sqrt(np.sum(self.velocity ** 2))

        if speed > speed_limit:
            self.velocity = (self.velocity / speed) * speed_limit
            self.yaw_rate = self.yaw_rate

    def keep_within_bounds(self):
        min_x = -self.flight_zone.x/2
        max_x = self.flight_zone.x/2

        min_y = -self.flight_zone.y/2
        max_y = self.flight_zone.y/2

        min_z = self.flight_zone.floor_offset
        max_z = self.flight_zone.z

        buffer = 0.2

        turning_factor = 0.1

        # TODO: Scale velocity so the drone turns faster the further out-of-bounds it is

        if self.position[0] > (max_x - buffer):
            self.velocity[0] -= turning_factor
        elif self.position[0] < (min_x + buffer):
            self.velocity[0] += turning_factor

        if self.position[1] > (max_y - buffer):
            self.velocity[1] -= turning_factor
        elif self.position[1] < (min_y + buffer):
            self.velocity[1] += turning_factor

        if self.position[2] > ((max_z + self.flight_zone.floor_offset) - buffer):
            self.velocity[2] -= turning_factor
        elif self.position[2] < ((min_z + self.flight_zone.floor_offset) + buffer):
            self.velocity[2] += turning_factor
