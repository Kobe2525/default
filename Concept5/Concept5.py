from time import sleep, localtime, strftime, gmtime
import pymysql
import board
import adafruit_bmp280
from flask import Flask, render_template, request, url_for
import _thread
from gpiozero import PWMLED
from simple_pid import PID

# Initialize the heating element on GPIO pin 5
Heat = PWMLED(5)

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
bmp280.sea_level_pressure = 1013.25

# Database connection
conn = pymysql.connect(host='127.0.0.1', unix_socket='/var/run/mysqld/mysqld.sock', user='Smets', passwd='Thomas', db='Temp')
cur = conn.cursor()

# Initial values
WantTemp = 20  # Desired temperature
ActTemp = 0     # Actual temperature

# PID controller setup
pid = PID(1.0, 0.5, 0.01, setpoint=WantTemp)
pid.sample_time = 1  # Update every second
pid.output_limits = (0, 1)  # Limits output to PWM range (0 to 1)
pid.auto_mode = True

def read_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", 'r') as file:
            return int(file.read().strip()) / 1000.0
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None

def Read():
    return bmp280.temperature

def HeatControl():
    global WantTemp, ActTemp
    ActTemp = Read()
    pid.setpoint = WantTemp  # Update setpoint dynamically
    control_output = pid(ActTemp)  # Get PID output
    Heat.value = control_output  # Apply output to heating element
    print(f"Setpoint: {WantTemp}, Actual: {ActTemp}, Output: {control_output}")

def main():
    while True:
        cpu_temp = read_cpu_temperature()
        HeatControl()
        cur.execute("INSERT INTO CPUTemp(time, Temp, TempBMP, TempWant, y) VALUES (%s, %s, %s, %s, %s)",
                    (strftime("%Y-%m-%d %H:%M:%S", gmtime()), cpu_temp, ActTemp, WantTemp, Heat.value * 100))
        conn.commit()
        sleep(1)

app = Flask(__name__, static_url_path='/style.css', static_folder='www', template_folder='www')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/TempSlider', methods=["POST"])
def TempSlider():
    global WantTemp
    WantTemp = int(request.form["getal"])
    return str(WantTemp)

@app.route('/dataoutW')
def dataoutW():
    return str(round(WantTemp, 2))

@app.route('/dataoutX')
def dataoutX():
    return str(round(ActTemp, 2))

@app.route('/dataoutY')
def dataoutY():
    return "aan" if Heat.value > 0 else "uit"

@app.route('/dataoutYP')
def dataoutYP():
    return '<img src="/style.css/freezer.png" class="image" />' if Heat.value > 0 else ""

@app.route('/dataoutWX')
def dataoutWX():
    return str(round(WantTemp - ActTemp, 2))

if __name__ == '__main__':
    _thread.start_new_thread(main, ())
    app.run(debug=True, host='0.0.0.0', port=5050, use_reloader=False)
