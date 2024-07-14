from flask import Flask
import game.routes
from game.session_management import setup_daily_reset, stop_scheduler
import signal
import sys
from game.db_setup import init_db
from game.answer_management import update_answers

scheduler_thread = None

def signal_handler(sig, frame):
    if scheduler_thread:
        stop_scheduler()
        scheduler_thread.join()
    sys.exit(0)

def create_app():
    app = Flask(__name__)

    # Initialize database
    init_db()

    # Load and update answers
    update_answers()

    # Set up routes
    app.register_blueprint(game.routes.bp)   

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
