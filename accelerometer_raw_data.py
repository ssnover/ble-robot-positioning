#!/usr/bin/python3
"""
file: accelerometer_raw_data.py
purpose: Write a series of raw accelerometer data points to a file in order
         to determine what 1g is as a raw measurement.

         Takes in a single argument which is the filename where the data
         should be written to.
"""

import sys
from time import sleep

# Import the LSM303 module.
import Adafruit.Adafruit_LSM303 as Adafruit_LSM303
# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303(accel_address=0x48)


def main():
    """
    Samples sensor at 1 Hz and prints output to a file as x, y, z CSV
    """
    lsm303.set_accelerometer_resolution(
        Adafruit_LSM303.LSM303_ACCEL_1_MG_PER_LSB)
    lsm303.set_accelerometer_datarate(Adafruit_LSM303.LSM303_ACCEL_RATE_50_HZ)

    sleep(1)

    try:
        data_filename = str(sys.argv[1])
    except IndexError:
        data_filename = "data.txt"

    data_file = open(data_filename, "a+")

    try:
        while True:
            (raw_x, raw_y, raw_z) = lsm303.read_accelerometer()
            data_file.write("{}, {}, {}\n".format(raw_x, raw_y, raw_z))
            print("{}, {}, {}".format(raw_x, raw_y, raw_z))
            sleep(1)
    except KeyboardInterrupt:
        data_file.close()
        return


if __name__ == "__main__":
    main()
