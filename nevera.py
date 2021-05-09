import paho.mqtt.client as mqtt_client
import random
import time
import numpy as np
import connection as con #ARCHIVO QUE NOS CONECTA CON ELEPHANT
import psycopg2
from threading import Timer

broker = "127.0.0.1"
port = 1883
topic = "casa/cocina/nevera"
client_id = f'python-mqtt-{random.randint(0, 1000)}'


#funcion que genera la temperatura
def gen_temperature():
    temperature = np.random.normal(10, 2, None)
    str_temperature = str(temperature)
    return str_temperature



#obtener el ultimo minuto para insertar el siguiente
def get_last():
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        query = """SELECT minute FROM nevera_temp ORDER BY ID DESC LIMIT 1;"""
        cursor.execute(query)
        minuto = cursor.fetchone()
        elmin = 0
        con.close_connection(connection)
        print("MINUTO ", minuto[0])
        return minuto[0]

    except (Exception, psycopg2.Error) as error:
        print("Error while clearing", error)

def get_last_ice():
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        query = """SELECT minute FROM nevera_ice ORDER BY ID DESC LIMIT 1;"""
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
    last_minute = get_last()
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        insert_query = """INSERT INTO nevera_temp (temperature, minute) 
                        VALUES (%s, %s)"""
        cursor.execute(insert_query, (value, last_minute+5,))
        connection.commit()
        cursor.execute("SELECT * FROM nevera_temp ORDER BY ID DESC LIMIT 1")
        res = cursor.fetchone()
        print('se inserto: ', res)
        con.close_connection(connection)
    except (Exception, psycopg2.Error) as error:
        print("Error while getting data", error)

def insert_ice(value):
    last_minute = get_last_ice()
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        insert_query = """INSERT INTO nevera_ice (ice, minute) 
                        VALUES (%s, %s)"""
        cursor.execute(insert_query, (value, last_minute+10,))
        connection.commit()
        cursor.execute("SELECT * FROM nevera_ice ORDER BY ID DESC LIMIT 1")
        res = cursor.fetchone()
        print('se inserto: ', res)
        con.close_connection(connection)
    except (Exception, psycopg2.Error) as error:
        print("Error while getting data", error)


#funcion para eliminar lo que hay en la tabla para que se pueda ejecutar muchas veces
def clear():
    try:
        connection = con.get_connection()
        cursor = connection.cursor()
        query = """DELETE FROM nevera_temp"""
        cursor.execute(query)
        connection.commit()
        con.close_connection(connection)
    except (Exception, psycopg2.Error) as error:
        print("Error while clearing", error)

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
    msg_count = 0
    time.sleep(1)
    msg = "{temperature: " + now_temp + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        insert(now_temp)
    else:
        print(f"Failed to send message to topic {topic}")

def publish_ice(client, ice):
    ice = str(ice)
    msg_count = 0
    msg = "{ice: " + ice + "}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
        insert_ice(ice)
    else:
        print(f"Failed to send message to topic {topic}")
             

#ahora la corrida [EL MAIN]

def run():
    client = connect_mqtt()
    count = 0
    while True:
        count += 1
        time = Timer(0.5, client.loop())
        temperature = np.random.normal(10, 2, None)
        str_temperature = str(temperature)
        publish(client, str_temperature)

        if(count == 2):
            count = 0
            ice = np.random.uniform(0, 10, None)
            client.loop()
            publish_ice(client, ice)
    #client.loop_start()
    #publish(client)

if __name__ == '__main__':
    #clear()
    run()
