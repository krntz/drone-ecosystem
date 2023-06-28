from enum import Enum, auto, unique

from entities.boids.boid import Boid, BoidTypes


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
