from answer import Answers
from flask import Flask
import routes
import requests
from session_management import setup_daily_reset, stop_scheduler
import signal
import sys
from db_setup import init_db

scheduler_thread = None
answers = None

def signal_handler(sig, frame):
    if scheduler_thread:
        stop_scheduler()
        scheduler_thread.join()
    sys.exit(0)

def fetch_answers():
    url = "https://drive.google.com/uc?export=download&id=17mPmTa93JrBDtxFNkv9bMoqJxM9ho6is"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch answers from Google Drive")
    
def update_answers():
    global answers
    answers_data = fetch_answers()
    answers = Answers(answers_data)
    print("Answers updated successfully")

def create_app():
    global answers
    app = Flask(__name__)

    # Initialize database
    init_db()

    # Load and update answers
    update_answers()

    # Set up routes
    main_bp = routes.create_blueprint(answers)
    app.register_blueprint(main_bp)   

    # Set up session reset
    setup_daily_reset()

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    return app

if __name__ == "__main__":
    app = create_app()
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        if scheduler_thread:
            stop_scheduler()
            scheduler_thread.join()