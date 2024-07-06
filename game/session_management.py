import time
import schedule
import threading
import sqlite3

shutdown_flag = threading.Event()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def clear_all_sessions():
    with get_db_connection() as conn:
        conn.execute('DELETE FROM active_sessions')
        conn.commit()
    print("All sessions cleared")

def run_scheduler():
    while not shutdown_flag.is_set():
        schedule.run_pending()
        time.sleep(1)

def setup_daily_reset():
    schedule.every().day.at("00:00").do(clear_all_sessions)
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    return scheduler_thread

def stop_scheduler():
    shutdown_flag.set()

def save_session(session_id, model_data):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO active_sessions (
                session_id, num_correct, done, start_time, time, pauses, 
                clue1, clue2, answer1, inbetween, answer2, correct, newClue
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, model_data.num_correct, model_data.done, model_data.start_time,
            model_data.time, ','.join(map(str, model_data.pauses)), model_data.clue1,
            model_data.clue2, model_data.answer1, model_data.inbetween, model_data.answer2,
            model_data.correct, model_data.newClue
        ))
        conn.commit()

def load_session(session_id):
    with get_db_connection() as conn:
        session = conn.execute('SELECT * FROM active_sessions WHERE session_id = ?', (session_id,)).fetchone()
        if session:
            return dict(session)
        return None
    
def delete_session(session_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM active_sessions WHERE session_id = ?', (session_id,))
        conn.commit()

def get_all_sessions():
    with get_db_connection() as conn:
        sessions = conn.execute('SELECT * FROM active_sessions').fetchall()
        info = []
        for session in sessions:
            session_info = f"Session ID: {session['session_id']}\n"
            session_info += f"  Num Correct: {session['num_correct']}\n"
            session_info += f"  Done: {session['done']}\n"
            session_info += f"  Start Time: {session['start_time']}\n"
            session_info += f"  Time: {session['time']}\n"
            session_info += f"  Pauses: {session['pauses']}\n"
            session_info += f"  Clue 1: {session['clue1']}\n"
            session_info += f"  Clue 2: {session['clue2']}\n"
            session_info += f"  Answer 1: {session['answer1']}\n"
            session_info += f"  In Between: {session['inbetween']}\n"
            session_info += f"  Answer 2: {session['answer2']}\n"
            session_info += f"  Correct: {session['correct']}\n"
            session_info += f"  New Clue: {session['newClue']}\n"
            info.append(session_info)
        return "\n".join(info)