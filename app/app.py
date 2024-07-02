from answer import Answers
from flask import Flask
import routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes.bp)   
    
    # Load modelData and store it in app config
    with app.app_context():
        app.config['answers'] = Answers('/Users/charlie/Desktop/Code/In-Betweens-Py/app/static/resources/answers.json')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)