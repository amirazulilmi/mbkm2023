import RPi.GPIO as GPIO
import Adafruit_DHT as dht
from time import time
from time import sleep
from time import struct_time
from serial import Serial
import board
import adafruit_ds3231
import os
import ssl
import json
import paho.mqtt.client as mqtt
import numpy as np
from datetime import datetime

# Set GPIO Pins and i2c

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED_TAKEDATA = 24

DHT = 4
i2c = board.I2C()
rtc = adafruit_ds3231.DS3231(i2c)
GPIO.setup(LED_TAKEDATA, GPIO.OUT)

# MQTT Parameters
host = "mqtt.sandihex.id"
topic = "rpi"
port = 8883

# Set directory
os.chdir("/home/filanmbkm2023/mqtt")
print(ssl.OPENSSL_VERSION)
print(os.getcwd() + "\n")

# MQTT Setup
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected with result=", str(rc))
        else:
            print(f"Not connected {rc}")

    print("Creating Client mqtt ..................")
    client = mqtt.Client()

    print("Connecting to http://" + host + "\n")
    client.tls_set("ca.crt", "client.crt", "client.key", tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(False)
    client.on_connect = on_connect
    client.connect(host, port, 60)
    return client

# Functions to read and store JSON data
def read_json(file_path: str) -> dict:
    """Takes in a json file path and returns its contents"""
    with open(file_path, "r") as json_file:
        content = json.load(json_file)
    return content

def store_json(data: dict, file_path: str):
    """Takes in a python dict and stores it as a .json file"""
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)

def payload():
    try:
        while True:
            #RTC
            print("masuk payload")
            t = rtc.datetime
            t_datetime = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
            serialDevice = "/dev/ttyAMA0"
            ser = Serial(serialDevice, 9600, 8, 'N', 1, timeout=1)
            timeStart = time()
            valueCount = 0
            maxwait = 0.25 # seconds to try for a good reading before quitting
            
            
            #ambil 15 data lalu rata-ratakan
            rawDistance = []
            
            #simpan waktu pengukuran dalam orde detik
            rawTime = []
            ia = 0
            timer = t.tm_sec + 15
            while ia < 200 :
                timeStart = time()

                if t.tm_sec > timer :
                    print("waktu habis")
                    break
                while time() < timeStart + maxwait:
                    if ser.inWaiting():
                        print("serwait")
                        bytesToRead = ser.inWaiting()
                        valueCount += 1
                    if valueCount < 2: # 1st reading may be partial number; throw it out
                        print("masuk valcon")
                        continue
                    testData = ser.read(bytesToRead)
                    if not testData.startswith(b'R'):
                        # data received did not start with R
                        print("masuk valcon 2")
                        continue
                    try:
                        sensorData = testData.decode('utf-8').lstrip('R')
                        print("masuk valcon 3")
                    except UnicodeDecodeError:
                        # data received could not be decoded properly
                        print("error valcon 3")
                        continue
                    try:
                        print("masuk valcon 4")
                        mm = int(sensorData)
                        t = rtc.datetime
                        t_datetime = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                        formatted_timestamp = t_datetime.strftime("%Y%m%d_%H:%M:%S")
                        
                        
                        rawDistance.append(mm)
                        rawTime.append(formatted_timestamp)
                        ia = ia + 1
                        print("serclose")  
                    except ValueError:
                         # value is not a number
                        print("error valcon 4")
                        continue
                    
            print("berhasil ambil data maxboti")
            mean_distance = np.mean(rawDistance)
            print(rawDistance)
            print(rawTime)

            print(f'jarak: {round(mean_distance, 2)} mm')

            #Read Temp and Hum from DHT22
            h,t = dht.read_retry(dht.DHT22, DHT)
            
            #Print Temperature and Humidity on Shell window
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t,h))
            sleep(2)

            # Format timestamp using strftime
            formatted_timestamp = t_datetime.strftime("%Y%m%d_%H:%M:%S")

            # Create data dictionary
            data = {}
            data["waktu"]=formatted_timestamp
            data["jarak"]= round(mean_distance, 2)
            data["temperature"]=t
            data["humidity"]=h
            data["raw_jarak"] = rawDistance[0:len(rawDistance)]
            data["raw_waktu"] = rawTime[0:len(rawTime)]
            print(len(rawDistance))
            print(len(rawTime))
            
            rawDistance.clear()
            rawTime.clear()
            print(data)

            # Store data to JSON file
            store_json(data, f"/home/filanmbkm2023/data/{formatted_timestamp}_data.json")

            return data

    except:
        GPIO.cleanup()

def publish(client, payload):
    payload = str(payload)
    # Publish payload
    sleep(2)
    result = client.publish(topic, payload)
    status = result[0]
    if status == 0:
        print(f"Sending '{payload}' to topic {topic} OK !")
    else:
        print("Sending failed....")

def run():
    
    client = connect_mqtt()
    GPIO.output(LED_TAKEDATA,GPIO.HIGH)
    client.loop_start()
    data = payload()
    publish(client, data)
    GPIO.output(LED_TAKEDATA,GPIO.LOW)

if __name__ == '__main__':
    run()

