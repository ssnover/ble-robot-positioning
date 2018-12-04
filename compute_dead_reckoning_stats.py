#!/usr/bin/python3
import statistics
import time

from Adafruit.Adafruit_BNO055 import BNO055

bno = BNO055()

if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

accelerations_x = []
accelerations_y = []
accelerations_z = []

headings = []

for i in range(0, 1000):
    time.sleep(1)
    heading, _, _ = bno.read_euler()
    x, y, z = bno.read_linear_acceleration()
    headings += [heading]
    accelerations_x += [x]
    accelerations_y += [y]
    accelerations_z += [z]

print("Mean Heading: {}".format(statistics.mean(headings)))
print("Std Dev Heading: {}".format(statistics.stdev(headings)))

print("Linear Acceleration")
print("Mean X: {}".format(statistics.mean(accelerations_x)))
print("Std Dev X: {}".format(statistics.stdev(x)))
print("Mean Y: {}".format(statistics.mean(accelerations_y)))
print("Std Dev Y: {}".format(statistics.stdev(accelerations_y)))
print("Mean Z: {}".format(statistics.mean(accelerations_z)))
print("Std Dev Z: {}".format(statistics.stdev(accelerations_z)))
