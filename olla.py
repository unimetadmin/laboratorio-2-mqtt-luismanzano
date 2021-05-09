import paho.mqtt.client as mqtt_client
import random
import time
import numpy as np
import connection as con #ARCHIVO QUE NOS CONECTA CON ELEPHANT
import psycopg2
from threading import Timer

broker = "127.0.0.1"
port = 1883
topic = "casa/cocina/olla"
client_id = f'python-mqtt-{random.randint(0, 1000)}'



#funcion que anota todo en la db
def insert(value):
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        insert_query = """INSERT INTO olla_temp (temp) 
                        VALUES (%s)"""
        cursor.execute(insert_query, (value,))
        connection.commit()
        cursor.execute("SELECT * FROM olla_temp ORDER BY ID DESC LIMIT 1")
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
def publish(client, temp):
    now_temp = temp
    msg = "{temperature: " + now_temp + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        insert(now_temp)
    else:
        print(f"Failed to send message to topic {topic}")

def boiled(client, msg):
    msg = "{mensaje: " + msg + "}"
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
    count = 0
    while True:
        count += 1
        time = Timer(1.0, client.loop())
        temperature = np.random.uniform(0, 150, None)
        str_temperature = str(temperature)
        publish(client, str_temperature)

        if(temperature > 100):
            client.loop()
            boiled(client, "El agua hirvio")
    #client.loop_start()
    #publish(client)

if __name__ == '__main__':
    #clear()
    run()
