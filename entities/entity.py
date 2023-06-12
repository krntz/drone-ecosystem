#!/usr/bin/env python3

import abc
from enum import Enum, auto, unique

import numpy as np

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garret", "Joseph La Delpha"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


@unique
class EntityTypes(Enum):
    UNDEFINED: int = auto()
    BOID: int = auto()
    VEGETAION: int = auto()


class Entity(abc.ABC):
    def __init__(self,
                 uid: str,
                 collision_radius: float,
                 position: any = np.zeros(3)) -> None:
        self._position = position

        self._uid = uid

        self._collision_radius = collision_radius

        self._entity_type = EntityTypes.UNDEFINED

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def position(self) -> any:
        return self._position

    @property
    def collision_radius(self) -> float:
        return self._collision_radius

    @property
    def entity_type(self) -> any:
        return self._entity_type

    @abc.abstractmethod
    def update(self) -> None:
        """
        Updates the boids state based on the current world state.

        Should be run *at least* once per time step.
        """
