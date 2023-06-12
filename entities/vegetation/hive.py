from entities.vegetation.vegetation import Vegetation


class Hive(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any,
                 residents: list,
                 occupants: list,
                 food_threshold: int,
                 power_bed: any) -> None:
        super().__init__(uid=uid,
                         position=position,
                         collision_radius=0.5,
                         activation_radius=0.7)

        self.residents = residents
        self.occupants = occupants

        self.current_food = 0
        self._food_threshold = food_threshold

        self.power_bed = power_bed

   @property
   def food_threshold(self) -> int:
       return self._food_threshold
