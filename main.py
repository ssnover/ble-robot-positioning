#!/usr/bin/python3

import json
import os.path
import threading

import dead_reckoning
import sensor_fusion
import robot_control
import RPi.GPIO as GPIO

def main():
    """
    Entry point for the positioning robot program.
    """
    # if there's a file with the position, get it and pass it
    if os.path.isfile("start_position.json"):
        position = open("start_position.json")
        init_pos_dict = json.loads(position.read())
        start_position = dead_reckoning.Position(x=init_pos_dict['x'], 
                                                 y=init_pos_dict['y'], 
                                                 z=0.0)
        start_heading = init_pos_dict['heading']
    else:
        start_position = dead_reckoning.Position(x=0.0, y=0.0, z=0.0)
        start_heading = 0.0

    print("Starting Position")
    print("X: {0}, Y: {1}, Heading: {2}".format(start_position.x, start_position.y, start_heading))

    if os.path.isfile("beacon_coordinates.json"):
        beacon_file = open("beacon_coordinates.json", 'r')
        beacon_coords = beacon_file.read()
        coords = json.loads(beacon_coords)
    else:
        coords = []
        print("Enter coordinates of each beacon as xy points separated by a space.")
        for i in range(1, 4):
            input_str = input("{}: ".format(i)).strip()
            x = float(input_str.split(' ')[0])
            y = float(input_str.split(' ')[1])
            coords.append(x)
            coords.append(y)

    print("Beacon Positions")
    for i in range(1, 4):
        print("Beacon {0}: X - {1}, Y - {2}".format(i, coords[2*(i-1)], coords[2*(i-1)+1]))

    # start up IMU threads
    my_imu_sampling = dead_reckoning.DeadReckoning(accelerometer_frequency=50, 
                                                   magnetometer_frequency=25, 
                                                   initial_position=start_position,
                                                   initial_heading=start_heading)
    my_imu_sampling.begin()

    # start up BLE RSSI measurements

    # start up sensor fusion module
    positioning = sensor_fusion.SensorFusion(frequency=1,
                               ble_positioning=None,
                               dead_reckoner=my_imu_sampling)
    positioning.begin()
    # start robot control

    motor_r_pwm = 27
    motor_l_pwm = 22
    motor_r_dir = 4
    motor_l_dir = 17
    freq = 100
    stopped = 0
    slow = 10
    med = 50

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(motor_r_pwm, GPIO.OUT)
    GPIO.setup(motor_l_pwm, GPIO.OUT)
    GPIO.setup(motor_r_dir, GPIO.OUT)
    GPIO.setup(motor_l_dir, GPIO.OUT)
    motor_r = GPIO.PWM(motor_r_pwm, freq)
    motor_l = GPIO.PWM(motor_l_pwm, freq)

    try:
        while True:
            new_position = dead_reckoning.Position(x = 1.0, y = 1.0, z=0.0)
            current_position = my_position_tracker.get_current_position()
            current_orientation = my_position_tracker.get_current_heading()
            dist_x = new_position.x - current_position.x
            dist_y = new_position.y - current_position.y
            dist_tot = sqrt((dist_x)^2+(dist_y)^2)
            newAng = arctan(dist_x/dist_y)
            turn_tot = newAng - current_position + 360

            if current_orientation > 180:
                robot_control.turn(360-current_orientation)
            else:
                robot_control.turn(-1*current_orientation)
            if dist_x > 0:
                if dist_y > 0:
                    robot_control.turn(-1*newAng)
                else:
                    robot_control.turn(-90-newAng)
            else:
                if dist_y < 0:
                    robot_control.turn(90+newAng)
                else:
                    robot_control.turn(newAng)

            robot_control.move(dist_tot)
            time.sleep(0.5)
    except KeyboardInterrupt:
        my_position_tracker.stop()

    pass

if __name__ == "__main__":
    main()
