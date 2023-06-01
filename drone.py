import math

import numpy as np
from numpy.random import default_rng


class Drone:
    def __init__(self, flight_zone, uid):
        self.flight_zone = flight_zone
        self._uid = uid

        self._position = np.zeros(3)
        self.yaw = 0

        self._velocity = np.zeros(3)
        self.yaw_rate = 0

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

    def set_new_position(self):
        raise NotImplementedError
