# Visual Acoustic and Thermal sensor (VisAcTh) calibration
> [!NOTE]
> Source code to calibrate the homemade VisAcTh (Visual Acoustic Thermal) sensor


## 📁 fitting
The `fitting` folder contains the Jupyter notebooks used for the calibration and evaluation of our sensor in real conditions. The data for the calibration and the ones captured during the testing experiments are provided in the data folder.

### Software environment & dependencies 
The code has to be run in a Linux environment or WSL.
Required Python packages are listed in the `requirements.txt` file. In addition, you need to install [xmgrace](https://plasma-gate.weizmann.ac.il/Grace/), which can be used here as an alternative to lmfit for the curve fitting.

## 📁 embedded_code
This folder contains the Python code executed by MicroPython (V1.19.1) on the ESP32 board.

⚠️ This code is not intended to be run on production or sensitive applications.

## 🗒️ Datasheets and technical references

Datasheets of the following sensors are available in the `datasheets` folder:
* [ICP-10111 temperature & pressure sensor](./datasheets/datasheet_ICP10111_temperature_pressure_sensor.pdf)
* [MEMS microphone](./datasheets/datasheet_MEMS_microphone.pdf)
* [BH1750FVI ambiant light sensor](./datasheets/datasheets_BH1750FVI_ambiant_light_sensor.pdf)
* [Si7021-A20 humidity & temperature sensor](./datasheets/datasheet_Si7021-A20_humidity_temperature_sensor.pdf)
* [DS18B20 temperature sensor](./datasheets/datasheet_DS18B20_temperature_sensor.pdf)

To complement the technical information provided in the previous datasheets, please find below some technical references:
* [BH1750 light intensity sensor (wiki)](https://wiki.dfrobot.com/Light_Sensor__SKU_SEN0097_#target_4)
* [ICP-10111 barometric pressure temperature sensor (wiki)](https://wiki.dfrobot.com/SKU_SEN0516_Fermion_ICP_10111_Pressure_Sensor)
* [MEMS microphone (wiki)](https://wiki.dfrobot.com/Fermion_MEMS_Microphone_Sensor_SKU_SEN0487)
* [Si7021 humidity and temperature sensor (links to schematic and code in document section)](https://www.sparkfun.com/products/13763)
* [Wind Sensor Rev. C (technical and commercial page)](https://moderndevice.com/products/wind-sensor)
* [uPesy ESP32 Wroom Low Power DevKit v1.2 (wiki)](https://www.upesy.fr/blogs/tutorials/upesy-esp32-wroom-low-power-devkit-board-documentation-version-latest?shpxid=381d4974-6bc8-4380-b842-925b6b18ada5)