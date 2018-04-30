import psycopg2

def connect():
    connection = psycopg2.connect(
        host='',                       # host on which the database is running
        database='',                                                      # name of the database to connect to
        user='',                                                          # username to connect with
        password=''     # password associated with your username
    )
    return connection
