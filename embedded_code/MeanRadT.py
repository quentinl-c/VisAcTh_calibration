#DS18B20
import onewire
from machine import Pin
import ds18x20

class MeanRadT:
    """"
    Classe MeanRadT
    This class is used to get the mean radiation temperature from a DS18B20 sensor.
    """
    def __init__(self, ReadPin=4, c0=0.0, c1=0.0):
        self.ReadPin = Pin(ReadPin)
        self.c0 = c0
        self.c1 = c1
        print(f"[DEBUG] Mean Rad T : {self.__dict__}")

    def MRT(self): 
        ow = onewire.OneWire(self.ReadPin)  # Configuring a one-wire bus on pin 4
        sensor = ds18x20.DS18X20(ow) # Setting up the DS18B20 sensor driver
        roms = sensor.scan() # Scanning for DS18B20 sensors
        sensor.convert_temp() # Making the sensor to start a temperature conversion
        value = sensor.read_temp(roms[0])

        # calibration law:
        value_calibre = value * self.c0 + self.c1
        
        ow.reset()
        return value_calibre, value # Return the calibrated value and the raw value