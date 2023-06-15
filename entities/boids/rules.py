import math

import numpy as np


def fly_towards_center(boid: any, other_boids: list) -> None:
    """
    Rule 1 in the standard boids model

    Boids should steer towards the center of the other boids (if any)
    """

    if other_boids:
        center = np.zeros(3)

        for b in other_boids:
            center += b.position

        center /= len(other_boids)

        boid.velocity += (center - boid.position) * boid.cohesion
        boid.yaw_rate = boid.yaw_rate


def avoid_others(boid: any) -> None:
    """
    Rule 2 in the standard boids model

    Keeps a distance between the boid and other boids to prevent mid-air collisions
    """

    # Boids outside visual range are not close enough to collide

    if boid.detected_boids:
        move = np.zeros(3)

        close_boids = filter(
            lambda b: boid.distance_to_point(
                b.position) < boid.minimum_distance,
            boid.detected_boids
        )

        for b in close_boids:
            move += boid.position - b.position

        boid.velocity += move * boid.separation
        boid.yaw_rate = boid.yaw_rate


def match_velocity(boid: any, other_boids: list) -> None:
    """
    Rule 3 in the standard boids model

    Matches velocity (speed and direction) of other boids (if any)
    """

    if other_boids:
        average_velocity = np.zeros(3)

        for b in other_boids:
            average_velocity += b.velocity

        average_velocity /= len(other_boids)
        boid.velocity += (average_velocity - boid.velocity) * boid.alignment


def limit_velocity(boid: any) -> None:
    # TODO: Should take into account the time per each step to ensure we aren't trying to move too fast

    speed_limit = 0.25

    speed = math.sqrt(np.sum(boid.velocity ** 2))

    if speed > speed_limit:
        boid.velocity = (boid.velocity / speed) * speed_limit
        boid.yaw_rate = boid.yaw_rate


def keep_within_bounds(boid: any) -> None:
    min_x = -boid.flight_zone.x/2
    max_x = boid.flight_zone.x/2

    min_y = -boid.flight_zone.y/2
    max_y = boid.flight_zone.y/2

    min_z = boid.flight_zone.floor_offset
    max_z = boid.flight_zone.z

    buffer = 0.2

    turning_factor = 0.1

    # TODO: Scale velocity so the drone turns faster the further out-of-bounds it is

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
