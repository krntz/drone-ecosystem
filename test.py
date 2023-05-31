from swarmControl import SwarmControl

import logging, time

from utils import FlightZone, DronePosition
if __name__ == '__main__':
    DEBUG = True

    uris = {
        'radio://0/80/2M/E7E7E7E7E0',
        #'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        # 'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        # 'radio://0/80/2M/E7E7E7E7E7',
        # 'radio://0/80/2M/E7E7E7E7E8',
    }

    logging.basicConfig(level=logging.INFO)
    flight_zone = FlightZone(2.0, 3.0, 1.25, 0.30)
    s = SwarmControl(uris,
                     flight_zone,
                     'radio://0/80/2M/E7E7E7E7E0',
                     DEBUG=DEBUG)

    try:
        s.swarm_take_off()
        time.sleep(2)

        time_step = 1

        positions = {'radio://0/80/2M/E7E7E7E7E2':DronePosition(0, 0, 0.5, 0), 
                     'radio://0/80/2M/E7E7E7E7E0':DronePosition(0.5, 0.5, 0.5, 0)}

        s.swarm_move(positions, 1)
        time.sleep(1)

        new_z = [1.30, 1.15, 1, 0.85, 0.70]

        for z in new_z:
            pos = {'radio://0/80/2M/E7E7E7E7E2':DronePosition(0, 0, 0.5, 0),
                   'radio://0/80/2M/E7E7E7E7E0':DronePosition(0, 0, z, 0)}

            s.swarm_move(pos, 1)
            time.sleep(4)

        s.swarm_move(positions, 1)
        time.sleep(1)

        s.swarm_land()
    except KeyboardInterrupt:
        print("Exiting")
        s.swarm_land(emergency_land=True)
    except Exception as e:
        s.swarm_land(emergency_land=True)
        raise e
    finally:
        s.swarm.close_links()
        del s
