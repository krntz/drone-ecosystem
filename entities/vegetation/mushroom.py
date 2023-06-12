#!/usr/bin/env python3

from entities.vegetation.vegetation import Vegetation

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garret", "Joseph La Delpha"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class Mushroom(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any) -> None:

        super().__init__(uid=uid,
                         position=position,
                         collision_radius=0.2,
                         activation_radius=0.4)
