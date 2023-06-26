#!/usr/bin/env python3

import argparse
import logging
from threading import Event

import cflib.crtp
import yaml
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.mem import (LighthouseBsCalibration, LighthouseBsGeometry,
                                 LighthouseMemHelper)
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

__author__ = "Amandus Krantz"
__credits__ = ["Bitcraze AB"]
__license__ = "GPL-3"
__maintainer__ = "Amandus Krantz"
__email__ = "amandus.krantz@lucs.lu.se"
__status__ = "Prototype"

logger = logging.getLogger(__name__)


class WriteMem:
    def __init__(self, geo_data, calib_data):
        self._write_event = Event()

        self._geo_data = geo_data
        self._calib_data = calib_data

    def to_drone(self, scf):
        """
        Writes geometry and calibration data to a Synchronous Crazyflie instance.
        """

        helper = LighthouseMemHelper(scf.cf)

        logger.debug(
            f"Writing geometry data to drone with URI {scf.cf.link_uri}")
        helper.write_geos(self._geo_data, self._data_written)
        self._write_event.wait()

        self._write_event.clear()

        logger.debug(
            f"Writing calibration data to drone with URI {scf.cf.link_uri}")
        helper.write_calibs(self._calib_data, self._data_written)
        self._write_event.wait()

    def _data_written(self, success):
        if success:
            print('Data written')
        else:
            print('Write failed')

        self._write_event.set()

    def to_file(self, filename: str):
        """
        Writes geometry and calibration data to a local file.
        """

        geo_dict = {i: geo.as_file_object()
                    for i, geo in self._geo_data.items()}

        calib_dict = {i: calib.as_file_object()
                      for i, calib in self._calib_data.items()}

        file_dict = {"geos": geo_dict, "calibs": calib_dict}

        logger.debug(f"Writing geometry and calibration data to {filename}")
        with open(filename, 'w') as f:
            yaml.dump(file_dict, f)


class ReadMem:
    def __init__(self) -> None:
        self._read_event = Event()
        self._geo_data = {}
        self._calib_data = {}

    @property
    def geo_data(self):
        return self._geo_data

    @property
    def calib_data(self):
        return self._calib_data

    def from_drone(self, scf) -> None:
        """
        Reads geometry and calibration data from a Synchronous Crazyflie instance.
        """

        helper = LighthouseMemHelper(scf.cf)

        helper.read_all_geos(self._geo_read_ready)
        self._read_event.wait()

        self._read_event.clear()

        helper.read_all_calibs(self._calib_read_ready)
        self._read_event.wait()

    def _geo_read_ready(self, geo_data) -> None:
        self._geo_data = geo_data
        self._read_event.set()

    def _calib_read_ready(self, calib_data) -> None:
        self._calib_data = calib_data
        self._read_event.set()

    def from_file(self, filename: str) -> None:
        """
        Reads geometry and calibration data from a local file.
        """

        with open(filename, 'r') as f:
            lighthouseConfig = yaml.safe_load(f)

        lighthouse_calibration = lighthouseConfig["calibs"]
        lighthouse_geometry = lighthouseConfig["geos"]

        for i in range(len(lighthouse_geometry)):
            geo = lighthouse_geometry[i]
            bsGeo = LighthouseBsGeometry()
            bsGeo.origin = geo["origin"]
            bsGeo.rotation_matrix = geo["rotation"]
            bsGeo.valid = True

            self.geo_dict[i] = bsGeo

        for i in range(len(lighthouse_calibration)):
            calib = lighthouse_calibration[i]
            bsCalib = LighthouseBsCalibration()
            bsCalib.uid = calib["uid"]
            bsCalib.valid = True

            for j, sweep in enumerate(calib["sweeps"]):
                bsCalib.sweeps[j].phase = sweep["phase"]
                bsCalib.sweeps[j].tilt = sweep["tilt"]
                bsCalib.sweeps[j].curve = sweep["curve"]
                bsCalib.sweeps[j].gibmag = sweep["gibmag"]
                bsCalib.sweeps[j].gibphase = sweep["gibphase"]
                bsCalib.sweeps[j].ogeemag = sweep["ogeemag"]
                bsCalib.sweeps[j].ogeephase = sweep["ogeephase"]

            self.calib_dict[i] = bsCalib


def main() -> None:
    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser(
        description="Reads and/or writes calibration data from/to Crazyflie drones")

    parser.add_argument('-i', '--input', required=True, dest='input',
                        help='Input to read calibration data from, can be either ' +
                        'a local file or the URI of an already calibrated drone')

    parser.add_argument('-o', '--output', required=True, dest='output',
                        help='Output to write calibration data to, can be either a file or a drone')

    args = parser.parse_args()

    cflib.crtp.init_drivers()

    read_mem = ReadMem()

    input_is_drone = args.input.startswith("radio://")

    if input_is_drone:
        with SyncCrazyflie(args.input, cf=Crazyflie(rw_cache='./cache')) as scf:
            read_mem.from_drone(scf)
    else:
        read_mem.from_file(args.input)

    write_mem = WriteMem(read_mem.geo_data, read_mem.calib_data)

    output_is_drone = args.output.startswith("radio://")

    if output_is_drone:
        with SyncCrazyflie(args.output, cf=Crazyflie(rw_cache='./cache')) as scf:
            write_mem.to_drone(scf)
    else:
        write_mem.to_file(args.output)


if __name__ == "__main__":
    main()
