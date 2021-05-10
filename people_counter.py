import paho.mqtt.client as mqtt_client
import random
import time
import numpy as np
import connection as con #ARCHIVO QUE NOS CONECTA CON ELEPHANT
import psycopg2
from threading import Timer

broker = "127.0.0.1"
port = 1883
topic = "casa/sala/contador_personas"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def get_last():
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        query = """SELECT minute FROM people_count ORDER BY ID DESC LIMIT 1;"""
        cursor.execute(query)
        minuto = cursor.fetchone()
        elmin = 0
        con.close_connection(connection)
        print("MINUTO ", minuto[0])
        return minuto[0]

    except (Exception, psycopg2.Error) as error:
        print("Error while clearing", error)



#funcion que anota todo en la db
def insert(value):
    try:
        minute = get_last()
        connection = con.get_connection()
        cursor = connection.cursor()
        insert_query = """INSERT INTO people_count (count, minute) 
                        VALUES (%s, %s)"""
        cursor.execute(insert_query, (value, minute+1,))
        connection.commit()
        cursor.execute("SELECT * FROM people_count ORDER BY ID DESC LIMIT 1")
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
def publish(client, str_people):
    people = str_people
    msg = "{people: " + people + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        insert(people)
    else:
        print(f"Failed to send message to topic {topic}")

def people_alert(client, msg):
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
        time = Timer(0.1, client.loop())
        people = np.random.randint(0, 10, None)
        str_people = str(people)
        publish(client, str_people)

        if(people > 5):
            client.loop()
            people_alert(client, "Epale hermano pero bueno y entonces!? Estamos en pandemia y tu andas de irresponsable")
    #client.loop_start()
    #publish(client)

if __name__ == '__main__':
    #clear()
    run()
