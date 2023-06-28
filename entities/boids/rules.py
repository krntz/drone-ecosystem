import numpy as np


def fly_towards_center(boid: any, other_boids: list, delta_time: float) -> None:
    """
    Rule 1 in the standard boids model

    Boids should steer towards the center of the other boids (if any)
    """

    cohesion = boid.cohesion * delta_time

    if other_boids:
        center = np.zeros(3)

        for b in other_boids:
            center += b.position

        center /= len(other_boids)

        boid.velocity += (center - boid.position) * cohesion
        boid.yaw_rate = boid.yaw_rate


def avoid_others(boid: any, delta_time: float) -> None:
    """
    Rule 2 in the standard boids model

    Keeps a distance between the boid and other boids to prevent mid-air collisions
    """

    # Boids outside visual range are not close enough to collide

    if boid.detected_boids:
        separation = boid.separation * delta_time
        move = np.zeros(3)

        close_boids = filter(
            lambda b: boid.distance_to_point(
                b.position) < boid.minimum_distance,
            boid.detected_boids
        )

        for b in close_boids:
            move += boid.position - b.position

        boid.velocity += move * separation
        boid.yaw_rate = boid.yaw_rate


def match_velocity(boid: any, other_boids: list, delta_time: float) -> None:
    """
    Rule 3 in the standard boids model

    Matches velocity (speed and direction) of other boids (if any)
    """

    if other_boids:
        alignment = boid.alignment * delta_time
        average_velocity = np.zeros(3)

        for b in other_boids:
            average_velocity += b.velocity

        average_velocity /= len(other_boids)
        boid.velocity += (average_velocity - boid.velocity) * alignment


def limit_velocity(boid: any) -> None:
    """
    Clamps the speed of the boid to be within its min and max speed.
    """

    speed = np.linalg.norm(boid.velocity)

    heading = boid.velocity / speed

    speed = np.clip(speed, boid.min_speed, boid.max_speed)

    boid.velocity = heading * speed


def keep_within_bounds(boid: any, delta_time: float) -> None:
    min_x = -boid.flight_zone.x/2
    max_x = boid.flight_zone.x/2

    min_y = -boid.flight_zone.y/2
    max_y = boid.flight_zone.y/2

    min_z = boid.flight_zone.floor_offset
    max_z = boid.flight_zone.z

    buffer = 0.2

    turning_factor = 0.1 * delta_time

    if boid.position[0] > (max_x - buffer):
        boid.velocity[0] -= turning_factor
    elif boid.position[0] < (min_x + buffer):
        boid.velocity[0] += turning_factor

    if boid.position[1] > (max_y - buffer):
        boid.velocity[1] -= turning_factor
    elif boid.position[1] < (min_y + buffer):
        boid.velocity[1] += turning_factor

    if boid.position[2] > ((max_z + boid.flight_zone.floor_offset) - buffer):
        boid.velocity[2] -= turning_factor
    elif boid.position[2] < ((min_z + boid.flight_zone.floor_offset) + buffer):
        boid.velocity[2] += turning_factor


def move_towards_point(boid: any, point: any) -> None:
    raise NotImplementedError


def avoid_hovering_above(boid: any) -> None:
    raise NotImplementedError
