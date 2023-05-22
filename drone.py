class Drone:
    def __init__(self, boidSep, boidAlign, boidCoh) -> None:
        self.boidSep = boidSep
        self.boidAlign = boidAlign
        self.boidCoh = boidCoh
    
    def __del__(self):
        """
        When garbage collected, make sure the drones land and shut off their motors
        """
        pass

    def linear_move(self, pos, move_time):
        """
        Moves the drone linearly to the indicated position. Velocity is based on move_time.
        """

        raise NotImplementedError

    def getDistance(self):
        """
        Returns ordered list of distances to all other drones
        """
        raise NotImplementedError
    
    def boid(self):
        """
        Defines behaviours of a boid
        """
        raise NotImplementedError
