# Visual Acoustic and Thermal sensor (VisAcTh) calibration
> Source code to calibrate the homemade VisAcTh (Visual Acoustic Thermal) sensor


## 📁 fitting
The fitting folder contains the Jupyter notebooks used for the calibration and evaluation of our sensor in real conditions. The data for the calibration and the ones captured during the testing experiments are provided in the data folder.

### Software environment & dependencies 
The code has to be run in a Linux environment or WSL.
Required Python packages are listed in the `requirements.txt` file. In addition, you need to install [xmgrace](https://plasma-gate.weizmann.ac.il/Grace/), which can be used here as an alternative to limit for the curve fitting.

## 📁 embeded_code
This folder contains the Python code executed by MicroPython (V1.19.1) on our ESP32 board.

⚠️ This code is not intended to be run on production or sensitive applications.
