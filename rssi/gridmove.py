import sys
import fileinput
import subprocess
from statistics import mean
from scipy import stats

def getGridPosition():
    LLength = 33
    XCoor = [0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5,5]
    YCoor = [1,2,3,4,0,1,2,3,4,5,0,1,2,3,4,5,0,1,2,3,4,5,0,1,2,3,4,5,1,2,3,4,5]
    BMode = [[-37,-58,-57],[-43,-55,-56],[-46,-59,-54],[-54,-60,-54],[-53,-52,-58],[-46,-57,-55],[-53,-69,-58],[-52,-60,-61],[-53,-57,-47],[-53,-58,-46],[-51,-47,-63],[-56,-54,-62],[-53,-52,-56],[-58,-54,-53],[-53,-59,-48],[-58,-61,-48],[-59,-48,-62],[-56,-57,-60],[-57,-52,-63],[-58,-55,-62],[-53,-62,-53],[-52,-61,-52],[-58,-51,-61],[-57,-46,-58],[-58,-54,-61],[-59,-57,-60],[-61,-58,-67],[-56,-67,-55],[-58,-43,-60],[-60,-62,-54],[-61,-56,-51],[-66,-71,-54],[-55,-59,-55]]
    BMean = [[-37.1585,-57.8,-57.416],[-42.8315,-54.2835,-55.028],[-45.1605,-58.312,-53.995],[-53.034,-57.944,-54.8335],[-52.468,-51.935,-57.371],[-45.202,-55.8285,-54.744],[-50.1255,-63.013,-59.3665],[-57.1945,-58.9935,-57.196],[-51.088,-54.8785,-49.5705],[-53.472,-60.156,-45.882],[-49.0285,-46.1275,-64.0275],[-56.5925,-52.792,-60.635],[-51.9525,-50.2775,-55.6885],[-56.95,-52.4855,-52.5175],[-53.6005,-56.5765,-49.3945],[-57.0105,-57.1135,-47.9085],[-58.474,-48.814,-59.9645],[-55.095,-54.4255,-63.5065],[-56.8475,-52.6445,-61.479],[-58.2195,-53.8895,-62.404],[-52.305,-59.841,-53.086],[-54.182,-59.0685,-53.8055],[-56.805,-49.774,-59.101],[-56.545,-47.0985,-55.562],[-58.65,-50.895,-59.534],[-58.1545,-56.608,-58.8165],[-58.587,-55.5245,-67.6875],[-54.939,-61.766,-55.219],[-55.7355,-42.5765,-58.7185],[-58.7185,-60.575,-52.7335],[-61.7295,-56.793,-51.172],[-66.588,-63.9435,-52.6395],[-56.707,-57.331,-53.6865]]
    
    b1_rssi_data = []
    b2_rssi_data = []
    b3_rssi_data = []
    
    #print("Sampling...")
    
    ble_poll_data = subprocess.Popen('./ble_poll.sh 600', stdout=subprocess.PIPE, shell=True).communicate()[0].decode('utf-8')
    
    for line in ble_poll_data.splitlines():
        linedata = line.split(",")
        beacon_id = int(linedata[0])
        if beacon_id == 1:
            b1_rssi_data.append(float(linedata[1]))
        elif beacon_id == 2:
            b2_rssi_data.append(float(linedata[1]))
        elif beacon_id == 3:
            b3_rssi_data.append(float(linedata[1]))
        else:
            #print("beacon ID must be 1, 2, or 3")
            sys.exit()
    
    if not (len(b1_rssi_data) and len(b2_rssi_data) and len(b3_rssi_data)):
        #print("polling failed to obtain all 3 beacons")
        sys.exit()
    
    #print("Done")
    #print("")
    
    rssi_matches = []
    rssi_match_count = 0
    
    rssi_sample_mode = [stats.mode(b1_rssi_data).mode[0],stats.mode(b2_rssi_data).mode[0],stats.mode(b3_rssi_data).mode[0]]
    rssi_sample_mean = [mean(b1_rssi_data),mean(b2_rssi_data),mean(b3_rssi_data)]
    
    #print("RSSI Mode:")
    #print(rssi_sample_mode)
    #print("")
    #print("RSSI Mean:")
    #print(rssi_sample_mean)
    #print("")
    
    position = [-1,-1]
    
    for i in range(0, LLength):
        #rssi_match_count = 0
        #if rssi_sample_mode[0] == BMode[i][0]:
        #    rssi_match_count += 1
        #if rssi_sample_mode[1] == BMode[i][1]:
        #    rssi_match_count += 1
        #if rssi_sample_mode[2] == BMode[i][2]:
        #    rssi_match_count += 1
        if rssi_sample_mode == BMode[i]:
            rssi_matches.append(i)
        #if rssi_match_count == 2:
            #print("Strong match @ (%d,%d)" % (XCoor[i],YCoor[i]))
    
    if len(rssi_matches) == 1:
        #print("One mode match:")
        #print(BMode[rssi_matches[0]])
        position = [XCoor[rssi_matches[0]],YCoor[rssi_matches[0]]]
    elif len(rssi_matches) > 1:
        #print("Multiple mode matches:")
        #print(BMode[rssi_matches[0]])
        match_score = 999
        match_index = -1;
        for i in rssi_matches:
            diff_score = abs(rssi_sample_mean[0] - BMean[i][0]) + abs(rssi_sample_mean[1] - BMean[i][1]) + abs(rssi_sample_mean[2] - BMean[i][2])
            if (diff_score < match_score):
                match_score = diff_score
                match_index = i
        #print("matched mean:")
        #print(BMean[match_index])
        position = [XCoor[match_index],YCoor[match_index]]
    else:
        #print("No mode matches")
        match_score = 999
        match_index = -1;
        for i in range(0, LLength):
            diff_score = abs(rssi_sample_mean[0] - BMean[i][0]) + abs(rssi_sample_mean[1] - BMean[i][1]) + abs(rssi_sample_mean[2] - BMean[i][2])
            if (diff_score < match_score):
                match_score = diff_score
                match_index = i
        #print("matched mean:")
        #print(BMean[match_index])
        position = [XCoor[match_index],YCoor[match_index]]
    #print("")
    #print("Est. Position:")
    #print(position)
    return position[0], position[1]

if __name__ == "__main__":
    curX, curY = getGridPosition()
    print("(%d,%d)" % (curX,curY))
