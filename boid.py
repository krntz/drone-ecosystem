"""
Based on Ben Eater's Javascript implementation of Boids: https://github.com/beneater/boids/blob/master/boids.js
"""

from drone import Drone
from utils import DronePosition, DroneVelocity


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

    def set_new_position(self, boid_positions, time_step):
        """
        Takes the positions of all boids in the swarm, converts them to distances
        to the current boid, and figures out how to change the position
        for the next time step
        """
        self.previous_position = self.position
        self.previous_velocity = self.velocity
        
        self.fly_towards_center()
        self.avoid_others()
        self.match_velocity()

        self.keep_within_bounds(boid_positions[self.uri])

        x = self.position.x
        y = self.position.y
        z = self.position.z

        x += self.velocity.dx
        y += self.velocity.dy
        z += self.velocity.dz

        # TODO: Calculate yaw based on x and y heading
        self.position = DronePosition(x, y, z, 0)

    def fly_towards_center(self):
        """
        Rule 1 in the standard boids model
        """
        pass

    def avoid_others(self, distance_to_boids):
        """
        Rule 2 in the standard boids model
        """
        pass

    def match_velocity(self):
        """
        Rule 3 in the standard boids model
        """
        pass

    def limit_speed(self):
        """
        Should take into account the time per each step to ensure we aren't trying to move too fast
        """
        raise NotImplementedError

    def keep_within_bounds(self, position):
        min_x = -self.flight_zone.x/2
        max_x = self.flight_zone.x/2

        min_y = -self.flight_zone.y/2
        max_y = self.flight_zone.y/2

        min_z = self.flight_zone.floor_offset
        max_z = self.flight_zone.z

        buffer = 0.2

        turning_factor = 0.05

        dx = self.velocity.dx
        dy = self.velocity.dy
        dz = self.velocity.dz

        # TODO: Scale velocity so the drone turns faster the further out-of-bounds it is
        if position.x > (max_x - buffer):
            dx -= turning_factor
        elif position.x < (min_x + buffer):
            dx += turning_factor

        if position.y > (max_y - buffer):
            dy -= turning_factor
        elif position.y < (min_y + buffer):
            dy += turning_factor

        if position.z > ((max_z + self.flight_zone.floor_offset) - buffer):
            dz -= turning_factor
        elif position.z < ((min_z + self.flight_zone.floor_offset) + buffer):
            dz += turning_factor

        self.set_velocities(DroneVelocity(dx, dy, dz))
