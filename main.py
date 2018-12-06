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
    if os.path.isfile("starting_position.json"):
        position = open("starting_position.json")
        init_pos_dict = json.loads(position.read())
        start_position = dead_reckoning.Position(x=init_pos_dict['x'], 
                                                 y=init_pos_dict['y'], 
                                                 z=0.0)
    else:
        start_position = dead_reckoning.Position(x=0.0, y=0.0, z=0.0)

    # start up tcp server to take directions

    # start up IMU threads
    my_imu_sampling = dead_reckoning.DeadReckoning(accelerometer_frequency=50, 
                                                   magnetometer_frequency=25, 
                                                   initial_position=start_position)
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

    turn(90)
    turn(-90)

    pass

if __name__ == "__main__":
    main()
