from entities.entity import Entity


class Vegetation(Entity):
    def __init__(self,
                 uid: str,
                 position,
                 collision_radius: float,
                 activation_radius: float,
                 active: bool = False) -> None:

        if self.collision_radius > self.activation_radius:
            raise ValueError(
                "The collision radius cannot be larger than the activation radius.")

        super.__init__(uid, position)

        self.collision_radius = collision_radius
        self.activation_radius = activation_radius

        self.active = active
