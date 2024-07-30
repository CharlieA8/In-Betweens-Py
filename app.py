from flask import Flask
import game.routes
from game.session_management import setup_daily_reset, stop_scheduler
import signal
import sys
import os
from game.db_setup import init_db, setup_db_pool, connection_pool
from game.answer_management import daily_update

scheduler_thread = None

def signal_handler(sig, frame):
    if scheduler_thread:
        stop_scheduler()
        scheduler_thread.join()
    sys.exit(0)

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE_URL=database_url
    )

    # Initialize database
    init_db(app.config['DATABASE_URL'])
    setup_db_pool()

    # Load and update answers
    daily_update()

    # Set up routes
    app.register_blueprint(game.routes.bp)   

    # Set up session reset
    setup_daily_reset()

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(host="0.0.0.0", port=port)
    finally:
        connection_pool.closeall()
        if scheduler_thread:
            stop_scheduler()
            scheduler_thread.join()
