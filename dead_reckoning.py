#!/usr/bin/python3
"""
file: dead_reckoning.py
"""

from collections import namedtuple
import datetime
from math import atan2, cos, sin, pi
from statistics import median
import threading
import time

import Adafruit.Adafruit_LSM303 as Adafruit_LSM303

#Position = namedtuple("Position", "x y z")


class Position(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


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
        self.my_initial_orientation = 0
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

        Also scales the position to account for measurement in milli-g's.
        """
        position_meters = Position(x=self.my_current_position.x * 9.81 * 10e-3,
                                   y=self.my_current_position.y * 9.81 * 10e-3,
                                   z=self.my_current_position.z * 9.81 * 10e-3)
        return position_meters

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
        self.my_magnetometer_thread.start()
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
        self.my_lsm303.set_accelerometer_resolution(
            Adafruit_LSM303.LSM303_ACCEL_1_MG_PER_LSB)
        self.my_lsm303.set_accelerometer_datarate(
            Adafruit_LSM303.LSM303_ACCEL_RATE_200_HZ)

        accel_x = []
        accel_y = []
        accel_z = []
        # collect five values
        for _ in range(0, 3):
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

        while self.my_app_is_running:
            time.sleep(1 / self.accel_freq)
            if not self.my_app_is_running:
                break
            acceleration_x_previous = acceleration_x_current
            acceleration_y_previous = acceleration_y_current
            acceleration_z_previous = acceleration_z_current
            velocity_x_previous = velocity_x_current
            velocity_y_previous = velocity_y_current
            velocity_z_previous = velocity_z_current

            # now collect another sensor value
            (acceleration_x_current, acceleration_y_current,
             acceleration_z_current) = self.my_lsm303.read_accelerometer()
            # find the difference
            diff_a_x = acceleration_x_current - acceleration_x_previous
            diff_a_y = acceleration_y_current - acceleration_y_previous
            diff_a_z = acceleration_z_current - acceleration_z_previous
            # calculate the current velocity in each direction
            velocity_x_current = (
                diff_a_x / self.accel_freq) + velocity_x_previous
            velocity_y_current = (
                diff_a_y / self.accel_freq) + velocity_y_previous
            velocity_z_current = (
                diff_a_z / self.accel_freq) + velocity_z_previous

            # change in posiiton = (change in velocity) * (change in time) / 2
            # division by two comes for average velocity over the period
            self.my_current_position.x = ((velocity_x_current - velocity_x_previous) / self.accel_freq / 2) * cos(
                self.my_current_orientation) + self.my_current_position.x
            self.my_current_position.y = ((velocity_y_current - velocity_y_previous) / self.accel_freq / 2) * sin(
                self.my_current_orientation) + self.my_current_position.y
            self.my_current_position.z = (
                velocity_z_current - velocity_z_previous) / self.accel_freq / 2 + self.my_current_position.z

        return 0

    def magnetometer_context(self):
        """
        Context for the magnetometer thread
        """
        self.my_lsm303.set_magnetometer_datarate(
            Adafruit_LSM303.LSM303_MAG_RATE_30_HZ)

        # Take 3 magnetometer measurements and take the mean to get a
        # more accurate starting position.
        azimuth_sum = 0
        for _ in range(0, 3):
            time.sleep(1 / self.mag_freq)
            (x, y, _) = self.my_lsm303.read_magnetometer()
            azimuth = atan2(float(y), float(x))
            azimuth_sum += azimuth
        self.my_initial_orientation = azimuth_sum / 3

        # Repeatedly measure the magnetometer and set the new orientation
        while self.my_app_is_running:
            time.sleep(1 / self.mag_freq)

            (x, y, _) = self.my_lsm303.read_magnetometer()
            # find the azimuth angle
            self.my_current_orientation = atan2(float(y), float(x))

        return 0


def main():
    """
    Tests the dead reckoning class by printing the total lateral movement.
    """
    my_position_tracker = DeadReckoning(
        accelerometer_frequency=100, magnetometer_frequency=15)
    my_position_tracker.begin()

    try:
        while True:
            current_position = my_position_tracker.get_current_position()
            print("Distance Traveled - x: {0:.2f} mm, y: {0:.2f} mm, z: {0:.2f} mm".format(current_position.x*1000,
                                                                                           current_position.y*1000,
                                                                                           current_position.z*1000))
            current_orientation = my_position_tracker.get_current_heading()
            print("Change in Heading - {} degrees".format(current_orientation * 180 / pi))
            time.sleep(1)
    except KeyboardInterrupt:
        my_position_tracker.stop()


if __name__ == "__main__":
    main()
