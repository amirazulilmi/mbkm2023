import paho.mqtt.client as mqtt
import ssl
import os
import json
import re
import inspect
import psycopg2
from psycopg2.extras import Json

os.chdir("/home/mqtt/mict")


def on_connect(client, userdata, flags, rc):
    print("Connected with result =",str(rc))

def on_message(client, userdata, message):
    print("received message ="    , str(message.payload.decode("utf-8")))
    print("message topic="        , message.topic)
    print("message qos="          , message.qos)
    print("message retain flag="  , message.retain)
    payload = str(message.payload.decode("utf-8"))
    data = json.loads(payload)

    #extract data
    device_id = data["device_id"]
    battery = data["system"]['battery']
    solar = data["system"]['solar']
    measure1 = data["rs485"][17]
    measure2 = data["rs485"][19]
    measure3 = data["rs485"][21]
    measure4 = data["rs485"][23]
    a = re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)[\.]?\d(?:[eE][-+]?\d+)?',measure1)
    b = re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)[\.]?\d(?:[eE][-+]?\d+)?',measure2)
    c = re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)[\.]?\d(?:[eE][-+]?\d+)?',measure3)
    d = re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)[\.]?\d(?:[eE][-+]?\d+)?',measure4)
    conduct_mscm = a[1]
    conduct_temp = a[2]
    salinity = a[3]
    do_temp = b[1]
    do_percent = b[2]
    do_mgl = b[3]
    chl_temp = c[1]
    chl_ppb = c[2]
    chl_ftu = c[3]
    dir_1 = d[1]
    dir_2 = d[2]
    dir_3 = d[3]
    dir_4 = d[5]
    dir_5 = d[6]
    dir_6 = d[7]
    dir_7 = d[8]
    dir_8 = d[9]
    dir_9 = d[10]
    dir_10 = d[11]

    conn = psycopg2.connect(
           host="localhost",
           database="buoy_data",
           user="mqtt",
           password="satrep123")
    cur = conn.cursor()

    query = "INSERT INTO sensors(device_id,battery,solar,conduct_mscm,conduct_temp,salinity,do_temp,do_percent,do_mgl,chl_temp,chl_ppb,chl_ftu,dir_1,dir_2,dir_3,dir_4,dir_5,dir_6,dir_7,dir_8,dir_9,dir_10,payload) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data = (device_id,battery,solar,conduct_mscm,conduct_temp,salinity,do_temp,do_percent,do_mgl,chl_temp,chl_ppb,chl_ftu,dir_1,dir_2,dir_3,dir_4,dir_5,dir_6,dir_7,dir_8,dir_9,dir_10,payload,)
    cur.execute(query, data)
    conn.commit()
    print("finish writing.....")
    conn.close()


print(os.getcwd() + "\n")
print("creating new instance")
client = mqtt.Client()

print("Connecting to Broker mqtt.mict.id")

client.tls_set("ca.pem","client.crt","client.key",tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(False)
client.on_connect = on_connect
client.connect("mqtt.mict.id",8883,60)

print("Subscribing to topic | BOUY")
client.on_message = on_message
client.subscribe("buoy")
client.loop_forever()
