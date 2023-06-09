from enum import Enum

from entities.boids.boid import Boid, BoidTypes


class HermitBoid(Boid):
    @unique
    class States(Enum):
        ROAMING: int = auto()
        FEEDING: int = auto()

    def __init__(self,
                 flight_zone: any,
                 uid: str) -> None:
        super().__init__(flight_zone=flight_zone,
                         uid=uid,
                         separation=1)

        self.state = States.ROAMING

        # The HermitBoid is antisocial and prefers to keep its distance
        self.minimum_distance = 1

        self.eating_rate = 1

        self._type = BoidTypes.HERMIT

    def update(self, time_step: float) -> None:
        match self.state:
            case States.ROAMING:
                # TODO: What does the Hermit do when roaming?
                pass
            case States.FEEDING:
                # TODO: Hermit should move towards the closest active Spore
                pass

        super().update(time_step)
