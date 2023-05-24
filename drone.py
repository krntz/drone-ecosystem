import math
import random

from utils import DronePosition, DroneVelocity


class Drone:
    def __init__(self, flight_zone, uri, DEBUG=False) -> None:
        self.flight_zone = flight_zone
        self.uri = uri
        self.DEBUG = DEBUG

        self.position = DronePosition(0, 0, 0, 0)

        self.velocity = DroneVelocity(0, 0, 0)

    def dprint(self, message):
        if self.DEBUG:
            print(message)

    def random_init(self):
        self.position = DronePosition(
            random.random() *
            (self.flight_zone.x - 0.2) -
            (self.flight_zone.x - 0.2) /
            2,
            random.random() *
            (self.flight_zone.y - 0.2) -
            (self.flight_zone.y - 0.2) /
            2,
            (random.random() *
             self.flight_zone.z) +
            self.flight_zone.floor_offset,
            0
        )

        self.velocity = DroneVelocity(
            random.random() * 0.1 - 0.05,
            random.random() * 0.1 - 0.05,
            random.random() * 0.1 - 0.05
        )

    def distance_to_swarm(self, boid_positions):
        """
        Returns ordered list of distances to all other drones
        """

        distances = [
            math.sqrt(
                (self.position.x - boid.x) ** 2 +
                (self.position.y - boid.y) ** 2 +
                (self.position.z - boid.z) ** 2
            )

            for boid in boids
        ]

        return distances

    def get_uri(self):
        return self.uri

    def get_position(self):
        return self.position

    def set_velocities(self, velocity):
        self.velocity = velocity

    def get_velocity(self):
        return self.velocity

    def set_new_position(self):
        raise NotImplementedError
