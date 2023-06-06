import logging

from boids.boid import Boid
from boidManager import BoidManager
from crazyflieSwarmControl import CrazyflieSwarmControl
from utils import FlightZone

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    uris = {
        'radio://0/80/2M/E7E7E7E7E0',
        #'radio://0/80/2M/E7E7E7E7E1',
        #'radio://0/80/2M/E7E7E7E7E2',
        #'radio://0/80/2M/E7E7E7E7E3',
        #'radio://0/80/2M/E7E7E7E7E4',
        #'radio://0/80/2M/E7E7E7E7E5',
        #'radio://0/80/2M/E7E7E7E7E6',
        #'radio://0/80/2M/E7E7E7E7E7',
        #'radio://0/80/2M/E7E7E7E7E8',
    }

    logging.basicConfig(level=logging.DEBUG)
    flight_zone = FlightZone(2.0, 3.0, 1.25, 0.30)

    boid_separation = 1
    boid_alignment = 0.1
    boid_cohesion = 0.1
    visual_range = 1

    drones = [
        Boid(flight_zone,
             uri,
             boid_separation,
             boid_alignment,
             boid_cohesion,
             visual_range)

        for uri in uris]

    time_step = 1

    try:
        swarmControl = CrazyflieSwarmControl(uris,
                                             flight_zone,
                                             'radio://0/80/2M/E7E7E7E7E0')

        boidManager = BoidManager(swarmControl, flight_zone, drones)

        boidManager.boid_loop(time_step)
    except KeyboardInterrupt:
        logger.info("Exiting")
    except Exception:
        swarmControl.swarm_land(True)
        raise
    finally:
        swarmControl.swarm_land(True)
        del swarmControl
        del boidManager
