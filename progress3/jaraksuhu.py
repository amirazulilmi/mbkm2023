import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import time
import board
import adafruit_ds3231
import os
import ssl
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# Set GPIO Pins and i2c
TRIG = 23
ECHO = 24
maxTime = 0.04
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
DHT = 4
i2c = board.I2C()
rtc = adafruit_ds3231.DS3231(i2c)

# MQTT Parameters
host = "mqtt.sandihex.id"
topic = "rpi"
port = 8883

# Set directory
os.chdir("/home/mbkm2023/mqtt")
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
            t = rtc.datetime
            t_datetime = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

            #Read distance from HCSR04
            GPIO.setup(TRIG, GPIO.OUT)
            GPIO.setup(ECHO, GPIO.IN)
            GPIO.output(TRIG, False)
            time.sleep(0.01)
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            pulse_start = time.time()
            timeout = pulse_start + maxTime
            while GPIO.input(ECHO) == 0 and pulse_start < timeout:
                pulse_start = time.time()
            pulse_end = time.time()
            timeout = pulse_end + maxTime
            while GPIO.input(ECHO) == 1 and pulse_end < timeout:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            print(f'jarak: {round(distance, 2)} cm')

            #Read Temp and Hum from DHT22
            h,t = dht.read_retry(dht.DHT22, DHT)
            #Print Temperature and Humidity on Shell window
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t,h))
            time.sleep(2)

            # Format timestamp using strftime
            formatted_timestamp = t_datetime.strftime("%Y%m%d_%H:%M:%S")

            # Create data dictionary
            data = {}
            data["waktu"]=formatted_timestamp
            data["jarak"]= round(distance, 2)
            data["temperature"]=t
            data["humidity"]=h
            print(data)

            # Store data to JSON file
            store_json(data, f"/home/mbkm2023/data/{formatted_timestamp}_data.json")

            return data

    except:
        GPIO.cleanup()

def publish(client, payload):
    payload = str(payload)
    # Publish payload
    time.sleep(2)
    result = client.publish(topic, payload)
    status = result[0]
    if status == 0:
        print(f"Sending '{payload}' to topic {topic} OK !")
    else:
        print("Sending failed....")

def run():
    client = connect_mqtt()
    client.loop_start()
    data = payload()
    publish(client, data)

if __name__ == '__main__':
    run()
