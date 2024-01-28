from time import time
from time import sleep
from serial import Serial

serialDevice = "/dev/ttyAMA0" # default for RaspberryPi


def measure(portName):
    ser = Serial(portName, 9600, 8, 'N', 1, timeout=1)
    timeStart = time()
    valueCount = 0
    maxwait = 0.25 # seconds to try for a good reading before quitting

    while time() < timeStart + maxwait:
        if ser.inWaiting():
            bytesToRead = ser.inWaiting()
            valueCount += 1
            if valueCount < 2: # 1st reading may be partial number; throw it out
                continue
            testData = ser.read(bytesToRead)
            if not testData.startswith(b'R'):
                # data received did not start with R
                continue
            try:
                sensorData = testData.decode('utf-8').lstrip('R')
            except UnicodeDecodeError:
                # data received could not be decoded properly
                continue
            try:
                mm = int(sensorData)
            except ValueError:
                # value is not a number
                continue
            ser.close()
            return(mm)

    ser.close()
    raise RuntimeError("Expected serial data not received")




maxRange = 9999  # change for 5m vs 10m sensor
sleepTime = 0.25
data= []

while True:
    times = time()
    mm = measure(serialDevice)
    if mm >= maxRange:
        print("no target")
        sleep(sleepTime)
        continue
    print("distance:", mm)
    data.append(mm)
    sleep(sleepTime)
