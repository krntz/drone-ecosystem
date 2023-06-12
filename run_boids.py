#!/usr/bin/env python3

import logging

from controllers.crazyflieController import CrazyflieController
from entities.entityManager import EntityManager
from entities.boids.standardBoid import StandardBoid
from utils.utils import FlightZone

__author__ = "Amandus Krantz"
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    uris = {
        'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        # 'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        # 'radio://0/80/2M/E7E7E7E7E7',
        # 'radio://0/80/2M/E7E7E7E7E8',
    }

    logging.basicConfig(level=logging.INFO)
    flight_zone = FlightZone(2.0, 3.0, 1.25, 0.30)

    boid_separation = 1
    boid_alignment = 0.1
    boid_cohesion = 0.1
    visual_range = 1

    update_rate = 1.0/60

    drones = [
        StandardBoid(uri,
                     flight_zone,
                     boid_separation,
                     boid_alignment,
                     boid_cohesion,
                     visual_range)

        for uri in uris]

    with CrazyflieController(uris, flight_zone, 'radio://0/80/2M/E7E7E7E7E0') as swarmController:
        entityManager = EntityManager(
            update_rate, swarmController, flight_zone, drones)

        entityManager.boid_loop()
