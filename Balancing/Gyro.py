import smbus
import math
from mpu6050 import mpu6050
from time import sleep
from gpiozero import DigitalOutputDevice
import _thread
import os

class Gyro(	):
	def __init__(self, adres):
		from mpu6050 import mpu6050
		import smbus
		self.ADDRESS = adres
		self.sensor = mpu6050(self.ADDRESS)
		self.bus = smbus.SMBus(1)
		self.gyro_offset_x = 0
		self.gyro_offset_y = 0
		self.gyro_total_x = 0
		self.gyro_total_y = 0
		self.last_x = 0
		self.last_y = 0
		self.K = 0.98
		self.K1 = 1 - self.K
		self.W = 0
		self.time_diff = 0.02
		self.ITerm = 0
		self.X = 0
		self.Y = 0
		self.freq = 0
	
	def distance(self, a, b):
		return math.sqrt((a*a) + (b*b))

	def y_rotation(self, x, y, z):
		radians = math.atan2(x, self.distance(y, z))
		return -math.degrees(radians)

	def x_rotation(self, x, y, z):
		radians = math.atan2(y, self.distance(x, z))
		return math.degrees(radians)

	def initialize(self):
		self.K = 0.98
		self.K1 = 1 - self.K

		self.W = 0

		self.time_diff = 0.02
		self.ITerm = 0

		#Calling the MPU6050 data 
		accel_data = self.sensor.get_accel_data()
		gyro_data = self.sensor.get_gyro_data()

		aTempX = accel_data['x']
		aTempY = accel_data['y']
		aTempZ = accel_data['z']

		gTempX = gyro_data['x']
		gTempY = gyro_data['y']
		gTempZ = gyro_data['z']




		self.last_x = self.x_rotation(aTempX, aTempY, aTempZ)
		self.last_y = self.y_rotation(aTempX, aTempY, aTempZ)

		self.gyro_offset_x = gTempX
		self.gyro_offset_y = gTempY

		self.gyro_total_x = (self.last_x) - self.gyro_offset_x
		self.gyro_total_y = (self.last_y) - self.gyro_offset_y
		#-------------------------------------------------------------------------------FILTER STOP
		#-------------------------------------------------------------------------------MPU6050 interne filter Start
		power_mgmt_1 = 0x6b
		power_mgmt_2 = 0x6c 
		DeviceAddress = 0x68
		CONFIG       = 0x1A
		self.bus.write_byte_data(DeviceAddress, power_mgmt_1, 0)
		#Write to Configuration register
		#Setting DLPF (last three bit of 0X1A to 6 i.e '110' It removes the noise due to vibration.) https://ulrichbuschbaum.wordpress.com/2015/01/18/using-the-mpu6050s-dlpf/
		#bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))	
		self.bus.write_byte_data(DeviceAddress, CONFIG, int('0000110',2))
		

	def read(self):
		
		#-------------------------------------------------------------------------------FILTER START
		accel_data = self.sensor.get_accel_data()
		gyro_data = self.sensor.get_gyro_data()

		accelX = accel_data['x']
		accelY = accel_data['y']
		accelZ = accel_data['z']

		gyroX = gyro_data['x']
		gyroY = gyro_data['y']
		gyroZ = gyro_data['z']

		gyroX -= self.gyro_offset_x
		gyroY -= self.gyro_offset_y

		gyro_x_delta = (gyroX * self.time_diff)
		gyro_y_delta = (gyroY * self.time_diff)

		self.gyro_total_x += gyro_x_delta
		self.gyro_total_y += gyro_y_delta

		rotation_x = self.x_rotation(accelX, accelY, accelZ)
		rotation_y = self.y_rotation(accelX, accelY, accelZ)
		
		#Complementary Filter
		self.last_x = self.K * (self.last_x + gyro_x_delta) + (self.K1 * rotation_x)
		self.last_y = self.K * (self.last_y + gyro_y_delta) + (self.K1 * rotation_y)
		#------------------------------------------------------------------------------FILTER STOP
		self.X = round(self.last_x, 3)
		self.Y = round(self.last_y, 3)
		#Print

		# print('gyro = ' + str(self.X) +'  gewenste=' + str(self.W))
		# print('gyro = ' + str(self.Y) +'  gewenste=' + str(self.W))
		sleep(0.01)
		os.system('clear')
		return 'gyro = ' + str(self.X) + '  gewenste=' + str(self.W) + ' gyro = ' + str(self.Y) +'  gewenste=' + str(self.W)
	
