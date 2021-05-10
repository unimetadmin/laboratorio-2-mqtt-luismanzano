import psycopg2

def get_connection():
    connection = psycopg2.connect(user="kpktnhlf",
                                  password="RK3i9fEtEYpEmNmjcTlvlX1pVr8WiafO",
                                  host="queenie.db.elephantsql.com",
                                  port="5432",
                                  database="kpktnhlf")
    return connection

def close_connection(connection):
    if connection:
        connection.close()