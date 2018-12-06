#!/usr/bin/python3
"""
    file: sensor_fusion.py
    purpose: Simple algorithm to take multiple sensor inputs for the same
             quantity and to use them to make a more accurate estimate.
"""

import threading
import time

import dead_reckoning

class PositionData(object):
    def __init__(self, x, y, error):
        self.x = x
        self.y = y
        self.error = error

class SensorFusion:
    """
    Simple class to manage the periodic sensor fusion reading.
    """

    def __init__(self, frequency=1, ble_positioning=None, dead_reckoner=None):
        self.my_position_estimate = PositionData(x=0.0, y=0.0, error=0.0)
        self.my_frequency = frequency
        self.my_positioning_ble = ble_positioning
        self.my_positioning_imu = dead_reckoner
        self.my_context = threading.Thread(target=self.sensor_fusion_context,
                                           args=(),
                                           name="Sensor Fusion Thread")
        self.my_thread_running = False
        return
    
    def begin(self):
        """
        Sets the flag to allow the sensor_fusion_context to run and starts the 
        thread.
        """
        self.my_thread_running = True
        self.my_context.start()
        return

    def end(self):
        """
        Clears the flag to signal to the sensor_fusion_context to stop running.
        """
        self.my_thread_running = False
        return

    def sensor_fusion_context(self):
        """
        Thread context which periodically gets estimates of position from
        BLE trilateration and dead reckoning and fuses the data into a single
        estimate.
        """
        loop_counter = 0

        while self.my_thread_running:
            time.sleep(1 / self.my_frequency)
            position_estimates = []
            if self.my_positioning_imu:
                (x, y, err) = self.my_positioning_imu.get_position_estimate()
                position_estimates += [PositionData(x, y, err)]

            if self.my_positioning_ble:
                (x, y, err) = self.my_positioning_ble.get_position_estimate()
                position_estimates += [PositionData(x, y, err)]

            if len(position_estimates) == 2:
                self.my_position_estimate = self.fuse(position_estimates[0], position_estimates[1])
            elif len(position_estimates) == 1:
                self.my_position_estimate = position_estimates[0]

            self.my_heading_estimate = self.my_positioning_imu.get_heading_estimate()

    def fuse(self, first, second):
        """
        Takes two estimates of position and interpolates a new position weighted
        by their error estimates.
        """
        return PositionData(first.x + (first.error / (first.error + second.error)) * (second.x - first.x), 
                            first.y + (first.error / (first.error + second.error)) * (second.y - first.y),
                            min(first.error, second.error))

def main():
    """
    Test application for the sensor fusion.
    """
    # start up dead reckoning
    # start up BLE trilateration
    # start sensor fusion context
    # request the current position every second
    # after 1 minute, end
    pass

if __name__ == "__main__":
    main()