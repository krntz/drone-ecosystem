#!/usr/bin/env python3

from entities.vegetation.vegetation import Vegetation

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class Flower(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any,
                 collision_radius: float,
                 activation_radius: float,
                 polination_threshold: int) -> None:
        super().__init__(uid,
                         position,
                         collision_radius,
                         activation_radius)

        self.polination_threshold = polination_threshold
        self.polination_level = 0.0
