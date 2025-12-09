from game.answer import Answer
from psycopg2.extras import RealDictCursor
from game.db_setup import get_db_connection, release_db_connection
from game.update_queue import queue_pop
from datetime import datetime, timedelta
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
    today = datetime.now(timezone('US/Eastern')).date()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the date in the answers table, which is the Saturday before the update
        cursor.execute('SELECT date FROM answers LIMIT 1')
        current_answers_date_row = cursor.fetchone()
        answers_date = current_answers_date_row['date'] if current_answers_date_row else None

        # If today is the same or later than the date in the answers table, do not update
        if answers_date and answers_date.date() >= today:
            return f"*Update* Answers already updated for week of {today}. Update aborted."
        
        # Get the new clue from update and the current answers
        cursor.execute('SELECT * FROM update')
        data = cursor.fetchone()
        cursor.execute('SELECT * FROM answers')
        current_answers = cursor.fetchone()

        # Check to see if update table is the same as the current answers
        if data and current_answers:
            if current_answers['answer1'] == data['answer1']:
                # If the answer is the same, terminate the update
                return f"Answers in update table are unchanged; update aborted."
        
        # If the answer is different, proceed with the update
        if data:
            clear_answers(conn)
            next_saturday = today + timedelta((5 - today.weekday()) % 7)
            output_string = ""

            # Add new clue to the weekly table
            cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (data['answer1'], data['in_between'], data['answer2'], data['clue1'], 
                                    data['clue2'], data['count1'], data['count2'], next_saturday))
            
            # Check if clue is in the archive
            cursor.execute('''SELECT * FROM archive WHERE answer1 = %s AND in_between = %s AND answer2 = %s''', 
                           (data['answer1'], data['in_between'], data['answer2']))
            archive_data = cursor.fetchone()

            # If the clue is not in the archive, insert it
            if not archive_data:
                cursor.execute('''INSERT INTO archive (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ''', (data['answer1'], data['in_between'], data['answer2'], data['clue1'], 
                                data['clue2'], data['count1'], data['count2']))
                archive_string = f"{data['answer1']} {data['in_between']} {data['answer2']}"
                output_string += f"*Update* New clue added to archive: {archive_string} \n"

            conn.commit()
            output_string += "*Update* Answers updated until " + str(next_saturday)

            # Pop the next clue from the queue into the update table
            if queue_pop():
                output_string += "\n*Queue* New clue popped from queue into update table."
            else:
                output_string += "\n*Queue* No new clues in queue to pop."

            return output_string
            
        else:
            clear_answers(conn)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', ("GLASS HALF", "FULL", "HOUSE", "What an optimist sees", 
                                "John Stamos hit show", 3, 2, datetime(2000, 1, 1).date()))
                conn.commit()
                return "*Update* No new answers found in update table; default values added."
    finally:
        release_db_connection(conn)

def force_update():
    conn = get_db_connection()
    today = datetime.now(timezone('US/Eastern')).date()
    next_saturday = today + timedelta((5 - today.weekday()) % 7)

    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM update')
            data = cursor.fetchone()
            if data:
                clear_answers(conn)
                # Add new clue to the weekly table
                cursor.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                                clue2, count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ''', (data[1], data[2], data[3], data[4], data[5], data[6], data[7], next_saturday))
                
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