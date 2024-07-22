from game.session_management import get_db_connection
from game.answer import Answer
import requests


def fetch_answers():
    url = "https://drive.google.com/uc?export=download&id=178X71g7a4-TcbMBQAz6z0r7zTE3v6sXN"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch answers from Google Drive")
    
def update_answers():
    with get_db_connection() as conn:
        clear_answers(conn)
        answers = fetch_answers()
        conn.execute('''INSERT INTO answers (answer1, in_between, answer2, clue1, 
                            clue2, count1, count2) VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (answers['answer1'], answers['in_between'], answers['answer2'], 
                                answers['clue1'], answers['clue2'], answers['count1'], answers['count2']))
        conn.commit()

def get_answers():
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM answers')
        answers_sql = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]
        answers_dict = dict(zip(column_names, answers_sql))

        return Answer(answers_dict)

def clear_answers(conn):
    conn.execute('DELETE FROM answers')
    conn.commit()