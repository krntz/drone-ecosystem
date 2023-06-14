#!/usr/bin/env python3

from entities.vegetation.vegetation import Vegetation

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"


class PowerFungus(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any
                 residents: list,
                 occupants: list = residents):
        super().__init__(uid=uid,
                         position=position,
                         collision_radius=0.75,
                         activation_radius=None)
