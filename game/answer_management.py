from game.answer import Answer
from psycopg2.extras import RealDictCursor
from game.db_setup import get_db_connection, release_db_connection
from datetime import datetime

def get_answers():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM answers')
            answers_sql = cursor.fetchone()
            if answers_sql:
                answers_dict = dict(answers_sql)
                return Answer(answers_dict)
            else:
                return None
    finally:
        release_db_connection(conn)

def clear_answers(conn):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM answers')
    conn.commit()
    print("Answers cleared")

def upload_answers(data):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO update (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (data['answer1'], data['in_between'], data['answer2'], 
                                data['clue1'], data['clue2'], data['count1'], data['count2'], data['date']))
        conn.commit()
    finally:
        release_db_connection(conn)

def update_answers():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM update')
        data = cursor.fetchone()
        if data:
            clear_answers(conn)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', (data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
                conn.commit()
                cursor.execute('DELETE FROM update')
                conn.commit()
                print("Answers updated for " + data[8])
        else:
            clear_answers(conn)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', ("GLASS HALF", "FULL", "HOUSE", "What an optimist sees", 
                                "John Stamos hit show", 3, 2, datetime.now().date()))
                conn.commit()
                cursor.execute('DELETE FROM update')
                conn.commit()
                print("No new answers found in update table; default values added.")
    finally:
        release_db_connection(conn)

def check_answers():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM update')
            data = cursor.fetchone()
            if data:
                return dict(data)
            else:
                return None
    finally:
        release_db_connection(conn)