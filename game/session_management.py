import time
import schedule
import threading
import json
from datetime import datetime
from psycopg2.extras import RealDictCursor
import pytz
from game.answer_management import update_answers
from game.db_setup import get_db_connection, release_db_connection
from game.archive_management import filter_old_users

shutdown_flag = threading.Event()

def clear_all_sessions():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM sessions')
        conn.commit()
        print("All sessions cleared")
    finally:
        release_db_connection(conn)

def save_session(session_id, model_data):
    conn = get_db_connection()
    try:
        pauses_json = json.dumps([
            [p[0].isoformat(), p[1].isoformat() if p[1] else None] 
            for p in model_data.pauses
        ])
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO sessions (
                    session_id, start_time, time, pauses, pause_start,
                    clue1, clue2, answer1, inbetween, answer2, correct, response
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                    start_time = EXCLUDED.start_time,
                    time = EXCLUDED.time,
                    pauses = EXCLUDED.pauses,
                    pause_start = EXCLUDED.pause_start,
                    clue1 = EXCLUDED.clue1,
                    clue2 = EXCLUDED.clue2,
                    answer1 = EXCLUDED.answer1,
                    inbetween = EXCLUDED.inbetween,
                    answer2 = EXCLUDED.answer2,
                    correct = EXCLUDED.correct,
                    response = EXCLUDED.response
            ''', (
                session_id, model_data.start_time, 
                model_data.time, pauses_json, model_data.pause_start, 
                model_data.clue1, model_data.clue2, model_data.answer1, model_data.inbetween, 
                model_data.answer2, model_data.correct, model_data.response
            ))
        conn.commit()
    finally:
        release_db_connection(conn)

def load_session(session_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM sessions WHERE session_id = %s', (session_id,))
            session = cursor.fetchone()
        if session:
            pauses_data = session['pauses'] if session['pauses'] else []
            pauses = [
                [datetime.fromisoformat(p[0]), datetime.fromisoformat(p[1]) if p[1] else None]
                for p in pauses_data
            ]
            return {
                'start_time': session['start_time'],
                'time': session['time'],
                'pauses': pauses,
                'pause_start': session['pause_start'],
                'clue1': session['clue1'],
                'clue2': session['clue2'],
                'answer1': session['answer1'],
                'inbetween': session['inbetween'],
                'answer2': session['answer2'],
                'correct': session['correct'],
                'response': session['response']
            }
        return None
    finally:
        release_db_connection(conn)
    
def delete_session(session_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM sessions WHERE session_id = %s', (session_id,))
        conn.commit()
    finally:
        release_db_connection(conn)