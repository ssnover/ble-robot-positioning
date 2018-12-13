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
        start_position = dead_reckoning.Position(x=3.0, y=3.0, z=0.0)
        start_heading = 0.0

    print("Starting Position")
    print("X: {0}, Y: {1}, Heading: {2}".format(start_position.x, start_position.y, start_heading))

    if True: #os.path.isfile("beacon_coordinates.json"):
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
        print("Beacon {0}: X: {1}, Y: {2}".format(i, coords[2*(i-1)], coords[2*(i-1)+1]))

    robot_control.ble_positions = robot_control.BEACON_POSITIONS(beacon1=(coords[0], coords[1]),
                                                     beacon2=(coords[2], coords[3]),
                                                     beacon3=(coords[4], coords[5]))
    
    # robot_control.ble_positions = robot_control.BEACON_POSITIONS(beacon1=(0,0),
                                                                 # beacon2=(5,0),
                                                                 # beacon3=(0,5))

    # start up IMU threads
    my_imu_sampling = dead_reckoning.DeadReckoning(accelerometer_frequency=50, 
                                                   magnetometer_frequency=25, 
                                                   initial_position=start_position,
                                                   initial_heading=start_heading)
    my_imu_sampling.begin()

    # start up BLE RSSI measurements
    # start one thread which reads in samples of RSSI measurements
    # start up another thread which runs the trilateration algorithm periodically
    ble_trilateration = None

    # start up sensor fusion module
    positioning = sensor_fusion.SensorFusion(frequency=1,
                               ble_positioning=ble_trilateration,
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

    #GPIO.setup(motor_r_pwm, GPIO.OUT)
    #GPIO.setup(motor_l_pwm, GPIO.OUT)
    #GPIO.setup(motor_r_dir, GPIO.OUT)
    #GPIO.setup(motor_l_dir, GPIO.OUT)

    try:
        robot_control.main( my_imu_sampling, robot_control.ble_positions, start_position.x, start_position.y, start_heading )
        robot_control.finish()
    except KeyboardInterrupt:
        my_position_tracker.stop()

    pass

if __name__ == "__main__":
    main()

