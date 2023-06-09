import numpy as np

from entities.entity import Entity
from entities.vegetation import mushroom.Mushroom, spore.Spore


class PowerBed(Entity):
    def __init__(self,
                 uid: str,
                 position: any,
                 size: any,
                 spore_positions: list,
                 mushroom_positions: list) -> None:
        super().__init__(uid, position)

        self._size = size

        self._spores = [Spore(f"spore{i}", pos)
                       for i, pos in enumerate(spore_positions)]

        self._mushrooms = [Mushroom(f"mushroom{i}", pos)
                          for i, pos in enumerate(mushroom_positions)]

    @property
    def spores(self) -> list:
        return self._spores

    @property
    def mushrooms(self) -> list:
        return self._mushrooms

    @property
    def size(self) -> any:
        return self._size

    def update(self) -> None:
        # check if enough Spores have been deactivated, if so, start activating mushrooms
        pass

