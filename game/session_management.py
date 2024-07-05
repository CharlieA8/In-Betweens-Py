import time
import schedule
import threading

active_sessions = {}
shutdown_flag = threading.Event()

def clear_all_sessions():
    global active_sessions
    active_sessions.clear()
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

def get_sessions():
    info = []
    for session_id, model_data in active_sessions.items():
        session_info = f"Session ID: {session_id}\n"
        session_info += f"  Num Correct: {model_data.num_correct}\n"
        session_info += f"  Done: {model_data.done}\n"
        session_info += f"  Start Time: {model_data.start_time}\n"
        session_info += f"  Time: {model_data.time}\n"
        session_info += f"  Pauses: {len(model_data.pauses)}\n"
        session_info += f"  Clue 1: {model_data.clue1}\n"
        session_info += f"  Clue 2: {model_data.clue2}\n"
        session_info += f"  Answer 1: {model_data.answer1}\n"
        session_info += f"  In Between: {model_data.inbetween}\n"
        session_info += f"  Answer 2: {model_data.answer2}\n"
        session_info += f"  Correct: {model_data.correct}\n"
        session_info += f"  New Clue: {model_data.newClue}\n"
        info.append(session_info)
    return "\n".join(info)
