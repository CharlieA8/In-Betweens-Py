import requests
from answer import Answers
from app import create_app

def update_answers():
    app = create_app()
    
    # URL of JSON file on Google Drive
    url = "https://drive.google.com/uc?export=download&id=17mPmTa93JrBDtxFNkv9bMoqJxM9ho6is"

    # Fetch new JSON file
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Create new Answers object
        new_answers = Answers(data)

        # Update app config
        with app.app_context():
            app.config['answers'] = new_answers
            print("Answers updated successfully")
    else:
        print("Failed to fetch new answers file")

if __name__ == "__main__":
    update_answers()