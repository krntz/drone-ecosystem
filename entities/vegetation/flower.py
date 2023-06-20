#!/usr/bin/env python3

from enum import Enum, auto, unique

from entities.vegetation.vegetation import Vegetation, VegetationTypes

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class Flower(Vegetation):
    @unique
    class _States(Enum):
        ACTIVE: int = auto()
        SYNTHESISING: int = auto()
        INACTIVE: int = auto()

    def __init__(self,
                 uid: str,
                 position: any,
                 collision_radius: float,
                 activation_radius: float,
                 pollen_capacity: int,
                 pollen_threshold: int,
                 energy_threshold: int,
                 synthesis_rate: int) -> None:
        super().__init__(uid=uid,
                         position=position,
                         collision_radius=collision_radius,
                         activation_radius=activation_radius)

        self._pollen_capacity = pollen_capacity
        self._pollen_threshold = pollen_threshold
        self._energy_threshold = energy_threshold
        self._synthesis_rate = synthesis_rate

        self.pollen_level = 0.0
        self.energy_level = 0.0

        self._type = VegetationTypes.FLOWER

        self._state = self._States.INACTIVE

        self._open = True
        self._flowering = False

   @property
   def open(self) -> bool:
       return self._open

   @property
   def flowering(self) -> bool:
       return self._flowering

   @property
   def state(self) -> any:
       return self._state

   def release_energy(self) -> int:
       """
       Releases part of the Flowers stored energy.

       If there is just a little bit of energy left in the flower, it releases
       all of it.
       """

       if (self._pollen_level - self._release_rate) < 0:
           release_amount = self._pollen_level
       else:
           release_amount = self._release_rate

        self._pollen_level -= release_amount

        return release_amount

    def update(self) -> None:
        """
        The Flower moves between different states depending on its pollen and
        energy levels.

        The Flower only accepts new pollen at the start of the
        inactive->synthesis->active cycle.
        """

        match self._state:
            case self._States.INACTIVE:
                """
                In the inactive state, the SwarmBoids will deposit "pollen"
                in the Flower.

                Once there is enough pollen, the Flower will move to
                the synthesis state.
                """

                if self.pollen_level >= self.pollen_capacity:
                    self._open = False
                    self._state = self._States.SYNTHESISING

            case self._States.SYNTHESISING:
                """
                In the synthesis state, the Flower converts available pollen
                to energy.

                When there is enough energy, the Flower flowers and moves to
                an active state.
                """

                # TODO: These should be tuned
                self.energy_level += self._synthesis_rate
                self.pollen_level -= self._synthesis_rate

                if self.energy_level > self._energy_threshold:
                    self._state = self._States.ACTIVE
                    self._flowering = True

            case self._States.ACTIVE:
                """
                In the active state, the HarvesterBoids are attracted to the
                Flower and starts harvesting the energy.

                Once the energy has been depleted, the Flower moves back to
                its inactive state.
                """

                if self.energy_level == 0:
                    self._state = self._States.INACTIVE
                    self._flowering = False
                    self._open = True

            case _:
                raise ValueError(f"Flower with id {self._uid} has unknown state {self._state}")
