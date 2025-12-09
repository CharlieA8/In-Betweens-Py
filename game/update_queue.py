from game.answer import Answer
from psycopg2.extras import RealDictCursor
from game.db_setup import get_db_connection, release_db_connection
from datetime import datetime, timedelta
from pytz import timezone

def queue_push(data):
    # data param is a dictionary, with keys corresponding to the columns in update_queue table
    conn = get_db_connection()

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the time of insertion
        now = datetime.now(timezone('US/Eastern'))

        cursor.execute('''INSERT INTO update_queue (answer1, in_between, answer2, clue1, clue2, 
                       count1, count2, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                       (data['answer1'], data['in_between'], data['answer2'], data['clue1'], 
                        data['clue2'], data['count1'], data['count2'], now)
        )
    finally:
        release_db_connection(conn)

def queue_pop():
    # This method pops the oldest element in the queue and inserts it into the update table
    # If the queue is empty, it returns false
    conn = get_db_connection()

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the oldest element in the queue
        cursor.execute('''SELECT * FROM update_queue ORDER BY date ASC LIMIT 1''')
        row = cursor.fetchone()

        # Return false if the queue is empty
        if not row:
            print("*Queue* Queue is empty, nothing to pop.")
            return False
        
        # Else if an element was found, insert the row into the update table
        cursor.execute('DELETE FROM update')
        cursor.execute('''INSERT INTO update (answer1, in_between, answer2, clue1, clue2, 
                       count1, count2) VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                       (row['answer1'], row['in_between'], row['answer2'], row['clue1'], 
                        row['clue2'], row['count1'], row['count2'])
        )
        print(f"*Queue* New clue popped from queue & inserted into update: {row['answer1']}, {row['in_between']}, {row['answer2']}.")
        return True
        
    finally:
        release_db_connection(conn)

def visualize_queue():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''SELECT * FROM update_queue ORDER BY date ASC''')
            queue_data = cursor.fetchall()
            return queue_data # returns a list of dictionaries
    finally:
        release_db_connection(conn)

def delete_from_queue(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM update_queue WHERE id = %s', (id,))
        conn.commit()
        print(f"*Queue* Clue manually deleted from the update queue with id: {id}.")
    finally:
        release_db_connection(conn)