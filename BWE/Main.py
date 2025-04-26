from time import sleep, localtime, strftime, gmtime
import pymysql
from flask import Flask, render_template, request, url_for
import _thread
from gpiozero import AngularServo, DigitalOutputDevice,PWMLED
import logging


# Database connection
conn = pymysql.connect(host='127.0.0.1', unix_socket='/var/run/mysqld/mysqld.sock', user='Smets', passwd='Thomas', db='BWE')
cur = conn.cursor()

app = Flask(__name__, static_folder='www', template_folder='www')
log = logging.getLogger('werkzeug')
log.disabled = True

BucketPer = 50
ConveyorPer = 0
angle = 0

running = True
ServoSpeed = 0
CW = 0
CCW = 1
startspeed = 0.001
stopstappen = 750
speedsleep = 0.02

servo = AngularServo(17, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)  # Replace 17 with your GPIO pin
conveyor = PWMLED(5)
DIR = DigitalOutputDevice(20)  # Direction pin
STEP = DigitalOutputDevice(21)  # Step pin
M1 = DigitalOutputDevice(23)
M2 = DigitalOutputDevice(24)
M1.off()
M2.off()

def logDatabase():
    cur.execute("INSERT INTO Graph(time, BucketSpeed, Conveyorspeed, Angle) VALUES (%s, %s, %s, %s)",(strftime("%Y-%m-%d %H:%M:%S", gmtime()), BucketPer, ConveyorPer, angle))
    conn.commit()
    sleep(1)

def Conveyor():
    global ConveyorPer
    conveyor.value = ConveyorPer/100
    #print("ConveyorSpeed= ", ConveyorPer)

def Bucket():
    global BucketPer, ServoSpeed
    ServoSpeed = (BucketPer/100*180)
    servo.angle = ServoSpeed
    #print("ServoSpeed= ", ServoSpeed)

def step_motor(step_pin, sleep_time, direction):
    """Performs a single step for the motor."""
    print("hhhhhhhhhhhhhhhhhhhhhhhhhhh")
    DIR.value = direction
    step_pin.on()
    sleep(sleep_time)
    step_pin.off()
    sleep(sleep_time)

def StepMotor():
    global angle,running
    while running:
        if angle > 0:
            print("Steppermotor: Forwards")
            calculated = angle * 1750 / 20 #800
            for _ in range(int(calculated)):
                step_motor(STEP, 0.001, CW)
        elif angle < 0:
            print("Steppermotor: Backwards")
            calculated = -angle * 1750 / 20 #350
            for _ in range(int(calculated)):
                step_motor(STEP, 0.001,CCW)
        else:
            print("No movement")
        sleep(1)

def StepMoto():
    print("StepMoto")
    global angle,running
    oldangle = 0
    while running:
        HelpA = (angle-oldangle) / 45 * 1150
        oldangle = angle
        print(HelpA)
        if HelpA > 0:
            print("Steppermotor: Forwards")
            calculated = HelpA
            for _ in range(int(calculated)):
                step_motor(STEP, speedsleep, CW)
        elif HelpA < 0: 
            print("Steppermotor: Backwards")
            calculated = -HelpA
            for _ in range(int(calculated)):
                step_motor(STEP, speedsleep, CCW)
        print("Angle= ", angle)
        print("OldAngle= ", oldangle)
        print("HelpA= ", HelpA)
        
        sleep(1)

def main():
    global BucketPer,ConveyorPer,angle,ServoSpeed,running
    _thread.start_new_thread(logDatabase, ())
    _thread.start_new_thread(StepMoto, ())
    try:
        while running:
            Conveyor()
            Bucket() 
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        running = False
        conn.close()
        exit(0)        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/BucketSpeed', methods=["POST"])
def BucketSpeed():
    global BucketPer
    BucketPer = float(request.form["getal"])
    return str(BucketPer)

@app.route('/Angle', methods=["POST"])
def Angle():
    global angle
    angle = float(request.form["getal"])
    return str(angle)

@app.route('/ConveyorSpeed', methods=["POST"])
def ConveyorSpeed():
    global ConveyorPer
    ConveyorPer = float(request.form["getal"])
    return str(ConveyorPer)

@app.route('/ButtonPos', methods=["POST"])
def ButtonPos():
	global angle
	getal= int(request.form["getal"])
	angle += getal
	return str(angle) 

@app.route('/ButtonNeg', methods=["POST"])
def ButtonNeg():
	global angle
	getal= int(request.form["getal"])
	angle -= getal
	return str(angle) 

@app.route('/ButtonCal', methods=["POST"])
def ButtonCal():
	global angle
	getal= int(request.form["getal"])
	angle -= getal
	return str(angle) 

@app.route('/dataoutBucket')
def dataoutBucket():
    global BucketPer
    HelpA = round(float(BucketPer), 2)
    return str(HelpA)

@app.route('/dataoutConveyor')
def dataoutConveyor():
    global ConveyorPer
    HelpA = round(float(ConveyorPer), 2)
    return str(HelpA)

@app.route('/dataoutAngle')
def dataoutAngle():
    global angle
    HelpA = round(float(angle), 2)
    return str(angle)

@app.route('/dataoutBucketSpeed')
def dataoutBucketSpeed():
    global ServoSpeed
    HelpA = round(float(ServoSpeed), 2)
    return str(HelpA)


if __name__ == '__main__':
    _thread.start_new_thread(main, ())
    app.run(debug=True, host='0.0.0.0', port=5050, use_reloader=False)
