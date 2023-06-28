import numpy as np


def fly_towards_center(boid, other_boids, delta_time):
    """
    Rule 1 in the standard boids model

    Boids should fly towards the center of their swarm
    """

    cohesion = boid.boid_cohesion * delta_time

    center = np.zeros(3)
    num_neighbours = 0

    for boid in other_boids:
        boid_pos = boid.position

        if boid.distance_to_boid(boid_pos) < boid.visual_range:
            center += boid_pos
            num_neighbours += 1

    if num_neighbours > 0:
        center /= num_neighbours

        boid.velocity += (center - boid.position) * cohesion
        boid.yaw_rate = boid.yaw_rate


def avoid_others(boid, other_boids, delta_time):
    """
    Rule 2 in the standard boids model

    Keeps a distance between the boid and other boids to prevent mid-air collisions
    """

    separation = boid.boid_separation * delta_time
    move = np.zeros(3)

    for boid in other_boids:
        if boid.distance_to_boid(boid.position) < boid.minimum_distance:
            move += boid.position - boid.position

    boid.velocity += move * separation
    boid.yaw_rate = boid.yaw_rate


def match_velocity(boid, other_boids, delta_time):
    """
    Rule 3 in the standard boids model

    Matches velocity (speed and direction) of the swarm
    """

    alignment = boid.boid_alignment * delta_time

    average_velocity = np.zeros(3)
    num_neighbours = 0

    for boid in other_boids:
        boid_pos = boid.position

        if boid.distance_to_boid(boid_pos) < boid.visual_range:
            average_velocity += boid.velocity

            num_neighbours += 1

    if num_neighbours > 1:
        average_velocity /= num_neighbours
        boid.velocity += (average_velocity - boid.velocity) * alignment


def limit_velocity(boid) -> None:
    """
    Clamps the speed of the boid to be within its min and max speed.
    """

    speed = np.linalg.norm(boid.velocity)

    heading = boid.velocity / speed

    speed = np.clip(speed, boid.min_speed, boid.max_speed)

    boid.velocity = heading * speed


def keep_within_bounds(boid, delta_time: float) -> None:
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
