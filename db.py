import urllib.parse
import os
import psycopg2


def database_connection():
    parts = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    username = parts.username
    password = parts.password
    database = parts.path[1:]
    hostname = parts.hostname

    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname
    )
