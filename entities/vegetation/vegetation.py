from entities.entity import Entity, EntityTypes


class Vegetation(Entity):
    def __init__(self,
                 uid: str,
                 position: any,
                 collision_radius: float,
                 activation_radius: float = None) -> None:

        if self.collision_radius > self.activation_radius:
            raise ValueError(
                "The collision radius cannot be larger than the activation radius.")

        super().__init__(uid, colision_radius, position)

        self._activation_radius = activation_radius

        self._active = False

        self._entity_type = EntityTypes.VEGETATION

    @property
    def activation_radius(self) -> float:
        return self._activation_radius

    @property
    def active(self):
        return self._active
