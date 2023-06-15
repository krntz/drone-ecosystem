from entities.vegetation.vegetation import Vegetation


class Hive(Vegetation):
    def __init__(self,
                 uid: str,
                 position: any,
                 residents: list,
                 occupants: list,
                 food_threshold: int,
                 power_bed: any,
                 current_food: int = 0) -> None:
        super.__init__(uid=uid,
                       position=position,
                       collision_radius=0.5,
                       activation_radius=0.7,
                       active=False)

        self.residents = residents
        self.occupants = occupants

        self.current_food = current_food
        self._food_threshold = food_threshold

        self.power_bed = power_bed

   @property
   def food_threshold(self) -> int:
       return self._food_threshold
