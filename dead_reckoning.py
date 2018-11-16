#!/usr/bin/python3
"""
file: dead_reckoning.py
"""

from collections import namedtuple
import datetime.datetime.now
from math import cos, sin, pi
from statistics import median
import threading
import time

import Adafruit.Adafruit_LSM303 as Adafruit_LSM303

Position = namedtuple("Position", "x y z")

class DeadReckoning:
    """
    A class for tracking the current position and heading of the robot using an
    LSM303 accelerometer and magnetometer.
    """

    def __init__(self, accelerometer_frequency=5, magnetometer_frequency=5):
        """
        Constructor.
        """
        self.my_lsm303 = Adafruit_LSM303.LSM303(accel_address=0x48)
        self.my_current_position = Position(x=0.0, y=0.0, z=0.0)
        self.my_current_orientation = 0
        self.accel_freq = accelerometer_frequency
        self.mag_freq = magnetometer_frequency
        self.my_accelerometer_thread = threading.Thread(target=self.accelerometer_context,
                                                        args=(),
                                                        name="Accelerometer Thread")
        self.my_magnetometer_thread = threading.Thread(target=self.magnetometer_context,
                                                       args=(),
                                                       name="Magnetometer Thread")

    def get_current_position(self):
        """
        Get the current position relative to the start position.
        """
        return self.my_current_position

    def get_current_heading(self):
        """
        Get the current azimuth heading relative to the start orientation.
        """
        return self.my_current_orientation

    def begin(self):
        """
        Starts a thread to sample the accelerometer and magnetometer
        periodically.
        """
        self.my_app_is_running = True
        self.my_accelerometer_thread.start()
        return 0

    def stop(self):
        """
        Closes down the resources involved for sampling the sensors.
        """
        self.my_app_is_running = False
        return 0

    def accelerometer_context(self):
        """
        Context for the accelerometer thread.
        """
        accel_x = []
        accel_y = []
        accel_z = []
        # collect five values
        for i in range(0, 3):
            accelerometer = self.my_lsm303.read_accelerometer()
            accel_x += [accelerometer[0]]
            accel_y += [accelerometer[1]]
            accel_z += [accelerometer[2]]
            time.sleep(1 / self.accel_freq)

        # find the median in x, y, and z
        acceleration_x_current = median(accel_x)
        acceleration_y_current = median(accel_y)
        acceleration_z_current = median(accel_z)

        velocity_x_current = 0
        velocity_y_current = 0
        velocity_z_current = 0

        time_current = datetime.datetime.now()

        while self.my_app_is_running:
            time.sleep(1 / self.accel_freq)
            if not self.my_app_is_running:
                break
            acceleration_x_previous = acceleration_x_current
            acceleration_y_previous = acceleration_y_current
            acceleration_z_previous = acceleration_z_current
            time_previous = time_current
            velocity_x_previous = velocity_x_current
            velocity_y_previous = velocity_y_current
            velocity_z_previous = velocity_z_current

            # now collect another sensor value
            (acceleration_x_current, acceleration_y_current, acceleration_z_current) = 
                self.my_lsm303.read_accelerometer()
            # find the difference
            diff_a_x = acceleration_x_current - acceleration_x_previous
            diff_a_y = acceleration_y_current - acceleration_y_previous
            diff_a_z = acceleration_z_current - acceleration_z_previous
            # calculate the current velocity in each direction
            velocity_x_current = (diff_a_x / self.accel_freq) + velocity_x_previous
            velocity_y_current = (diff_a_y / self.accel_freq) + velocity_y_previous
            velocity_z_current = (diff_a_z / self.accel_freq) + velocity_z_previous

            # change in posiiton = (change in velocity) * (change in time) / 2
            # division by two comes for average velocity over the period
            self.my_current_position.x = ((velocity_x_current - velocity_x_previous) 
                                         / self.accel_freq 
                                         / 2) * cos(pi / self.my_current_orientation) 
                                         + self.my_current_position.x
            self.my_current_position.y = ((velocity_y_current - velocity_y_previous) 
                                         / self.accel_freq 
                                         / 2) * sin(pi / self.my_current_orientation)
                                         + self.my_current_position.y
            self.my_current_position.z = (velocity_z_current - velocity_z_previous) 
                                         / self.accel_freq 
                                         / 2
                                         + self.my_current_position.z

        return 0

    def magnetometer_context(self):
        """
        """
        while self.my_app_is_running:
            break

        return 0


def main():
    """
    Tests the dead reckoning class by printing the total lateral movement.
    """
    my_position_tracker = DeadReckoning(accelerometer_frequency=100, magnetometer_frequency=15)
    my_position_tracker.begin()

    try:
        while True:
            current_position = my_position_tracker.get_current_position()
            print("Distance Traveled - x: {}, y: {}, z: {}".format(current_position.x, 
                                                                   current_position.y, 
                                                                   current_position.z))
            time.sleep(1)
    except KeyboardInterrupt:
        my_position_tracker.stop()


if __name__ == "__main__":
    main()