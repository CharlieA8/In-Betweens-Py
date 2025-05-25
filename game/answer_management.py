from game.answer import Answer
from psycopg2.extras import RealDictCursor
from game.db_setup import get_db_connection, release_db_connection
from datetime import datetime
from pytz import timezone

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
            cursor.execute('DELETE FROM update')
            cursor.execute('''INSERT INTO update (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ''', (data['answer1'], data['in_between'], data['answer2'], 
                                data['clue1'], data['clue2'], data['count1'], data['count2']))
        conn.commit()
    finally:
        release_db_connection(conn)

def update_answers():
    conn = get_db_connection()
    now = datetime.now(timezone('US/Eastern')).date()
    try:
        cursor = conn.cursor()

        cursor.execute('SELECT date FROM answers LIMIT 1')
        current_data = cursor.fetchone()
        if current_data and current_data[0].date() == now:
            # If the date matches today's date, terminate the update
            print(f"Answers already updated for {now}. Update aborted.")
            return
        
        # Get the new clue from update
        cursor.execute('SELECT * FROM update')
        data = cursor.fetchone()

        # Check to see if it's the same as the current one
        if data:
            cursor.execute('SELECT answer1 FROM answers')
            current_answers = cursor.fetchone()
            if current_answers and current_answers[0] == data[1]:
                # If the answer is the same, terminate the update
                print(f"Answers in update table are unchanged; update aborted.")
                return
        
        # If the answer is different, proceed with the update
        if data:
            clear_answers(conn)
            with conn.cursor() as cursor:
                # Add new clue to the weekly table
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', (data[1], data[2], data[3], data[4], data[5], data[6], data[7], now))
                
                # Add new clue to the archive
                cursor.execute('''INSERT INTO archive (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ''', (data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
                conn.commit()
                print("Answers updated for " + str(now))
        else:
            clear_answers(conn)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', ("GLASS HALF", "FULL", "HOUSE", "What an optimist sees", 
                                "John Stamos hit show", 3, 2, datetime(2000, 1, 1).date()))
                conn.commit()
                print("No new answers found in update table; default values added.")
    finally:
        release_db_connection(conn)

def force_update():
    conn = get_db_connection()
    now = datetime.now(timezone('US/Eastern')).date()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM update')
            data = cursor.fetchone()
            if data:
                clear_answers(conn)
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', (data[1], data[2], data[3], data[4], data[5], data[6], data[7], now))
                conn.commit()
                print("Answers updated by force.")
            else:
                print("No new answers found in update table; no changes made.")
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