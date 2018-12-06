#!/usr/bin/python3

import json
import os.path
import threading

import dead_reckoning
import sensor_fusion

def main():
    """
    Entry point for the positioning robot program.
    """
    # if there's a file with the position, get it and pass it
    if os.path.isfile("starting_position.json"):
        position = open("starting_position.json")
        init_pos_dict = json.loads(position.read())
        start_position = dead_reckoning.Position(x=init_pos_dict['x'], y=init_pos_dict['y'], z=0.0)
    else:
        start_position = dead_reckoning.Position(x=0.0, y=0.0, z=0.0)

    # start up tcp server to take directions

    # start up IMU threads
    my_imu_sampling = dead_reckoning.DeadReckoning(accelerometer_frequency=50, magnetometer_frequency=25, initial_position=start_position)
    my_imu_sampling.begin()

    # start up BLE RSSI measurements

    # start up sensor fusion module
    sensor_fusion.SensorFusion(frequency=1,
                               ble_positioning=None,
                               dead_reckoner=my_imu_sampling)
    # start robot control

    pass

if __name__ == "__main__":
    main()
