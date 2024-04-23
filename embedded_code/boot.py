import math

import gc
import math
import os
from time import sleep
import utime

import usys as sys
from uio import StringIO

from machine import SoftI2C, Pin
import network

from conf_reader import ConfReader
from Si7021 import Si7021
from BH1750 import BH1750
from ICP10111 import ICP10111
from microdot import Microdot, send_file
from NoiseSensor import NoiseSensor
from MeanRadT import MeanRadT
from ModernDevice import ModernDevice_Sensor as ModernDevice

# Run the garbage collector
gc.collect()

# Set the configuration file
conf_file = ConfReader("conf_exemple.json")

ssid, password = conf_file.get_wifi_params()

# Connect to the access point
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

# Wait for the ESP to connect before continuing

print("ESP32 connection to the access point ", ssid)

while not station.isconnected():
    print(".", end=" ")
    sleep(1)
print("Successful connection")
print("ESP32 : Adresse IP, masque, passerelle et DNS", station.ifconfig())
