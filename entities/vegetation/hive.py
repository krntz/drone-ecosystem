#!/usr/bin/env python3

from enum import Enum, auto, unique

from entities.vegetation.vegetation import Vegetation, VegetationTypes

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class Hive(Vegetation):
    @unique
    class _States(Enum):
        DECAYING: int = auto()
        FEEDING: int = auto()

    def __init__(self,
                 uid: str,
                 position: any,
                 energy_threshold: int,
                 feeding_rate: int) -> None:

        super().__init__(uid=uid,
                         position=position,
                         collision_radius=0.5,
                         activation_radius=0.7)

        self._energy_threshold = energy_threshold
        self._feeding_rate = feeding_rate

        self.current_energy = 0

        self._type = VegetationTypes.HIVE

        self._state = self._States.IDLE

   @property
   def energy_threshold(self) -> int:
       return self._energy_threshold

   def receive_energy(self, received_energy: int) -> None:
       """
       A HarvesterBoid can deposit energy in the Hive.
       """

       self.current_energy += received_energy

   def update(self) -> None:
       match self._state:
           case self._States.DECAYING:
               # TODO: 2023-06-19 In the future it would be cool if the Hive
               # somehow acutally decayed if it went unfed.
               # For now it just idles.

               if self.current_energy >= self._energy_threshold:
                   self._state = self._States.FEEDING

           case self._States.FEEDING:
               if (self.current_energy - self._feeding_rate) < 0:
                   self.current_energy = 0
               else:
                   self.current_energy -= self._feeding_rate

               if self.current_energy == 0:
                   self._state = self._States.DECAYING

           case _:
                raise ValueError(f"Hive with id {self._uid} has unknown state {self._state}")
