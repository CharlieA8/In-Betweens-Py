from flask import Flask
import game.routes
import sys
import os
from game.db_setup import init_db, setup_db_pool, connection_pool
from game.answer_management import update_answers
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE_URL=database_url
    )
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Secure cookie settings
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )

    # Initialize database
    init_db(app.config['DATABASE_URL'])
    setup_db_pool()

    # Load and update answers
    update_answers()

    # Set up routes
    app.register_blueprint(game.routes.bp)   
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(host="0.0.0.0", port=port)
    finally:
        connection_pool.closeall()
