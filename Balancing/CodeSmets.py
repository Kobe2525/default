from mpu6050 import mpu6050
import wiringpi
import RPi.GPIO as GPIO
import atexit
from flask import Flask, render_template, request
import _thread
from time import sleep, gmtime, strftime
import io
import smbus
from simple_pid import PID
import os
import math

#-------------------------------------------------------------------------------FILTER START

sensor = mpu6050(0x68)
#K and K1 --> Constants used with the complementary filter
K = 0.98
K1 = 1 - K

time_diff = 0.02
ITerm = 0

#Calling the MPU6050 data 
accel_data = sensor.get_accel_data()
gyro_data = sensor.get_gyro_data()

aTempX = accel_data['x']
aTempY = accel_data['y']
aTempZ = accel_data['z']

gTempX = gyro_data['x']
gTempY = gyro_data['y']
gTempZ = gyro_data['z']

#some math 
def distance(a, b):
	return math.sqrt((a*a) + (b*b))

def y_rotation(x, y, z):
	radians = math.atan2(x, distance(y, z))
	return -math.degrees(radians)

def x_rotation(x, y, z):
	radians = math.atan2(y, distance(x, z))
	return math.degrees(radians)


last_x = x_rotation(aTempX, aTempY, aTempZ)
last_y = y_rotation(aTempX, aTempY, aTempZ)

gyro_offset_x = gTempX
gyro_offset_y = gTempY

gyro_total_x = (last_x) - gyro_offset_x
gyro_total_y = (last_y) - gyro_offset_y
#-------------------------------------------------------------------------------FILTER STOP
#-------------------------------------------------------------------------------MPU6050 interne filter Start
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1) 
DeviceAddress = 0x68
CONFIG       = 0x1A
bus.write_byte_data(DeviceAddress, power_mgmt_1, 0)
#Write to Configuration register
#Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
#bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))	
bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))
#-------------------------------------------------------------------------------MPU6050 interne filter STOP	

app = Flask(__name__, static_url_path='', static_folder='www', template_folder='www')

#-------------------------------------------------------------------------------Pinconfig Motor START

GPIO.setmode(GPIO.BCM)

GPIO_pins1 = (16, 20, 21) 
direction1 = 7    
step1 = 8      

GPIO_pins2 = (26, 19, 13) 
direction2 = 5      
step2 = 6 

#Motor config M1
GPIO.setup(direction1, GPIO.OUT)
GPIO.setup(step1, GPIO.OUT)
GPIO.setup(GPIO_pins1, GPIO.OUT)
GPIO.output(direction1, 1)   
GPIO.output(GPIO_pins1, (1, 1, 0))

#Motor config M2
GPIO.setup(direction2, GPIO.OUT)
GPIO.setup(step2, GPIO.OUT)
GPIO.setup(GPIO_pins2, GPIO.OUT)
GPIO.output(direction2, 1)   
GPIO.output(GPIO_pins2, (1, 1, 0))

PWM1 = GPIO.PWM(step1, 1) 	#starten 1Hz
PWM1.start(50) 				#DC 50%
PWM2 = GPIO.PWM(step2, 1) 	#starten 1Hz
PWM2.start(50) 				#DC 50%

#-------------------------------------------------------------------------------Pinconfig Motor STOP

#-------------------------------------------------------------------------------Init Variable
Y = 1
X =0
W = 0
P = 400
I = 2000
D = 10
simpletime = 0.001
freq = 1
delays = 5							# minimum volgens datasheet DRV8825 250KHz = T = 4µs = Delay 2 µs ==> 5 µs moet zeker lukken ==> x 100 om Y te laten mee spelen 500µs
initialdelay = 5					#tijd geven voor configuratie
#--------------------------------------------------------------------------------Init Variable STOP

pid = PID(P, I, D, setpoint = W)				#starten met instellen PIDregeling
pid.simple_time = simpletime					#gaat elke 0.01 sec lezen
pid.output_limits = (-100000, 100000)			#max 100khz
pid.auto_mode = True

sleep(initialdelay)


#main multithread
def main():
	global Y, X, W, freq, gyro_total_x, gyro_total_y, last_x
	while (True):
		#-------------------------------------------------------------------------------FILTER START
		accel_data = sensor.get_accel_data()
		gyro_data = sensor.get_gyro_data()

		accelX = accel_data['x']
		accelY = accel_data['y']
		accelZ = accel_data['z']

		gyroX = gyro_data['x']
		gyroY = gyro_data['y']
		gyroZ = gyro_data['z']

		gyroX -= gyro_offset_x
		gyroY -= gyro_offset_y

		gyro_x_delta = (gyroX * time_diff)
		gyro_y_delta = (gyroY * time_diff)

		gyro_total_x += gyro_x_delta
		gyro_total_y += gyro_y_delta

		rotation_x = x_rotation(accelX, accelY, accelZ)
		rotation_y = y_rotation(accelX, accelY, accelZ)
		
		#Complementary Filter
		last_x = K * (last_x + gyro_x_delta) + (K1 * rotation_x)
		#-------------------------------------------------------------------------------FILTER STOP
		X = round(last_x, 3)
		#Print
		os.system('clear')
		print('gyrooooo = ' + str(X) +'  gewenste=' + str(W))

		#Berekeing Y
		pid.setpoint = W
		Y = round(pid(X),2)
		freq = round((abs(Y)),3)+1						# 100KHz

		#Motor richting Links Rechts sturing
		GPIO.output(direction1, (Y>=0))			#Als Y < 0 motor 2 rechts en omgekeerd
		GPIO.output(direction2, (Y<=0))			#Als Y < 0 motor 1 links en omgekeerd
		#MotorStappen frequency
		PWM1.ChangeFrequency(freq)
		PWM2.ChangeFrequency(freq)

		sleep(simpletime)

_thread.start_new_thread(main,())

#flask server inputs en outputs
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/updateW',methods=["POST"])
def updateW():
	global W
	W = float(request.form["Wnew"])
	print(W)
	
@app.route('/updateP',methods=["POST"])
def updateP():
	global P
	P = float(request.form["Pnew"])
	pid.Kp = P

@app.route('/updateI',methods=["POST"])
def updateI():
	global I
	I = float(request.form["Inew"])
	pid.Ki = I

@app.route('/updateD',methods=["POST"])
def updateD():
	global D
	D = float(request.form["Dnew"])
	pid.Kd = D

@app.route('/dataout')
def dataout():
	return 'X = Gyro : ' + str(X) + '<br>W : ' + str(W) + '<br>Y : ' + str(Y) + ' ' + '<br>Frequentie : ' + str(freq) + 'Hz'  + '<br>P : : ' + str(P) + ' ' + '<br>I : : ' + str(round(I,2)) + ' ' + '<br>D : : '+ str(D)

def stop():
	GPIO.cleanup()

if __name__ == '__main__':

	atexit.register(stop)
	app.run(debug=True, host='0.0.0.0',port=5050, use_reloader=False)