#SEN0487 -- Capteur de son
from machine import Pin, ADC
import math
import time

class NoiseSensor:
    """
        Classe NoiseSensor
        This class is used to get the noise level from a SEN0487 sensor.
    """
    def __init__(self, ReadPin=32, a=0.0, b=0.0, mean_volt= 1549000.0):
        """
            Parameters:
            a: float, the parameter a
            b: float, the parameter b
            mean_volt: float, the mean voltage
            ReadPin: int, the pin number
        """
        self.a = a
        self.b = b
        self.mean_volt = mean_volt
        self.ReadPin = ReadPin
        print(f"[DEBUG] Noise sensor : {self.__dict__}")

    def AnalogDCRead(self):
        rd = ADC(Pin(self.ReadPin, mode=Pin.IN))
        rd.width(ADC.WIDTH_12BIT) 
        rd.atten(ADC.ATTN_11DB)#Full range: 3.3v
        ReadBit = rd.read()
        ReadVolt = rd.read_uv()
        return ReadVolt, ReadBit
    

    def noiselevel_calib_mod(self):
        """
            Record the digital signal in 1000 points
            return: tuple, the timestamp (list) and the digital signal (list)
        """
        POINTS_NBR = 1000
        mes= [[0,0]] * POINTS_NBR
        ref_time =  time.ticks_us()
        timestamp = [0]*POINTS_NBR

        for i in range(POINTS_NBR):
            timestamp[i] = time.ticks_us() - ref_time
            mes[i] = self.AnalogDCRead()[1] * 3.3 /4095

        #p_to_p_amp = max((m[0] for m in mes)) - min((m[0] for m in mes))
        
        return timestamp, mes
        
    
    def noiselevel(self):
        """
            Measure the noise level according to the calibration law
            return: tuple, the noise level and the peak to peak amplitude
        """
        i = 0
        avg_amp = 0
        TIME_SAMPLING = 250 #ms
        start_time = time.ticks_ms()
        while time.ticks_ms() - start_time < TIME_SAMPLING:
            i += 1
            mes = self.AnalogRead()[0]
            mes = math.fabs(mes - self.mean_volt)
            avg_amp = avg_amp + (mes - avg_amp) / (i+1) #running average
        p_to_p_amp = 2 * avg_amp


        try :
            # Calibration law
            noise_level_calib = 20 * math.log10(self.a * p_to_p_amp + self.b)
        except ValueError:
            print("[Warning] noise level")
            noise_level_calib = 0
        
        return noise_level_calib, p_to_p_amp
