from entities.vegetation.vegetation import Vegetation


class Mushroom(Vegetation):
    def __init__(sefl,
                 uid: str,
                 position) -> None:

        super().__init__(uid=uid,
                       position=position,
                       collision_radius=0.2,
                       activation_radius=0.4)
