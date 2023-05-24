"""
Based on Ben Eater's Javascript implementation of Boids: https://github.com/beneater/boids/blob/master/boids.js
"""

from drone import Drone
from utils import DronePosition, DroneVelocity

import math

class Boid(Drone):
    def __init__(self,
                 flight_zone,
                 uri,
                 boid_separation,
                 boid_alignment,
                 boid_cohesion,
                 DEBUG=False):
        Drone.__init__(self, flight_zone, uri, DEBUG)

        self.previous_location = None
        self.previous_velocity = None

        self.boid_separation = boid_separation
        self.minimum_distance = 0.2

        self.boid_alignment = boid_alignment
        self.boid_cohesion = boid_cohesion

    def set_new_velocity(self, boid_positions):
        """
        Takes the positions of all boids in the swarm, converts them to distances
        to the current boid, and figures out how to change the position
        for the next time step
        """
        self.previous_position = self.position
        self.previous_velocity = self.velocity
        
        new_velocity = self.velocity

        # Rule 1
        self.fly_towards_center()
        # Rule 2
        self.avoid_others()
        # Rule 3
        self.match_velocity()

        new_velocity = self.keep_within_bounds(new_velocity)
        new_velocity = self.limit_velocity(new_velocity)

        print(new_velocity)

        self.set_velocity(new_velocity)

        # TODO: Calculate yaw based on x and y heading
        #self.position = DronePosition(x, y, z, 0)

    def fly_towards_center(self):
        """
        Rule 1 in the standard boids model
        """
        pass

    def avoid_others(self):
        """
        Rule 2 in the standard boids model
        """
        pass

    def match_velocity(self):
        """
        Rule 3 in the standard boids model
        """
        pass

    def limit_velocity(self, velocity):
        """
        Should take into account the time per each step to ensure we aren't trying to move too fast
        """

        speed_limit = 0.25

        vx = velocity.vx
        vy = velocity.vy
        vz = velocity.vz

        speed = math.sqrt(vx ** 2 + vy ** 2 + vz ** 2)

        if speed > speed_limit:
            vx = (vx / speed) * speed_limit
            vy = (vy / speed) * speed_limit
            vz = (vz / speed) * speed_limit

        return DroneVelocity(vx, vy, vz)

    def keep_within_bounds(self, velocity):
        min_x = -self.flight_zone.x/2
        max_x = self.flight_zone.x/2

        min_y = -self.flight_zone.y/2
        max_y = self.flight_zone.y/2

        min_z = self.flight_zone.floor_offset
        max_z = self.flight_zone.z

        buffer = 0.2

        turning_factor = 0.1

        vx = velocity.vx
        vy = velocity.vy
        vz = velocity.vz

        # TODO: Scale velocity so the drone turns faster the further out-of-bounds it is
        if self.position.x > (max_x - buffer):
            vx -= turning_factor
        elif self.position.x < (min_x + buffer):
            vx += turning_factor

        if self.position.y > (max_y - buffer):
            vy -= turning_factor
        elif self.position.y < (min_y + buffer):
            vy += turning_factor

        if self.position.z > ((max_z + self.flight_zone.floor_offset) - buffer):
            vz -= turning_factor
        elif self.position.z < ((min_z + self.flight_zone.floor_offset) + buffer):
            vz += turning_factor

        return DroneVelocity(vx, vy, vz)
