from entities.vegetation.vegetation import Vegetation

class PowerFungus(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any
                 residents: list,
                 occupants: list = residents):
        super.__init__(uid = uid,
                       position = position,
                       collision_radius = 0.75,
                       activation_radius = None)
