#!/usr/bin/env python3

from enum import Enum, auto, unique

from entities.boids.boid import Boid, BoidTypes

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class HermitBoid(Boid):
    @unique
    class States(Enum):
        ROAMING: int = auto()
        FEEDING: int = auto()

    def __init__(self,
                 uid: str,
                 flight_zone: any) -> None:
        super().__init__(uid=uid,
                         flight_zone=flight_zone,
                         separation=1)

        self.state = self.States.ROAMING

        # The HermitBoid is antisocial and prefers to keep its distance
        self.minimum_distance = 1

        self.eating_rate = 1

        self._type = BoidTypes.HERMIT

    def update(self, delta_time: float) -> None:
        match self.state:
            case self.States.ROAMING:
                # TODO: What does the Hermit do when roaming?
                pass
            case self.States.FEEDING:
                # TODO: Hermit should move towards the closest active Spore
                pass

        super().update(delta_time)
