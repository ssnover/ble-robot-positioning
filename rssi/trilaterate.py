import sys
import math
import fileinput
import subprocess
from numpy import matrix, median, mean

def get_position_rssi( b1_x = 0, b1_y = 0, b2_x = 0, b2_y = 0, b3_x = 0, b3_y = 0):
    b1_rssi = 0.0
    b1_rssi_data = []
    b1_detect_cnt = 0.0
    b2_rssi = 0.0
    b2_rssi_data = []
    b2_detect_cnt = 0.0
    b3_rssi = 0.0
    b3_rssi_data = []
    b3_detect_cnt = 0.0
    
    ble_poll_data = subprocess.Popen('./ble_poll.sh', stdout=subprocess.PIPE, shell=True).communicate()[0].decode('utf-8')
    
    for line in ble_poll_data.splitlines():
        linedata = line.split(",")
        beacon_id = int(linedata[0])
        if beacon_id == 1:
            b1_rssi_data.append(float(linedata[1]))
            b1_detect_cnt += 1.0
        elif beacon_id == 2:
            b2_rssi_data.append(float(linedata[1]))
            b2_detect_cnt += 1.0
        elif beacon_id == 3:
            b3_rssi_data.append(float(linedata[1]))
            b3_detect_cnt += 1.0
        else:
            print("beacon ID must be 1, 2, or 3")
            sys.exit()
        
    if not (b1_detect_cnt and b2_detect_cnt and b3_detect_cnt):
        print("polling failed to obtain all 3 beacons")
        sys.exit()
    
    #b1_rssi = math.ceil(b1_rssi/b1_detect_cnt)
    #b2_rssi = math.ceil(b2_rssi/b2_detect_cnt)
    #b3_rssi = math.ceil(b3_rssi/b3_detect_cnt)
    
    b1_rssi_data.sort()
    b2_rssi_data.sort()
    b3_rssi_data.sort()
    
    print(b1_rssi_data)
    print(b2_rssi_data)
    print(b3_rssi_data)
    
    b1_rssi = math.ceil(median(b1_rssi_data))
    b2_rssi = math.ceil(median(b2_rssi_data))
    b3_rssi = math.ceil(median(b3_rssi_data))
    
    #b1_rssi = math.ceil(mean(b1_rssi_data))
    #b2_rssi = math.ceil(mean(b2_rssi_data))
    #b3_rssi = math.ceil(mean(b3_rssi_data))
    
    b1_dist = 0.0314*math.exp(-0.089*b1_rssi)
    b2_dist = 0.0274*math.exp(-0.087*b2_rssi)
    b3_dist = 0.0335*math.exp(-0.083*b3_rssi)
    
    print(b1_rssi)
    print(b2_rssi)
    print(b3_rssi)
    print(b1_dist)
    print(b2_dist)
    print(b3_dist)
    
    a1 = -2*b1_x + 2*b2_x
    b1 = -2*b1_y + 2*b2_y
    c1 = b1_x**2 + b1_y**2 - b1_dist**2 - b2_x**2 - b2_y**2 + b2_dist**2

    a2 = -2*b1_x + 2*b3_x
    b2 = -2*b1_y + 2*b3_y
    c2 = b1_x**2 + b1_y**2 - b1_dist**2 - b3_x**2 - b3_y**2 + b3_dist**2

    a3 = -2*b2_x + 2*b3_x
    b3 = -2*b2_y + 2*b3_y
    c3 = b2_x**2 + b2_y**2 - b2_dist**2 - b3_x**2 - b3_y**2 + b3_dist**2

    if b1 == 0:
            b1 = 0.001
    if b2 == 0:
            b2 = 0.001

    pos_x1 = (-1*c2 + ((c1*b2)/b1))/(-1*(a1*b2)/b1 + a2)
    pos_y1 = (-1*c1 - a1*pos_x1)/b1

    pos_x2 = (-1*c3 + (c1*b3)/b1)/((-1*a1*b3)/b1 + a3)
    pos_y2 = (-1*c1 - a1*pos_x2)/b1

    pos_x3 = (-1*c3 + (c2*b3)/b2)/((-1*a2*b3)/b2 + a3)
    pos_y3 = (-1*c2 - a2*pos_x3)/b2

    pos_x = (pos_x1+pos_x2+pos_x3)/3
    pos_y = (pos_y1+pos_y2+pos_y3)/3
    
    print("")
    print("coordinates:")
    print(pos_x)
    print(pos_y)
    
    #m_a = matrix([[2*(b1_X - b3_X),2*(b1_Y - b3_Y)],[2*(b2_X - b3_X),2*(b2_Y - b3_Y)]])
    #m_b = matrix([[math.pow(b1_X,2) - math.pow(b3_X,2) + math.pow(b1_Y,2) - math.pow(b3_Y,2) + math.pow(b3_dist,2) - math.pow(b1_dist,2)],[math.pow(b2_X,2) - math.pow(b3_X,2) + math.pow(b2_Y,2) - math.pow(b3_Y,2) + math.pow(b2_dist,2) - math.pow(b1_dist,2)]])
    
    #m_xy = (m_a.getT()*m_a).getI()*(m_a.getT()*m_b)
    
    #d1_check = math.pow(m_xy[0][0] - b1_X,2) + math.pow(m_xy[1][0] - b1_Y,2)
    
    #print(m_a)
    #print(m_b)
    #print(m_xy)
    #print(d1_check)

def main():
    if (not(len(sys.argv) == 7)):
        print("must enter three beacon (x,y) coordinates")
        sys.exit()
    b1_X = float(sys.argv[1])
    b1_Y = float(sys.argv[2])
    b2_X = float(sys.argv[3])
    b2_Y = float(sys.argv[4])
    b3_X = float(sys.argv[5])
    b3_Y = float(sys.argv[6])
    
    get_position_rssi(b1_X,b1_Y,b2_X,b2_Y,b3_X,b3_Y)

if __name__ == "__main__":
    main()
