import sqlite3

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                session_id TEXT PRIMARY KEY,
                num_correct INTEGER,
                done BOOLEAN,
                start_time REAL,
                time REAL,
                pauses TEXT,
                clue1 TEXT,
                clue2 TEXT,
                answer1 TEXT,
                inbetween TEXT,
                answer2 TEXT,
                correct BOOLEAN,
                newClue BOOLEAN
            )
        ''')
        conn.commit()

if __name__ == "__main__":
    init_db()