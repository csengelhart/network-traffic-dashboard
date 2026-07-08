"""
database.py

Handles PostgreSQL database connections for the network traffic monitoring project.
"""

import psycopg2

DB_HOST = "127.0.0.1"
DB_NAME = "network_monitor"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_PORT = 5432

def create_db_connection():
    """
       Creates and returns a PostgreSQL database connection.
    """
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port = DB_PORT
    )