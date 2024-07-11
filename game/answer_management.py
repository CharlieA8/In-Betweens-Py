from session_management import get_db_connection
from answer import Answers
import requests
import json


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
        answers_data = fetch_answers()
        for answer in answers_data:
            conn.execute('''INSERT INTO answers (id, answer1, in_between, answer2, clue1, 
                         clue2, count1, count2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                         ''', (answer['id'], answer['answer1'], answer['in_between'], answer['answer2'], 
                               answer['clue1'], answer['clue2'], answer['count1'], answer['count2']))
        conn.commit()

def get_answers():
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM answers')
        answers_sql = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        answers_list = [dict(zip(column_names, row)) for row in answers_sql]
        
        return Answers(answers_list)

def clear_answers(conn):
    conn.execute('DELETE FROM answers')
    conn.commit()
    print("Answers cleared")

