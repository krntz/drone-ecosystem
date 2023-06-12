from entities.vegetation.vegetation import Vegetation


class Mushroom(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any) -> None:

        super().__init__(uid=uid,
                         position=position,
                         collision_radius=0.2,
                         activation_radius=0.4)
