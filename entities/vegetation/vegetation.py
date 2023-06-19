#!/usr/bin/env python3

from enum import Enum, auto, unique

from entities.entity import Entity, EntityTypes

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


@unique
class VegetationType(Enum):
    UNDEFINED: int = auto()
    FLOWER: int = auto()
    MUSHROOM: int = auto()
    SPORE: int = auto()
    POWER_BED: int = auto()


class Vegetation(Entity):
    def __init__(self,
                 uid: str,
                 position: any,
                 collision_radius: float,
                 activation_radius: float | None = None) -> None:

        if self.collision_radius > self.activation_radius:
            raise ValueError(
                "The collision radius cannot be larger than the activation radius.")

        super().__init__(uid, colision_radius, position)

        self._activation_radius = activation_radius

        self._active = False

        self._entity_type = EntityTypes.VEGETATION
        self._type = VegetationTypes.UNDEFINED

    @property
    def activation_radius(self) -> float | None:
        return self._activation_radius

    @property
    def active(self) -> bool:
        return self._active

    @property
    def type(self) -> any:
        return self._type
