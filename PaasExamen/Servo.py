from gpiozero import AngularServo
import time
servo = AngularServo(26, min_angle=0, max_angle=180)
while True:
    helpA = int(input("Deg "))
    servo.angle = helpA
    time.sleep(0.5)