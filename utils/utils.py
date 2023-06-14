#!/usr/bin/env python3

from collections import namedtuple

__author__ = "Amandus Krantz"
__credits__ = ["Rachael Garrett", "Joseph La Delfa"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"

FlightZone = namedtuple("FlightZone", "x y z floor_offset")

DronePosition = namedtuple("DronePosition", "x y z yaw")
DroneVelocity = namedtuple("DroneVelocity", "vx vy vz yawrate")
