#!/usr/bin/env python3

import numpy as np

from entities.entity import Entity
from entities.vegetation import mushroom.Mushroom, spore.Spore

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class PowerBed(Entity):
    def __init__(self,
                 uid: str,
                 position: any,
                 size: any,
                 num_spores: list,
                 num_mushrooms: list) -> None:
        """
        The PowerBed keeps track of all vegetation in the "world" and facilitates
        the non-autonomous interactions between the plants.

        Conceptually: Think of it like the nervous system/mycelia of the system.
        """

        super().__init__(uid, position)

        self._size = size

        self._spores = [Spore() for i in range(num_spores)]

        self._mushrooms = [Mushroom() for i in range(num_mushrooms)]

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
