from swarmControl import FlightZone

class Drone:
    def __init__(self, pos, flightZone, uri) -> None:
        self.pos = pos
        self.flightZone = flightZone
        self.uri = uri

    def getDistance(self):
        """
        Returns ordered list of distances to all other drones
        """
        raise NotImplementedError

    def getPosition(self):
        raise NotImplementedError
