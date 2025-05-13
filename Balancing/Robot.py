from gpiozero import DigitalOutputDevice
from time import sleep
from Gyro import Gyro

gyro = Gyro(0x68)
gyro.initialize()
while True:
    print(gyro.read())

# Pin definitions
pinvent = DigitalOutputDevice(12, initial_value=True)

# Direction pins
DIR = DigitalOutputDevice(20)
DIR2 = DigitalOutputDevice(26)

# Step pins
STEP = DigitalOutputDevice(19)
STEP2 = DigitalOutputDevice(21)

# Direction constants
CW = 0
CCW = 1
CW2 = 1
CCW2 = 0

# Timing constants
startspeed = 0.001
stopstappen = 750
speedsleep = 0.0002



def forwards(cm):
    DIR.value = CW
    DIR2.value = CW2
    print("CCW")

    calculated = cm * 1750 / 20
    stapjes = (startspeed - speedsleep) / stopstappen
    print(stapjes)

    for i in range(stopstappen):
        print(startspeed - stapjes * i)
        STEP.on()
        STEP2.on()
        sleep(startspeed - stapjes * i)
        STEP.off()
        STEP2.off()
        sleep(startspeed - stapjes * i)

    for x in range(int(calculated - 500)):
        print(speedsleep)
        STEP.on()
        STEP2.on()
        sleep(speedsleep)
        STEP.off()
        STEP2.off()
        sleep(speedsleep)

def backwards(cm):
    DIR.value = CCW
    DIR2.value = CCW2
    print("CCW")

    calculated = cm * 1750 / 20

    for x in range(int(calculated)):
        STEP.on()
        STEP2.on()
        sleep(0.001)
        STEP.off()
        STEP2.off()
        sleep(0.001)

def right(gr):
    DIR.value = CCW
    DIR2.value = CW2
    print("Rechts")
    calculated = (2500 * (gr / 90)) / 2

    for x in range(int(calculated)):
        STEP.on()
        STEP2.on()
        sleep(0.001)
        STEP.off()
        STEP2.off()
        sleep(0.001)

def left(gr):
    DIR.value = CW
    DIR2.value = CCW2
    print("Rechts")
    calculated = (2500 * (gr / 90)) / 2

    for x in range(int(calculated)):
        STEP.on()
        STEP2.on()
        sleep(0.001)
        STEP.off()
        STEP2.off()
        sleep(0.001)

def stop():
    DIR.value = CW
    DIR2.value = CW2
    print("CCW")
    stapjes = (startspeed - speedsleep) / stopstappen

    for x in range(stopstappen):
        STEP.on()
        STEP2.on()
        sleep(speedsleep + stapjes * x)
        STEP.off()
        STEP2.off()
        sleep(speedsleep + stapjes * x)

def Exam():
    forwards(80)
    stop()
    sleep(1)
    print("left")
    left(47)
    sleep(1)
    forwards(52)
    stop()
    right(49)
    forwards(70)
    stop()

def returnHome():
    sleep(2)
    backwards(30)
    left(45)
    backwards(45)
    sleep(1)
    right(45)
    sleep(1)
    backwards(90)
    sleep(2)

try:
    sleep(3)
    Exam()
except KeyboardInterrupt:
    stop()
    pinvent.off()
    print("cleanup")