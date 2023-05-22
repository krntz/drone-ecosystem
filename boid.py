"""
Based on Ben Eater's Javascript implementation of Boids: https://github.com/beneater/boids/blob/master/boids.js
"""

from drone import Drone

class Boid(Drone):
    def __init__(self, 
                 pos, 
                 flightZone, 
                 uri, 
                 boidSep, 
                 boidAlign, 
                 boidCoh):
        Drone.__init__(self, pos, flightZone, uri)

        self.boidSep = boidSep
        self.boidAlign = boidAlign
        self.boidCoh = boidCoh

    def flyTowardsCenter(self):
        raise NotImplementedError

    def avoidOthers(self):
        raise NotImplementedError

    def matchVelocity(self):
        raise NotImplementedError

    def limitSpeed(self):
        raise NotImplementedError

    def keepWithinBounds(self):
        raise NotImplementedError
