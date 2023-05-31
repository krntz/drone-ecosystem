import math

import numpy as np
from numpy.random import default_rng


class Drone:
    def __init__(self, flight_zone, uri, DEBUG=False) -> None:
        self.flight_zone = flight_zone
        self.uri = uri
        self.DEBUG = DEBUG

        self.position = np.zeros(3)
        self.yaw = 0

        self.velocity = np.zeros(3)
        self.yaw_rate = 0

    def dprint(self, message):
        if self.DEBUG:
            print(message)

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

    def get_uri(self):
        return self.uri

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def set_velocity(self, velocity):
        self.velocity = velocity

    def get_velocity(self):
        return self.velocity

    def set_new_position(self):
        raise NotImplementedError
