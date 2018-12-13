import fileinput

measurements = []

for line in fileinput.input():
    measurements.append(int(line))

print(measurements)
