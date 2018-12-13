#!/usr/bin/python3
"""
file: dead_reckoning.py
"""

import datetime
from math import atan2, cos, sin, pi, radians
from statistics import median
import threading
import time

import Adafruit.Adafruit_BNO055 as Adafruit_BNO055

class Position(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class DeadReckoning:
    """
    A class for tracking the current position and heading of the robot using an
    accelerometer and magnetometer.
    """

    def __init__(self, 
                 accelerometer_frequency=5, 
                 magnetometer_frequency=5, 
                 initial_position=Position(x=0.0, y=0.0, z=0.0),
                 initial_heading=0):
        """
        Constructor.
        """
        self.my_bno055 = Adafruit_BNO055.BNO055()
        self.my_current_position = initial_position
        self.my_current_orientation = 0
        self.my_initial_orientation = 0
        self.my_previous_position = 0
        self.my_app_is_running = False
        self.my_starting_local_heading = initial_heading
        self.accel_freq = accelerometer_frequency
        self.mag_freq = magnetometer_frequency
        self.my_accelerometer_thread = threading.Thread(target=self.accelerometer_context,
                                                        args=(),
                                                        name="Accelerometer Thread")
        self.my_magnetometer_thread = threading.Thread(target=self.magnetometer_context,
                                                       args=(),
                                                       name="Magnetometer Thread")
        self.my_sensor_mutex = threading.Lock()

    def convert_global_heading_to_local_heading(self, global_heading):
        """
        """
        return (360 
                - global_heading 
                + self.my_initial_orientation 
                + self.my_starting_local_heading) % 360

    def get_current_position(self):
        """
        Get the current position absolute to the start position in meters.
        """
        position_meters = Position(x=self.my_current_position.x,
                                   y=self.my_current_position.y,
                                   z=self.my_current_position.z)
        return position_meters

    def set_current_position(self, new_position):
        """
        Set the current position in meters.
        """
        self.my_current_position = new_position
        self.my_previous_position = new_position
        self.my_nMinus1_position = new_position

    def get_current_heading(self):
        """
        Get the current azimuth heading relative to the start orientation.
        """
        return self.convert_global_heading_to_local_heading(self.my_current_orientation)

    def begin(self):
        """
        Starts a thread to sample the accelerometer and magnetometer
        periodically.
        """
        self.my_bno055.begin()
        self.my_app_is_running = True
        calibration_file = open('bno055_calibration.bin', 'r')
        #print(calibration_file.read())
        calibration_data = calibration_file.read().split(' ')
        print(len(calibration_data))
        calibration_data_int = []
        for datum in calibration_data:
            #print(datum)
            if datum != '':
                calibration_data_int.append(int(datum))
        calibration_file.close()
        self.my_bno055.set_calibration(calibration_data_int)
        self.my_accelerometer_thread.start()
        self.my_magnetometer_thread.start()
        return 0

    def stop(self):
        """
        Closes down the resources involved for sampling the sensors.
        """
        return 0

    def accelerometer_context(self):
        """
        Context for the accelerometer thread.
        """
        accel_x = 0
        accel_y = 0
        accel_z = 0
        time_current = datetime.datetime.now()

        self.my_sensor_mutex.acquire(blocking=True)
        accelerometer = self.my_bno055.read_linear_acceleration()
        self.my_sensor_mutex.release()
        accel_x = accelerometer[0]
        accel_y = accelerometer[1]
        accel_z = accelerometer[2]
        if abs(accel_z) < 0.1:
            accel_z = 0
        if abs(accel_y) < 0.1:
            accel_y = 0
        if abs(accel_x) < 0.1:
            accel_x = 0

        acceleration_x_current = (accel_x)
        acceleration_y_current = (accel_y)
        acceleration_z_current = (accel_z)

        velocity_x_current = 0
        velocity_y_current = 0
        velocity_z_current = 0

        self.my_nMinus1_position = self.my_previous_position
        self.my_previous_position = self.my_current_position
        self.my_current_position = Position(x=0.0, y=0.0, z=0.0)

        while self.my_app_is_running:
            time.sleep(1 / self.accel_freq)
            acceleration_x_previous = acceleration_x_current
            acceleration_y_previous = acceleration_y_current
            acceleration_z_previous = acceleration_z_current
            velocity_x_previous = velocity_x_current
            velocity_y_previous = velocity_y_current
            velocity_z_previous = velocity_z_current
            time_previous = time_current
            delta_time = 1/ self.accel_freq
            # get the new time
            time_current = datetime.datetime.now()
            # time between sampling
            delta_time_prev = delta_time
            delta_time = 1 / self.accel_freq

            # now collect another sensor value
            self.my_sensor_mutex.acquire(blocking=True)
            (acceleration_x_current, acceleration_y_current,
             acceleration_z_current) = self.my_bno055.read_linear_acceleration()
            self.my_sensor_mutex.release()
            if acceleration_x_current > 1.2:
                if acceleration_x_current < 1.5:
                    acceleration_x_current = 0
            acceleration_x_current = acceleration_x_current + 0.05
            acceleration_z_current = acceleration_z_current + 0.14
            if abs(acceleration_x_current) < 0.1:
                acceleration_x_current = 0
            if abs(acceleration_y_current) < 0.1:
                acceleration_y_current = 0
            if abs(acceleration_z_current) < 0.1:
                acceleration_z_current = 0
            # find the difference
            diff_a_x = (acceleration_x_current - acceleration_x_previous)
            diff_a_y = (acceleration_y_current - acceleration_y_previous)
            diff_a_z = (acceleration_z_current - acceleration_z_previous)
            # calculate the current velocity in each direction
            velocity_x_current = (acceleration_x_current * delta_time)*1.03 + velocity_x_previous/1.03
            velocity_y_current = (acceleration_y_current * delta_time)*1.03 + velocity_y_previous/1.03
            velocity_z_current = (acceleration_z_current * delta_time)*1.03 + velocity_z_previous/1.03

            if abs(velocity_x_current) < 0.01:
                velocity_x_current = 0
            if abs(velocity_y_current) < 0.01:
                velocity_y_current = 0
            if abs(velocity_z_current) < 0.01:
                velocity_z_current = 0

            if abs(velocity_x_current) > 1:
                velocity_x_current = 0
            if abs(velocity_y_current) > 0.7:
                velocity_Y_current = 0
            if abs(velocity_z_current > 0.5):
                velocity_z_current = 0

            # change in posiiton = (change in velocity) * (change in time)
            # division by two comes for average velocity over the period
            delta_v_x = (velocity_x_current - velocity_x_previous) / 2
            delta_v_y = (velocity_y_current - velocity_y_previous) / 2
            delta_v_z = (velocity_z_current - velocity_z_previous) / 2
            self.my_nMinus1_position = self.my_previous_position
            self.my_previous_position = self.my_current_position
            self.my_current_position.x = self.my_previous_position.x + (velocity_x_current * delta_time) + (1/2)*(acceleration_x_current*delta_time**2)
            self.my_current_position.y = self.my_previous_position.y + (velocity_y_current * delta_time) + (1/2)*(acceleration_y_current*delta_time**2)
            self.my_current_position.z = self.my_previous_position.z + (velocity_z_current * delta_time) + (1/2)*(acceleration_z_current*delta_time**2)

        return 0

    def magnetometer_context(self):
        """
        Context for the magnetometer thread
        """

        # Take 3 magnetometer measurements and take the mean to get a
        # more accurate starting position.
        headings = 0
        for _ in range(0, 3):
            time.sleep(1 / self.mag_freq)
            self.my_sensor_mutex.acquire(blocking=True)
            (heading, _, _) = self.my_bno055.read_euler()
            self.my_sensor_mutex.release()
            headings += heading
        self.my_sensor_mutex.acquire(blocking=True)
        (self.my_initial_orientation, _, _) = self.my_bno055.read_euler()
        self.my_sensor_mutex.release()

        # Repeatedly measure the magnetometer and set the new orientation
        while self.my_app_is_running:
            time.sleep(1 / self.mag_freq)

            self.my_sensor_mutex.acquire(blocking=True)
            (heading, _, _) = self.my_bno055.read_euler()
            self.my_sensor_mutex.release()

            self.my_current_orientation = heading

        return 0


def main():
    """
    Tests the dead reckoning class by printing the total lateral movement.
    """
    my_position_tracker = DeadReckoning(
        accelerometer_frequency=50, magnetometer_frequency=5)
    my_position_tracker.begin()

    try:
        while True:
            current_position = my_position_tracker.get_current_position()
            print("Distance Traveled - x: {0:.3f} mm, y: {1:.3f} mm, z: {2:.3f} mm".format(current_position.x*1e3,
                                                                                           current_position.y*1e3,
                                                                                           current_position.z*1e3))
            current_orientation = my_position_tracker.get_current_heading()
            print("Heading           - {:.3f} degrees".format(current_orientation))
            #my_position_tracker.set_current_position(Position(x=0.0, y=0.0, z=0.0))
            time.sleep(1)
    except KeyboardInterrupt:
        my_position_tracker.stop()


if __name__ == "__main__":
    main()
