#!/usr/bin/python3

import json
import sys

OUTPUT_FILENAME = "start_position.json"

def main():
    """
    Takes in x,y point for the xy coordinates of robot in meters and angle relative
    to x-axis of local grid.
    """
    if len(sys.argv) != 4:
        print("Usage:")
        print("set_beacon_points.py x y orientation")
        print(len(sys.argv))
    else:
        coordinates = {'x': float(sys.argv[1]), 'y': float(sys.argv[2]), 'heading': float(sys.argv[3])}
        json_str = json.dumps(coordinates)
        output_file = open(OUTPUT_FILENAME, 'w')
        output_file.write(json_str)
        output_file.close()
        print(json_str)



if __name__ == "__main__":
    main()
