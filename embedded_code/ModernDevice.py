from machine import Pin, ADC
import math

class ModernDevice_Sensor():
    """"
        Classe ModernDevice
        This class is used to get the wind speed from a ModernDevice sensor.
    """

    def __init__(self, RW=0.0, TW=0.0, a=0.0, b=0.0, n=0.0):
        """
            Parameters:
            RW: float, the resistance of the wire
            TW: float, the temperature of the wire
            a: float, the parameter a
            b: float, the parameter b
            n: float, the parameter n
        """
        self.RW = RW
        self.TW = TW
        self.a = a
        self.b = b
        self.n = n
        print(f"[DEBUG] Modern Device : {self.__dict__}")

    def WindSpeed(self, Tair=24.0):
        """
            Get the wind speed
            Parameters:
            Tair: float, the air temperature
            return: tuple, the wind speed, the RV pin value and the TMP pin value
        """
        
        RVPin = self.ModernDeviceRead(36)
        TMPPin = self.ModernDeviceRead(39)

        # Conversion of the analog value to a voltage (0-3.3V and  12bits resolution)
        U = (RVPin * 3.3) / 4095
        
        # Calibration law : King's law
        windSpeed_ms = ((1/self.b)*((U**2)/(self.RW * (self.TW - Tair))-self.a))**(1/self.n)
        
        if isinstance(windSpeed_ms, complex):
            # If the wind speed is negligible, we consider that the wind speed is 0
            windSpeed_ms = 0
        
        return  windSpeed_ms, RVPin, TMPPin

    def ModernDeviceRead(self, ReadPin):
        rd = ADC(Pin(ReadPin, mode=Pin.IN))
        rd.width(ADC.WIDTH_12BIT)
        rd.atten(rd.ATTN_11DB)  # Full range: 3.3v
        ReadBit = rd.read()
        return ReadBit