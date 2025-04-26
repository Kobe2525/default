from gpiozero import AngularServo
from time import sleep, localtime, strftime, gmtime
import board
import adafruit_bh1750
from simple_pid import PID
from flask import Flask, render_template, request, url_for
import _thread
import pymysql

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = adafruit_bh1750.BH1750(i2c)

servo = AngularServo(26, min_angle=0, max_angle=180)
servo.angle = 75

WantLux = 5
ActLux = 5
LdrMax = 5
LdrMin = 0

Kp = 0.48
Ki = 0.0064
Kd = 0.06
pid = PID(Kp, Ki, Kd, setpoint=WantLux)
pid.sample_time = 1  # Update every second
pid.output_limits = (0, 75)  # Limits output to PWM range (0 to 1)
pid.auto_mode = False
PidState = 0

# Database connection
conn = pymysql.connect(host='127.0.0.1', unix_socket='/var/run/mysqld/mysqld.sock', user='Smets', passwd='Thomas', db='PaasExamen')
cur = conn.cursor()

Acces = 1

def CalibrateMin():
	global LdrMin,Acces
	servo.angle = 75
	Acces = 0
	sleep(1)
	LdrMin = sensor.lux
	print("LdrMin: ",LdrMin," Lux")
	servo.angle = 75
	Acces = 1

def CalibratePos():
	global LdrMax,Acces
	servo.angle = 0
	Acces = 0
	sleep(1)
	LdrMax = sensor.lux
	print("LdrMax: ",LdrMax," Lux")
	servo.angle = 75
	Acces = 1


def LdrRead():
	global ActLux,Acces
	while True:
		if Acces == 1:
			HelpA = sensor.lux
			if HelpA == 0:
				HelpA = 0.00001

			ActLux = (100/(LdrMax-LdrMin)*HelpA)
			# print("HelpA: ",HelpA)
			print("ActLux",ActLux)
		else: 
			pass


def main():
	global ActLux,WantLux,Angle,Kp,Ki,Kd
	try:
		_thread.start_new_thread(LdrRead,())
		while True:
			if PidState == 1:
				print("PID on")
				pid.setpoint = WantLux  # Update setpoint dynamically
				control_output = pid(ActLux)  # Get PID output
				Angle = control_output
				servo.angle = Angle
			else :
				print("PID off")
				Angle = 15
			cur.execute("INSERT INTO Lux(time, ActLux, WantLux, y, Kp, Ki, Kd) VALUES (%s, %s, %s, %s, %s, %s, %s)",(strftime("%Y-%m-%d %H:%M:%S", gmtime()), ActLux, WantLux, Angle , Kp, Ki, Kd))
			conn.commit()
			pass
	except:
		servo.detach()
app = Flask(__name__, static_folder='www', template_folder='www')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/CalPButton', methods=["POST"])
def CalPButton():
	CalibratePos()
	return str("Done") 

@app.route('/PIDOnButton', methods=["POST"])
def PIDOnButton():
	global PidState
	PidState = 1
	pid.auto_mode = True
	return str("Done") 

@app.route('/PIDOffButton', methods=["POST"])
def PIDOffButton():
	global PidState
	PidState = 0
	pid.auto_mode = False
	return str("Done") 

@app.route('/CalNButton', methods=["POST"])
def CalNButton():
	CalibrateMin()
	return str("Done") 

@app.route('/LuxSlider', methods=["POST"])
def LuxSlider():
	global WantLux
	WantLux = float(request.form["getal"])
	return str("WantLux")

@app.route('/dataoutW')
def dataoutW():
	global WantLux
	return str(round(float(WantLux), 2))

@app.route('/dataoutX')
def dataoutX():
	global ActLux
	return str(round(float(ActLux), 2))

@app.route('/dataoutY')
def dataoutY():
	global Angle
	return str(Angle)

@app.route('/dataoutWX')
def dataoutWX():
	global ActLux,WantLux
	return str(round(float((WantLux-ActLux)), 2))

@app.route('/dataoutMax')
def dataoutMax():
	global LdrMax
	return str(round(float(LdrMax), 2))

@app.route('/dataoutMin')
def dataoutMin():
	global LdrMin
	return str(round(float(LdrMin), 2))

@app.route('/PSlider', methods=["POST"])
def PSlider():
	global Kp
	Kp = float(request.form["getal"])
	return str(Kp)

@app.route('/ISlider', methods=["POST"])
def ISlider():
	global Ki
	Ki = float(request.form["getal"])
	return str(Ki)

@app.route('/DSlider', methods=["POST"])
def DSlider():
	global Kd
	Kd = float(request.form["getal"])
	return str(Kd)

@app.route('/dataoutP')
def dataoutP():
    global Kp
    return str(Kp)

@app.route('/dataoutI')
def dataoutI():
    global Ki
    return str(Ki)

@app.route('/dataoutD')
def dataoutD():
    global Kd
    return str(Kd)


if __name__ == '__main__':
	_thread.start_new_thread(main,())
	app.run(debug=True, host='0.0.0.0', port=5050, use_reloader=False)

