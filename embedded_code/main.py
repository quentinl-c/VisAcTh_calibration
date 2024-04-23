"""
This script contains the main code for a webapp server that interacts with various sensors.
"""

# Webapp server
app = Microdot()

i2c = None
TRH_sensor = None
Lux_sensor = None
pressure_sensor = None
m = None
sound_sensor = None
MRT_sensor = None
Airwind_sensor = None

# i2C sensors init bloc
try:
    i2c = SoftI2C(Pin(22),Pin(21), freq=400000)

    # Configuration des capteurs i2C
    TRH_sensor = Si7021(i2c)
    Lux_sensor = BH1750(i2c)
    pressure_sensor = ICP10111(i2c)
except Exception as e:
    print(f"[ERROR] i2C : {e}")

# sound sensor init bloc
try:
    a, b, mean_volt = conf_file.get_noise_sensor_params()
    sound_sensor = NoiseSensor(a=a, b=b, mean_volt=mean_volt)
except Exception as e:
    print(f"[ERROR] Noise sensor : {e}")

# MRT sensor init bloc
try:
    a, b = conf_file.get_mrt_sensor_params()
    MRT_sensor = MeanRadT(c0=a, c1=b)
except Exception as e:
    print(f"[ERROR] MRT : {e}")

# ModernDevice sensor init bloc
try:
    RW, TW,  a, b, n = conf_file.get_wsrc_sensor_params()
    Airwind_sensor = ModernDevice(RW=RW, TW=TW, a=a, b=b, n=n)
except Exception as e:
    print(e)

"""
Route: /upload/<filename>
Method: POST
Description: Upload a file
"""
@app.post('/upload/<filename>')
def req_upload(request,filename):
    print(request)

"""
Route: /chart/mrt
Method: GET
Description: Render the MRT chart
"""
@app.route('/chart/mrt')
def render_chart(request):
    return send_file('mrt.html')

"""
Route: /chart/noise
Method: GET
Description: Render the noise chart
"""
@app.route('/chart/noise')
def render_chart(request):
    return send_file('noise.html')


"""
Route: /api/reboot
Method: GET
Description: Reboot the esp32 board
"""
@app.route('/api/reboot')
def req_reboot(request):
    request.app.shutdown(reboot=True)
    return {'msg': 'The server is rebooting...'}, 200

"""
Route: /calibration/noise
Method: GET
Description: Render a page to calibrate the noise sensor and linkend to a samples file
"""
@app.route('/calibration/noise')
def req_noise_data(request):
    dataVal = dict()
    timestamp, mes = sound_sensor.noiselevel_calib_mod() #niveau sonore en dB
    filename = str(utime.time()) + '.csv'
    with open(filename, 'w') as f:
        f.write("timestamp,uV,digital\n")
        for t, m in zip(timestamp, mes):
            f.write(f"{t},{m[0]},{m[1]}\n")
    content = f"""<html>
                    <head>
                        <title>Noise sensor calibration</title>
                    </head>
                    <body>
                        <h3>Noise sensor calibration</h3>
                        <a href="/retrieve/{filename}">records</a>
                    </body>
                </html>"""
    return content, 200, {'Content-Type': 'text/html'}

"""
Route: /retrieve/<filename>
Method: GET
Description: Retrieve a file stored on the esp32 board
"""
@app.route('/retrieve/<filename>')
def req_retrieve_file(request, filename):
    if filename not in os.listdir():
        return 'Not found', 404
    return send_file(filename, content_type=' text/csv')

"""
Route: /api/measures
Method: GET
Description: Retrieve the measures from the sensors (JSON format)
"""
@app.route('/api/measures')
def req_retrieve_data(request):
    dataValues = dict()
    
    if TRH_sensor is not None:
        TRH_sensor.reset() #Reset du SI7021
        dataValues['tempSI7021'] = TRH_sensor.temperature  #Temperature en °C du capteur SI7021
        dataValues['hum'] = TRH_sensor.relative_humidity  #Humidite relative en % du capteur SI7021 
    
    if Lux_sensor is not None:
        Lux_sensor.reset()
        dataValues['lum'] = Lux_sensor.luminance(BH1750.ONCE_HIRES_1) # luminosite en lux
    
    if pressure_sensor is not None:
        pressure_sensor.reset()
        m = pressure_sensor.get_temperature_pressure() 
        dataValues['tempICP'] = m[0] #Temperature en °C du capteur de presion ICP10111
        dataValues['pres'] = m[1] #Pression en Pa du capteur de presion ICP10111
    
    if sound_sensor is not None:
        dataValues['noiseCalib'], dataValues['noise'] = sound_sensor.noiselevel() #niveau sonore en dB
    
    if MRT_sensor is not None:
        dataValues['meanRadTempCalib'], dataValues['meanRadTempPin'] = MRT_sensor.MRT() #Temperature moyenne rayonnee en °C

    if Airwind_sensor is not None:
        Tair = dataValues['tempSI7021'] if 'tempSI7021' in dataValues else 24.0
        dataValues['windSpeed'], dataValues['RVPin'], dataValues['TMPPin']  = Airwind_sensor.WindSpeed(Tair=Tair) #Vitesse de l'air en m/s
    
   
    if all(k in dataValues for k in ['windSpeed', 'meanRadTempCalib', 'tempSI7021']):
        epsilonG = 0.95
        D = 4E-2
        Tglobe = dataValues['meanRadTempCalib']
        Tair = dataValues['tempSI7021']
        va = dataValues['windSpeed']
        
        dataValues['trNat'] = ((Tglobe + 273.15)**4 + (0.25E8 / epsilonG) * (math.fabs(Tglobe - Tair) / D)**(1/4) * (Tglobe - Tair))**(1/4) - 273.15
        dataValues['trFor'] = ((Tglobe + 273.15)**4 + (1.1E8 * (va**0.6) / epsilonG * (D**0.4)) * (Tglobe - Tair)) ** (1/4) - 273.15
    
    return dataValues, 200, {'Access-Control-Allow-Origin': '*'}


"""
Handler for runtime errors
"""
@app.errorhandler(Exception)
def runtime_error(request, exception):
    """
    Returns the staktrace when an exception is raised
    """
    s = StringIO()
    sys.print_exception(exception, s)
    error = s.getvalue()
    return {'error': error}, 500

app.run(debug=True)
