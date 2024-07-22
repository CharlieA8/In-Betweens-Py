import sqlite3

def init_db():
    with sqlite3.connect('sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT,
                time REAL,
                pauses TEXT,
                pause_start TEXT,
                clue1 TEXT,
                clue2 TEXT,
                answer1 TEXT,
                inbetween TEXT,
                answer2 TEXT,
                correct BOOLEAN
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer1 TEXT,
                in_between TEXT,
                answer2 TEXT,
                clue1 TEXT,
                clue2 TEXT,
                count1 INTEGER,
                count2 INTEGER
            )
        ''')
        conn.commit()

if __name__ == "__main__":
    init_db()