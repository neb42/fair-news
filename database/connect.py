import os
import psycopg2

DB_HOST = os.environ['DB_HOST']
DB_DATABASE = os.environ['DB_DATABASE']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

def connect():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection
    