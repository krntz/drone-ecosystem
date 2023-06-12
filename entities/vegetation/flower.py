from entities.vegetation.vegetation import Vegetation


class Flower(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any,
                 collision_radius: float,
                 activation_radius: float,
                 polination_threshold: int) -> None:
        super().__init__(uid, position, collision_radius,
                         activation_radius, active)

        self.polination_threshold = polination_threshold
        self.polination_level = 0.0
