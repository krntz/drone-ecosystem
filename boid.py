"""
Based on Ben Eater's Javascript implementation of Boids: https://github.com/beneater/boids/blob/master/boids.js
"""

from drone import Drone
from drone import DronePosition, DroneVelocity

import random

class Boid(Drone):
    def __init__(self, 
                 flight_zone, 
                 uri, 
                 boid_separation, 
                 boid_alignment, 
                 boid_cohesion):
        Drone.__init__(self, flight_zone, uri)

        self.boid_separation = boid_separation
        self.minimum_distance = 0.2

        self.boid_alignment = boid_alignment
        self.boid_cohesion = boid_cohesion

    def random_init(self):
        self.position = DronePosition(
                random.random() * self.flight_zone.x - self.flight_zone.x/2,
                random.random() * self.flight_zone.y - self.flight_zone.y/2,
                (random.random() * self.flight_zone.z) + self.flight_zone.floor_offset
                )

        self.velocity = DroneVelocity(
                random.randint(-5, 5),
                random.randint(-5, 5),
                random.randint(-5, 5)
                )

    def get_new_position(self, boid_positions):
        """
        Takes the positions of all boids in the swarm, converts them to distances
        to the current boid, and figures out how to change the position
        for the next time step
        """
        self.keep_within_bounds(boid_positions[self.uri])

    def fly_towards_center(self):
        raise NotImplementedError

    def avoid_others(self, distance_to_boids):
        raise NotImplementedError

    def match_velocity(self):
        raise NotImplementedError

    def limit_speed(self):
        raise NotImplementedError

    def keep_within_bounds(self, position):
        min_x = -self.flight_zone.x/2
        max_x = self.flight_zone.x/2

        min_y = -self.flight_zone.y/2
        max_x = self.flight_zone.y/2

        min_z = -self.flight_zone.z/2
        max_x = self.flight_zone.z/2

        buffer = 0.2

        turning_factor = 0.1

        if position.x > (max_x - buffer):
            self.dx -= turning_factor
        elif position.x < (min_x + buffer):
            self.dx += turning_factor

        if position.y > (max_y - buffer):
            self.dy -= turning_factor
        elif position.y < (min_y + buffer):
            self.dy += turning_factor 

        if position.z > (max_z + self.flight_zone.floor_offset - buffer):
            self.dz -= turning_factor
        elif position.z < (min_z + self.flight_zone.floor_offset + buffer):
            self.dz += turning_factor

    def set_velocities(self, dx, dy, dz):
        self.dx = dx
        self.dy = dy
        self.dz = dz
