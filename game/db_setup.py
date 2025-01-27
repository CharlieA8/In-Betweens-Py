import psycopg2
from psycopg2 import pool
import os

connection_pool = None

def init_db(database_url):
    conn = psycopg2.connect(database_url, sslmode='require')
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
            session_id TEXT PRIMARY KEY,
            start_time TIMESTAMP,
            time FLOAT,
            pauses JSONB,
            pause_start TIMESTAMP,
            clue1 TEXT,
            clue2 TEXT,
            answer1 TEXT,
            inbetween TEXT,
            answer2 TEXT,
            correct BOOLEAN,
            response BOOLEAN[]
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id SERIAL PRIMARY KEY,
                answer1 TEXT,
                in_between TEXT,
                answer2 TEXT,
                clue1 TEXT,
                clue2 TEXT,
                count1 INTEGER,
                count2 INTEGER,
                date TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update (
                id SERIAL PRIMARY KEY,
                answer1 TEXT,
                in_between TEXT,
                answer2 TEXT,
                clue1 TEXT,
                clue2 TEXT,
                count1 INTEGER,
                count2 INTEGER
            )
        ''')
        cursor.exectue('''
            CREATE TABLE IF NOT EXISTS archive (
                id SERIAL PRIMARY KEY,
                answer1 TEXT,
                in_between TEXT,
                answer2 TEXT,
                clue1 TEXT,
                clue2 TEXT,
                count1 INTEGER,
                count2 INTEGER,
            )
        ''')
    conn.commit()
    conn.close()

def setup_db_pool():
    global connection_pool
    database_url = os.environ.get('DATABASE_URL')
    connection_pool = pool.SimpleConnectionPool(1, 20, database_url, sslmode='require')

def get_db_connection():
    return connection_pool.getconn()

def release_db_connection(conn):
    connection_pool.putconn(conn)

if __name__ == "__main__":
    init_db()