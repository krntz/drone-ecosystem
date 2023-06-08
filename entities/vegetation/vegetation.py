from entities.entity import Entity


class Vegetation(Entity):
    def __init__(self,
                 uid: str,
                 position: any,
                 collision_radius: float,
                 activation_radius: float = None,
                 active: bool = False) -> None:

        if self.collision_radius > self.activation_radius:
            raise ValueError(
                "The collision radius cannot be larger than the activation radius.")

        super.__init__(uid, position)

        self._collision_radius = collision_radius
        self._activation_radius = activation_radius

        self.active = active

    @property
    def collision_radius(self) -> float:
        return self._collision_radius

    @property
    def activation_radius(self) -> float:
        return self._activation_radius
