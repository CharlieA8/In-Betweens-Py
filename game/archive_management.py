from game.answer import Answer
from psycopg2.extras import RealDictCursor
from game.db_setup import get_db_connection, release_db_connection
from datetime import datetime
from pytz import timezone

def get_archive(level):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM archive WHERE id = %s', (level,))
            answers_sql = cursor.fetchone()
            if answers_sql:
                answers_dict = dict(answers_sql)
                return Answer(answers_dict)
            else:
                return None
    finally:
        release_db_connection(conn)

def get_user_progress(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT completed_levels FROM user_data WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
            map = {}
            if result:
                for level in result['completed_levels']:
                    map[level] = True
            return map
    finally:
        release_db_connection(conn)

def save_level_completion(user_id, level):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
            INSERT INTO user_data (user_id, last_updated, completed_levels)
            VALUES (%s, %s, ARRAY[%s])
            ON CONFLICT (user_id) DO UPDATE SET
                last_updated = EXCLUDED.last_updated,
                completed_levels = user_data.completed_levels || %s 
            ''', (user_id, datetime.now(timezone('US/Eastern')), level, [level])
            )
        conn.commit()
    finally:
        release_db_connection(conn)

def upload_archive(data):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''INSERT INTO archive (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ''', (data['answer1'], data['in_between'], data['answer2'], 
                                data['clue1'], data['clue2'], data['count1'], data['count2'])
            )
        conn.commit()
    finally:
        release_db_connection(conn)

def get_levels_array():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM archive')
            count = cursor.fetchone()[0]
            if count == 0:
                return None
            elif count == 1:
                return [1]
            else:
                return list(range(1, count + 1))  # Returns [1, 2, ..., count]
    finally:
        release_db_connection(conn)

def visualize_archive():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM archive')
            archive_data = cursor.fetchall()
            return archive_data # returns a list of dictionaries
    finally:
        release_db_connection(conn)