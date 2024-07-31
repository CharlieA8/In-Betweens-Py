from game.answer import Answer
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from game.db_setup import get_db_connection, release_db_connection
import pytz

def fetch_answers():
    url = "https://drive.google.com/uc?export=download&id=178X71g7a4-TcbMBQAz6z0r7zTE3v6sXN" 
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch answers from Google Drive")
    
def update_answers(date, conn):
    clear_answers(conn)
    answers = fetch_answers()
    with conn.cursor() as cursor:
        cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (answers['answer1'], answers['in_between'], answers['answer2'], 
                                answers['clue1'], answers['clue2'], answers['count1'], answers['count2'], date))
    conn.commit()

def daily_update():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        todays_date = datetime.now(pytz.timezone('US/Eastern')).date()
        cursor.execute('SELECT COUNT(*) FROM answers')
        count = cursor.fetchone()[0]
        if count == 0:
            update_answers(todays_date, conn)
            print("*Table Empty* Answers updated for " + todays_date.isoformat())
            return
        else:
            cursor.execute('SELECT date FROM answers')
            date = cursor.fetchone()[0].date()
            if date != todays_date:
                update_answers(todays_date, conn)
                print("Answers updated for " + todays_date.isoformat())
                return
            else:
                print("Answers already updated for " + todays_date.isoformat())
                return
    finally:
        release_db_connection(conn)

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