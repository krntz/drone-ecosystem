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


class LighthouseDataHelper:
    def __init__(self):
        self._write_event = Event()
        self._read_event = Event()

        self._geometry_data = None
        self._calibration_data = None

    def _geo_read_callback(self, geo_data: dict) -> None:
        self._geometry_data = geo_data
        self._read_event.set()

    def _calib_read_callback(self, calib_data: dict) -> None:
        self._calibration_data = calib_data
        self._read_event.set()

    def _data_written_callback(self, success: bool) -> None:
        if not success:
            raise RuntimeError("Failed to write data!")

        self._write_event.set()

    def read_from_drone(self, scf: SyncCrazyflie) -> None:
        """
        Reads geometry and calibration data from a Synchronous Crazyflie instance.
        """

        helper = LighthouseMemHelper(scf.cf)

        logger.info(
            f"Reading geometry data from drone with URI {scf.cf.link_uri}")
        helper.read_all_geos(self._geo_read_callback)
        self._read_event.wait()

        self._read_event.clear()

        logger.info(
            f"Reading calibration data from drone with URI {scf.cf.link_uri}")
        helper.read_all_calibs(self._calib_read_callback)
        self._read_event.wait()

        logger.info("Data read")
        self._read_event.clear()

    def read_from_file(self, filename: str) -> None:
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

    def write_to_drone(self, scf: SyncCrazyflie):
        """
        Writes geometry and calibration data to a Synchronous Crazyflie instance.
        """

        if not self._geometry_data:
            raise RuntimeError(
                "No geometry data to write, need to read from drone/file first!")

        if not self._calibration_data:
            raise RuntimeError(
                "No calibration data to write, need to read from drone/file first!")

        helper = LighthouseMemHelper(scf.cf)

        logger.info(
            f"Writing geometry data to drone with URI {scf.cf.link_uri}")
        helper.write_geos(self._geometry_data, self._data_written_callback)
        self._write_event.wait()

        self._write_event.clear()

        logger.info(
            f"Writing calibration data to drone with URI {scf.cf.link_uri}")
        helper.write_calibs(self._calibration_data,
                            self._data_written_callback)
        self._write_event.wait()

        logger.info("Data written")
        self._write_event.clear()

    def write_to_file(self, filename: str):
        """
        Writes geometry and calibration data to a local file.
        """

        if not self._geometry_data:
            raise RuntimeError(
                "No geometry data to write, need to read from drone/file first!")

        if not self._calibration_data:
            raise RuntimeError(
                "No calibration data to write, need to read from drone/file first!")

        geo_dict = {lighthouse_num: geo.as_file_object()
                    for lighthouse_num, geo in self._geometry_data.items()}

        calib_dict = {lighthouse_num: calib.as_file_object()
                      for lighthouse_num, calib in self._calibration_data.items()}

        file_dict = {"geos": geo_dict, "calibs": calib_dict}

        logger.info(f"Writing geometry and calibration data to {filename}")
        with open(filename, 'w') as f:
            yaml.dump(file_dict, f)

        logger.info("Data written")


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Reads and/or writes calibration data from/to Crazyflie drones")

    parser.add_argument('-i', '--input', required=True, dest='input', type=str,
                        help='Input to read calibration data from, can be either ' +
                        'a local file or the URI of an already calibrated drone')

    parser.add_argument('-o', '--output', required=True, dest='output', type=str,
                        help='Output to write calibration data to, can be either a file or a drone')

    args = parser.parse_args()

    cflib.crtp.init_drivers()

    lighthouse_data = LighthouseDataHelper()

    input_is_drone = args.input.startswith("radio://")

    if input_is_drone:
        with SyncCrazyflie(args.input, cf=Crazyflie(rw_cache='./cache')) as scf:
            lighthouse_data.read_from_drone(scf)
    else:
        read_mem.from_file(args.input)

    output_is_drone = args.output.startswith("radio://")

    if output_is_drone:
        with SyncCrazyflie(args.output, cf=Crazyflie(rw_cache='./cache')) as scf:
            lighthouse_data.write_to_drone(scf)
    else:
        lighthouse_data.write_to_file(args.output)


if __name__ == "__main__":
    main()
