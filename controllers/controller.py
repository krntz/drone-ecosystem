import abc

import numpy as np


class Controller(abc.ABC):
    def __init__(self, uris: list, flight_zone: any) -> None:
        self.uris = uris

        self.flight_zone = flight_zone

        self._positions = {uri: np.zeros(3) for uri in self.uris}

    @property
    @abc.abstractmethod
    def PHYSICAL(self):
        """Denotes whether the system is physical or not"""

    @property
    def positions(self):
        """The positions of the drones in the system"""

        return self._positions

    @abc.abstractmethod
    def swarm_land(self, emergency_land=False):
        """Cleanly shut down the representation"""
        # TODO: Should probably be renamed

    @abc.abstractmethod
    def swarm_move(self):
        """Broadcast positions for each drone to move to"""

    @abc.abstractmethod
    def set_swarm_velocities(self):
        """Set the velocities for x, y, and z of each drone in the swarm"""
