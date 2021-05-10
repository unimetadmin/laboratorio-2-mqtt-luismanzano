import paho.mqtt.client as mqtt_client
import random
import time
import numpy as np
import connection as con #ARCHIVO QUE NOS CONECTA CON ELEPHANT
import psycopg2
from threading import Timer
import requests
from datetime import datetime
import json

broker = "127.0.0.1"
port = 1883
topic = "casa/sala/alexa_echo"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

#funcion que anota todo en la db
def insert(value):
    try:
        time = datetime.now()
        connection = con.get_connection()
        cursor = connection.cursor()
        insert_query = """INSERT INTO alexa (weather, time) 
                        VALUES (%s, %s)"""
        cursor.execute(insert_query, (value, time,))
        connection.commit()
        cursor.execute("SELECT * FROM alexa ORDER BY ID DESC LIMIT 1")
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
    msg = "{caracas_weather: " + data + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        insert(data)
    else:
        print(f"Failed to send message to topic {topic}")
             

#ahora la corrida [EL MAIN]

def run():
    client = connect_mqtt()
    count = 0
    while True:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Caracas&appid=5e9b140cd7d802dd03bb13e1b37332bd")
        data = res.json()["main"]["temp"]
       # data = json.load(parse)
        print('parse', data)
        time = Timer(5, client.loop())
        publish(client, str(data))

if __name__ == '__main__':
    #clear()
    run()