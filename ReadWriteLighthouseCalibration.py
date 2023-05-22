from cflib.crazyflie.mem import LighthouseBsCalibration
from cflib.crazyflie.mem import LighthouseBsGeometry
from cflib.crazyflie.mem import LighthouseMemHelper
import cflib.crtp

from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie import Crazyflie

from threading import Event

import yaml

class WriteMem:
    def __init__(self, scf, geo_dict, calib_dict):
        self._event = Event()

        helper = LighthouseMemHelper(scf.cf)

        helper.write_geos(geo_dict, self._data_written)
        self._event.wait()

        self._event.clear()

        helper.write_calibs(calib_dict, self._data_written)
        self._event.wait()

    def _data_written(self, success):
        if success:
            print('Data written')
        else:
            print('Write failed')

        self._event.set()

class ReadMem:
    def __init__(self, uri = "radio://0/80/2M/E7E7E7E7E0"):
        self._event = Event()
        self.geo_data = None
        self.calib_data = None

        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            helper = LighthouseMemHelper(scf.cf)

            helper.read_all_geos(self._geo_read_ready)
            self._event.wait()

            self._event.clear()

            helper.read_all_calibs(self._calib_read_ready)
            self._event.wait()

    def _geo_read_ready(self, geo_data):
        self.geo_data = geo_data
        self._event.set()

    def _calib_read_ready(self, calib_data):
        self.calib_data = calib_data
        self._event.set()
    
    def toFile(self, fn):
        geo_dict = {}
        
        for i, geo in self.geo_data.items():
            geo_dict[i] = geo.as_file_object()
        
        calib_dict = {}

        for i, calib in self.calib_data.items():
            calib_dict[i] = calib.as_file_object()
        
        file_dict = {"geos" : geo_dict, "calibs": calib_dict}

        with open(fn, 'w') as f:
            yaml.dump(file_dict, f)

def ReadFromFile(fn):
    with open(fn, 'r') as f:
        lighthouseConfig = yaml.safe_load(f)
        
    lhCalibs = lighthouseConfig["calibs"]
    lhGeos = lighthouseConfig["geos"]

    geo_dict = {}
    for i in range(len(lhGeos)):
        geo = lhGeos[i]
        bsGeo = LighthouseBsGeometry()
        bsGeo.origin = geo["origin"]
        bsGeo.rotation_matrix = geo["rotation"]
        bsGeo.valid = True

        geo_dict[i] = bsGeo

    calib_dict = {}

    for i in range(len(lhCalibs)):
        calib = lhCalibs[i]
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
        
        calib_dict[i] = bsCalib
    
    return geo_dict, calib_dict


if __name__ == "__main__":
    # TODO: Sort out parameters etc. to allow choosing to read and/or write to/from a drone or file

    cflib.crtp.init_drivers()
    mem = ReadMem()
    mem.toFile("config.yaml")
