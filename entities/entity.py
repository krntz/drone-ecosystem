import numpy as np


class Entity:
    def __init__(self,
                 uid: str,
                 collision_radius: float,
                 position: any = np.zeros(3)) -> None:
        self._position = position

        self._uid = uid

        self._collision_radius = collision_radius

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def position(self) -> any:
        return self._position

    @property
    def collision_radius(self) -> float:
        return self._collision_radius

    def update(self) -> None:
        raise NotImplementedError("All entities need an update function!")
