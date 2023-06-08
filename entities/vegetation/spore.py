from entities.vegetation.vegetation import Vegetation


class Spore(Vegetation):
    def __init__(self,
                 uid: str,
                 position,) -> None:

        super.__init(uid=uid, 
                     position=position, 
                     collision_radius=0.1,
                     activation_radius=0.2, 
                     active=False)
