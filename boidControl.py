from swarmControl import SwarmControl

class DroneControl:
    def __init__(self):
        pass

    def move_drones(self, drones, t):
        positions = {d.get_uri(): d.get_position() for d in drones}
        print(positions)

        self.swarm_move(positions, t, False)
