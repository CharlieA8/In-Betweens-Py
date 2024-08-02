import psycopg2
import os

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
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()