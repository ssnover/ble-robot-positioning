#!/usr/bin/python3
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import time
import math

import sensor_fusion
import dead_reckoning

from gridmove import getGridPosition

class BEACON_POSITIONS(object):
    def __init__(self, beacon1, beacon2, beacon3):
        self.beacon1 = beacon1
        self.beacon2 = beacon2
        self.beacon3 = beacon3

ble_positions = None

# turns the robot by 'degrees'
def turn ( degrees ):
	if degrees > 0:
                GPIO.output(4, 0)
                GPIO.output(17, 1)
	else:
                GPIO.output(4, 1)
                GPIO.output(17, 0)
                degrees *= 1.1
	motor_r.ChangeDutyCycle(50)
	motor_l.ChangeDutyCycle(50)
	time.sleep(abs(degrees)*0.0186*(9.0/7.0))
	motor_l.ChangeDutyCycle(0)
	motor_r.ChangeDutyCycle(0)
	return True

# moves the robot in a straight line
def move ( feet ):
	if feet > 0:
		GPIO.output(4, 0)
		GPIO.output(17, 0)
	else:
		GPIO.output(4, 1)
		GPIO.output(17, 1)
	motor_r.ChangeDutyCycle(50)
	motor_l.ChangeDutyCycle(50)
	time.sleep(feet*6.8/3.0)
	motor_l.ChangeDutyCycle(0)
	motor_r.ChangeDutyCycle(0)
	return True

# stops the robot, motors and the GPIO
def finish ():
	motor_r.ChangeDutyCycle(0)
	motor_l.ChangeDutyCycle(0)
	motor_r.stop()
	motor_l.stop()
	GPIO.cleanup()
	return True

# Uses the Beacon locations as well as the 3 RSSI distances
# to triangulate the robot's location
def getCurrentLocation(dist1, dist2, dist3, ble_0, ble_1, ble_2, ble_3, ble_4, ble_5):
        b1_x = ble_0
        b1_y = ble_1
        b2_x = ble_2
        b2_y = ble_3
        b3_x = ble_4
        b3_y = ble_5

        a1 = -2*b1_x + 2*b2_x
        b1 = -2*b1_y + 2*b2_y
        c1 = b1_x**2 + b1_y**2 - dist1**2 - b2_x**2 - b2_y**2 + dist2**2

        a2 = -2*b1_x + 2*b3_x
        b2 = -2*b1_y + 2*b3_y
        c2 = b1_x**2 + b1_y**2 - dist1**2 - b3_x**2 - b3_y**2 + dist3**2

        a3 = -2*b2_x + 2*b3_x
        b3 = -2*b2_y + 2*b3_y
        c3 = b2_x**2 + b2_y**2 - dist2**2 - b3_x**2 - b3_y**2 + dist3**2

        if b1 == 0:
            b1 = 0.00001
        if b2 == 0:
            b2 = 0.00001

        pos_x1 = (-1*c2 + ((c1*b2)/b1))/(-1*(a1*b2)/b1 + a2)
        pos_y1 = (-1*c1 - a1*pos_x1)/b1

        pos_x2 = (-1*c3 + (c1*b3)/b1)/((-1*a1*b3)/b1 + a3)
        pos_y2 = (-1*c1 - a1*pos_x2)/b1

        pos_x3 = (-1*c3 + (c2*b3)/b2)/((-1*a2*b3)/b2 + a3)
        pos_y3 = (-1*c2 - a2*pos_x3)/b2

        pos_x = (pos_x1+pos_x2+pos_x3)/3
        pos_y = (pos_y1+pos_y2+pos_y3)/3

        return pos_x, pos_y

def getDistAndAngle(curr_x, curr_y, new_x, new_y, current_o):
	dist_x = new_x - curr_x
	dist_y = new_y - curr_y
	totDist = ((dist_x)**2 + (dist_y)**2)**(0.5)

	newAng = -1*math.degrees(math.atan2(dist_x, dist_y))
	if current_o > 180:
            current_o = current_o - 360
	totAngle = newAng - current_o
	#if totAngle > 180
        #    totAngle = 360-totAngle
	if totAngle > 180:
            totAngle = totAngle - 360
	if totAngle < -180:
            totAngle = totAngle + 360

	return totDist, totAngle

# main function
def main( dead_reckoner, ble_pos, start_x, start_y, curr_head ):

	GPIO.setwarnings(False)
	#motor_r = GPIO.PWM(27, 100)
	#motor_l = GPIO.PWM(22, 100)
	GPIO.output(4, 0)
	GPIO.output(17, 0)
	motor_r.start(0)
	motor_l.start(0)

	current_x = start_x
	current_y = start_y
	curr_orient = curr_head

	new_x = 0.0
	new_y = 0.0

	while True:
            while False:
                turn(90)
                print("Heading from IMU: ", dead_reckoner.get_current_heading())
                input("...")
            print("=============================================================")
            print("Current X: ", current_x)
            print("Current Y: ", current_y)
            print("Current Orientation: ", curr_orient)
            curr_orient_imu = dead_reckoner.get_current_heading()
            print("Current Heading from IMU: ", curr_orient_imu)

            temp_x = 0.0
            temp_y = 0.0

            # simulated values to test out the triangulation function with known beacon locations
            #d1 = ((ble_pos.beacon1[0]-current_x)**2+(ble_pos.beacon1[1]-current_y)**2)**(0.5)*1.03
            #d2 = ((ble_pos.beacon2[0]-current_x)**2+(ble_pos.beacon2[1]-current_y)**2)**(0.5)*1.03
            #d3 = ((ble_pos.beacon3[0]-current_x)**2+(ble_pos.beacon3[1]-current_y)**2)**(0.5)*1.03

            # calculated X, Y location of the robot from RSSI triangulation distances
            temp_x, temp_y = getGridPosition() #getCurrentLocation(d1, d2, d3, ble_pos.beacon1[0], ble_pos.beacon1[1], ble_pos.beacon2[0], ble_pos.beacon2[1], ble_pos.beacon3[0], ble_pos.beacon3[1])
            print("Calculated Current X Pos: ", temp_x)
            print("Calculated Current Y Pos: ", temp_y)
            print(" ")

            # Enter new location for the robot to move to
            print("Enter coordinates of New XY Location seperated by a space.")
            input_new = input("{}: ".format("X Y")).strip()
            new_x = float(input_new.split(' ')[0])
            new_y = float(input_new.split(' ')[1])

            dist_tot, angle_tot = getDistAndAngle(temp_x, temp_y, new_x, new_y, curr_orient)
            print("Distance to New Location: ", dist_tot)
            print("Degrees to Turn: ", angle_tot)
            print(" ")
            input("Press Enter to Move to New Location:")
            turn(angle_tot)
            move(dist_tot)

            current_x = new_x
            current_y = new_y
            curr_orient = curr_orient + angle_tot
            if curr_orient < 0:
                curr_orient = 360 + curr_orient
            if curr_orient > 360:
                curr_orient - 360
	return True

GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

motor_r = GPIO.PWM(27, 100)
motor_l = GPIO.PWM(22, 100)

b1_x = 1.0
b1_y = 15.0
b2_x = 4.0
b2_y = 2.0
b3_x = 20.0
b3_y = 8.0

fast = 70
full = 100

if __name__ == "__main__":
	main()




