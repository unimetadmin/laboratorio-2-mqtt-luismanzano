import paho.mqtt.client as mqtt_client
import random
import time
import numpy as np
import connection as con #ARCHIVO QUE NOS CONECTA CON ELEPHANT
import psycopg2
from threading import Timer
import requests
from datetime import datetime, timedelta
import json

broker = "127.0.0.1"
port = 1883
topic = "casa/bano/nivel_tanque"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

#funcion que anota todo en la db
def insert(value):
    try:
        time = datetime.now()
        connection = con.get_connection()
        cursor = connection.cursor()
        insert_query = """INSERT INTO tank (water, time) 
                        VALUES (%s, %s)"""
        cursor.execute(insert_query, (value, time + timedelta(minutes=10),))
        connection.commit()
        cursor.execute("SELECT * FROM tank ORDER BY ID DESC LIMIT 1")
        res = cursor.fetchone()
        print('se inserto: ', res)
        con.close_connection(connection)
    except (Exception, psycopg2.Error) as error:
        print("Error while getting data", error)

#funcion que nos conecta MQTT
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

#publicando mensajes
def publish(client, data):
    msg = "{water: " + data + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        insert(data)
    else:
        print(f"Failed to send message to topic {topic}")


def publish_half(client, data):
    msg = "{message: " + "Ya el tanque va por la mitad" + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def publish_no_water(client, data):
    msg = "{message: " + "Ya el tanque va por la mitad" + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

#ahora la corrida [EL MAIN]

def run():
    client = connect_mqtt()
    water_capacity = 100
    water = 100
    count = 0
    while True:
        count +=1
        time = Timer(0.1, client.loop())
        minus_water = np.random.normal(water*0.10, water*0.05)
        water = water - minus_water
        
        publish(client, str(water))
        
        if(count == 3):
            count = 0
            plus_water = np.random.normal(water_capacity*0.20, water*0.05)
            water = water + plus_water
            client.loop()
            publish(client, str(water))
        
        if( water < (water_capacity/2)):
            publish_half(client)
        elif(water == 0):
            publish_no_water(client)
        

if __name__ == '__main__':
    #clear()
    run()