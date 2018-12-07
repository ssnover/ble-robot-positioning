#!/usr/bin/python3

import json
import sys

OUTPUT_FILENAME = "beacon_coordinates.json"

def main():
    """
    Takes in 6 points for the xy coordinates of three BLE beacons in meters.
    """
    if len(sys.argv) != 7:
        print("Usage:")
        print("set_beacon_points.py x0 y0 x1 y1 x2 y2")
    else:
        coordinates = []
        for i in range(1, 7):
            coordinates.append(float(sys.argv[i]))
        json_str = json.dumps(coordinates)
        output_file = open(OUTPUT_FILENAME, 'w')
        output_file.write(json_str)
        output_file.close()
        print(json_str)



if __name__ == "__main__":
    main()
