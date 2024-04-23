import json
import os

class ConfReader:
    """Class to read the configuration file of the ESP32"""
    
    WIFI_SECTION = "WIFI"
    SSID = "SSID"
    PW = "PASSWORD"
    
    PARAMS_SECTION = "PARAMETERS"
    NOISE_SENSOR = "NOISE"
    NOISE_SENSOR_a = "a"
    NOISE_SENSOR_b = "b"
    NOISE_SENSOR_meanv = "mean_volt"

    MRT_SENSOR = "MRT"
    MRT_SENSOR_a = "a"
    MRT_SENSOR_b = "b"

    WSRC_SENSOR = "WSRC"
    WSRC_SENSOR_TW = "TW"
    WSRC_SENSOR_RW = "RW"
    WSRC_SENSOR_a = "a"
    WSRC_SENSOR_b = "b"
    WSRC_SENSOR_n= "n"
    
    def __init__(self, conf_file):
        """"
            Constructor of the class ConfReader
            conf_file: str, the name of the configuration file"
        """
        if conf_file not in os.listdir():
            raise FileNotFoundError("File not found")
        self.conf_file = conf_file
    
    def _read_file(self):
        """"
            Read the configuration file
            return: dict, the content of the configuration file
        """
        with open(self.conf_file, "r") as f:
            return json.load(f)
    
    def get_wifi_params(self):
        """"
            Get the wifi parameters
            return: tuple, the SSID and the password of the wifi
        """
        conf = self._read_file()
        return (conf[self.WIFI_SECTION][self.SSID],
               conf[self.WIFI_SECTION][self.PW])

    def get_noise_sensor_params(self):
        """"
            Get the noise sensor parameters
            return: tuple, the parameters of the noise sensor : a, b and mean_volt
        """
        conf = self._read_file()
        return (conf[self.PARAMS_SECTION][self.NOISE_SENSOR][self.NOISE_SENSOR_a],
               conf[self.PARAMS_SECTION][self.NOISE_SENSOR][self.NOISE_SENSOR_b],
               conf[self.PARAMS_SECTION][self.NOISE_SENSOR][self.NOISE_SENSOR_meanv])

    def get_mrt_sensor_params(self):
        """"
            Get the mean radiation temperature sensor parameters
            return: tuple, the parameters of the MRT sensor : a and b
        """
        conf = self._read_file()
        return (conf[self.PARAMS_SECTION][self.MRT_SENSOR][self.MRT_SENSOR_a],
               conf[self.PARAMS_SECTION][self.MRT_SENSOR][self.MRT_SENSOR_b])

    def get_wsrc_sensor_params(self):
        """"
            Get the water surface sensor parameters
            return: tuple, the parameters of the WSRC sensor : RW, TW, a, b and n
        """
        conf = self._read_file()
        return (conf[self.PARAMS_SECTION][self.WSRC_SENSOR][self.WSRC_SENSOR_RW],
               conf[self.PARAMS_SECTION][self.WSRC_SENSOR][self.WSRC_SENSOR_TW],
               conf[self.PARAMS_SECTION][self.WSRC_SENSOR][self.WSRC_SENSOR_a],
               conf[self.PARAMS_SECTION][self.WSRC_SENSOR][self.WSRC_SENSOR_b],
               conf[self.PARAMS_SECTION][self.WSRC_SENSOR][self.WSRC_SENSOR_n])             