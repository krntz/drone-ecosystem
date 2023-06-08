import numpy as np

from entities.entity import Entity
from entities.vegetation import mushroom.Mushroom, spore.Spore


class PowerBed(Entity):
    def __init__(self,
                 uid: str,
                 position: any,
                 spore_positions: list,
                 mushroom_positions: list,
                 radius: float) -> None:
        super.__init__(uid, position)

        self.radius = radius

        self._spores = [Spore("spore" + str(i), pos)
                       for i, pos in enumerate(spore_positions)]

        self._mushrooms = [Mushroom("mushroom" + str(i), pos)
                          for i, pos in enumerate(mushroom_positions)]

    @property
    def spores(self) -> list:
        return self._spores

    @property
    def mushrooms(self) -> list:
        return self._mushrooms
