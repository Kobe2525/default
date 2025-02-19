from time import sleep, localtime, strftime,gmtime
import pymysql
import board
import adafruit_bmp280
from flask import Flask, render_template, request, url_for
import _thread
from gpiozero import PWMLED

Vent = PWMLED(6)

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c,address = 0x76)



# change this to match the location's pressure (hPa) at sea level
bmp280.sea_level_pressure = 1013.25
conn = pymysql.connect(host='127.0.0.1', unix_socket='/var/run/mysqld/mysqld.sock', user='Smets', passwd='Thomas', db='Temp')
cur = conn.cursor()

WantTemp=20
ActTemp=0
y=0

def read_cpu_temperature():
	try:
		# Pad naar het bestand met de CPU-temperatuur
		temp_file = "/sys/class/thermal/thermal_zone0/temp"
		
		# Lees de temperatuurwaarde
		with open(temp_file, 'r') as file:
			temp = file.read().strip()
		
		# De temperatuur wordt geretourneerd in milligraden Celsius (bijv. 45000 = 45.0°C)
		temperature_celsius = int(temp) / 1000.0
		return temperature_celsius
	except FileNotFoundError:
		print("Het bestand voor CPU-temperatuur is niet gevonden. Controleer of het systeem compatibel is.")
		return None
	except Exception as e:
		print(f"Er is een fout opgetreden bij het lezen van de CPU-temperatuur: {e}")
		return None

def Read():
   temp = bmp280.temperature
   return temp

def main():
	global WantTemp
	global ActTemp
	global y
	while True: 
		a = read_cpu_temperature()
		ActTemp = Read()
		if (WantTemp-ActTemp) <= -1:
			Vent.value = 1
			y = 1
		elif (WantTemp-ActTemp) >= 1:
			Vent.value = 0
			y=0
		yT = y*10
		# INSERT INTO [tabelnaam] (kolom1,kolom2) VALUES (%s,%s) Tijd moet in phpmyadmin datatype "TIMESTAMP" hebben
		cur.execute("INSERT INTO CPUTemp(time,Temp,TempBMP,TempWant,y) VALUES (%s,%s,%s,%s,%s)",(strftime("%Y-%m-%d %H:%M:%S", gmtime()),a,ActTemp,WantTemp,yT))
		conn.commit()
		sleep(1)
		
	
	


app = Flask(__name__, static_url_path='/style.css', static_folder='www', template_folder='www')
#Als de host (ip van je raspberry pi) opgevraagd wordt op de root directory ('/')
#dan gaan we de functie "index" uitvoeren
@app.route('/')
#functie "index"
def index():
	return render_template('index.html')

@app.route('/TempSlider', methods=["POST"])
def TempSlider():
	global WantTemp
	getal= int(request.form["getal"])
	WantTemp = getal
	return str(WantTemp) 

@app.route('/dataoutW')
def dataoutW():
	global WantTemp
	return str (round(WantTemp,2))

@app.route('/dataoutX')
def dataoutX():
	global ActTemp
	return str (round(ActTemp,2))

@app.route('/dataoutY')
def dataoutY():
	global y
	if y == 0:
		return str ("uit")
	elif y == 1:
		return str ("aan")
	else:
		return str ("heeft een error")

@app.route('/dataoutYP')
def dataoutYP():
	global y
	if y == 1:
		image = "/style.css/freezer.png"
		return f'<img src="{image}" class="image" />'
	elif y == 0:
		return str ("")
	else:
		return str ("heeft een error")

@app.route('/dataoutWX')
def dataoutWX():
	global ActTemp,WantTemp
	a = WantTemp - ActTemp
	return str (round(a,2))

if __name__ == '__main__':
	_thread.start_new_thread(main, ())
#host='0.0.0.0' => De webapp is nu toegankelijk via het ip van de raspberry pi.
#De webapp gaat luisteren op poort 5050
	app.run(debug=True, host='0.0.0.0',port=5050, use_reloader=False)
