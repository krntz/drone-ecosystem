from swarmControl import SwarmControl
from droneControl import DroneControl

if __name__ == '__main__':
    DEBUG = True

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

    logging.basicConfig(level=logging.ERROR)
    flight_zone = FlightZone(2.0, 3.0, 1.25, 0.30)
    s = SwarmControl(uris,
                     flight_zone,
                     'radio://0/80/2M/E7E7E7E7E0',
                     DEBUG=DEBUG)

    try:
        time_step = 0.75

        boid_separation = 0.05
        boid_alignment = 0.05
        boid_cohesion = 0.005

        drones = []

        for uri in uris:
            drones.append(
                Boid(flight_zone,
                     uri,
                     DEBUG,
                     boid_separation,
                     boid_alignment,
                     boid_cohesion
                     )
            )

        for d in drones:
            d.random_init()

        s.swarm_take_off()
        time.sleep(2)
        s.distribute_swarm(drones)
        time.sleep(2)

        flying = True

        while flying:
            new_positions = []

            for d in drones:
                d.set_new_position(s.get_positions())

            s.move_drones(drones, time_step)

            time.sleep(time_step)

        s.swarm_land()
    except KeyboardInterrupt:
        print("Exiting")
        s.swarm_land()
    except Exception as e:
        s.swarm_land()
        raise e
    finally:
        s.swarm.close_links()
        del s
