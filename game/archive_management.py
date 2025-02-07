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

def save_archive_completion(user_id, level):
    conn = get_db_connection
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
            INSERT INTO user_data (user_id, last_updated, completed_levels)
            VALUES (%s, %s, ARRAY[%s])
            ON CONFLICT (user_id) DO UPDATE SET
                last_updated = EXCLUDED.last_updated,
                completed_levels = array_append(user_data.completed_levels, %s)
            ''', (user_id, datetime.now(timezone('US/Eastern')), level, level)
            )
        conn.commit()
    finally:
        release_db_connection(conn)
