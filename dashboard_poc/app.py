import time
from flask import Flask
import requests
from pythermalcomfort.models import pmv
from pythermalcomfort.utilities import v_relative, clo_dynamic
from threading import Timer
import atexit
import math 

# IP address of the sensor node
SENSOR_URL = 'http://[IP-ADDRESS]:5000/api/measures'
# Number of data points to store in memory
MAX_LEN = 1200
# Frequency of data retrieval in seconds
WAIT_TIME_SECONDS = 1

def pmv_thcomfort(tdb, rh, v, tr):
    met = 1.1 #metabolic rate
    clo = 0.65 #clothing insulation
    clo_d = clo_dynamic(clo=clo, met=met)# calculate dynamic clothing
    vr = v_relative(v=v, met=met)# calculate relative air speed
    results_pmv = pmv(tdb=tdb, tr=tr, vr=vr, rh=rh, met=met, clo=clo_d, limit_inputs=False)
    return results_pmv

feeds = list()
next_exec = Timer(0,lambda x: None,())   
 
def interrupt():
    global next_exec
    next_exec.cancel()

def retrieve_data():
    global feeds
    global next_exec

    try:
        data = dict()

        r = requests.get(SENSOR_URL)
        r_json = r.json()     
        data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        data['hum'] = r_json['hum']
        data['tempSI7021'] = r_json['tempSI7021']
        data["windSpeed"] = r_json['windSpeed']
        data["pres"] = r_json['pres']
        data["noiseCalib"] = r_json['noise_calib']
        data["lum"] = r_json['lum']
        data["meanRadTempCalib"] = r_json['meanRadTemp_calib']
        
        tdb = float(data['tempSI7021'])
        rh = float(data['hum'])
        v = float(data["windSpeed"])
        tr = float(r_json['trFor'])
        pmv_score = pmv_thcomfort(tdb, rh, v, tr)
        if not math.isnan(pmv_score):
            data['pmv'] = pmv_score

        feeds.append(data)
        if len(feeds) > MAX_LEN:
            feeds.pop(0)

    except Exception as e:
        print(f"[ERROR] Error occured : {e}")
    finally:
        next_exec = Timer(WAIT_TIME_SECONDS, retrieve_data)
        next_exec.start()
            

atexit.register(interrupt)

retrieve_data()

app = Flask(__name__)



@app.route("/")
def get_all_data():
    return feeds
