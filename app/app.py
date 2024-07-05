from answer import Answers
from flask import Flask
import routes
from session_management import setup_daily_reset, stop_scheduler
import signal
import sys

scheduler_thread = None

def signal_handler(sig, frame):
    if scheduler_thread:
        stop_scheduler()
        scheduler_thread.join()
    sys.exit(0)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes.bp)   
    
    # Load answers and store it in app config
    with app.app_context():
        app.config['answers'] = Answers('/Users/charlie/Desktop/Code/In-Betweens-Py/app/static/resources/answers.json')

    # Set up session reset
    setup_daily_reset()

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    return app

if __name__ == "__main__":
    app = create_app()
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        if scheduler_thread:
            stop_scheduler()
            scheduler_thread.join()