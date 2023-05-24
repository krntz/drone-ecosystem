from collections import namedtuple

FlightZone = namedtuple("FlightZone", "x y z floor_offset")

DronePosition = namedtuple("DronePosition", "x y z yaw")
DroneVelocity = namedtuple("DroneVelocity", "vx vy vz")
