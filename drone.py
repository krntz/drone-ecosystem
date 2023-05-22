import math

from collections import namedtuple

DronePosition = namedtuple("DronePosition", "x y z")
DroneVelocity = namedtuple("DroneVelocity", "dx dy dz")

class Drone:
    def __init__(self, flight_zone, uri) -> None:
        self.flight_zone = flight_zone
        self.uri = uri
        
        self.position = DronePosition(0, 0, 0)
        self.velocity = DroneVelocity(0, 0, 0)

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

    def get_velocity(self):
        return self.velocity
