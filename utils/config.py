import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    PROJECT_ID = os.getenv('PROJECT_ID', 'momshelper-ai')
    REGION = os.getenv('REGION', 'us-central1')
    FIRESTORE_DATABASE = os.getenv('FIRESTORE_DATABASE', '(default)')
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', './data/chroma_db')
    SQLITE_DB_PATH = './data/momshelper.db'
    
    DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    MEAL_TIMES = {
        'breakfast': '08:00',
        'lunch': '13:00',
        'dinner': '20:00'
    }
    
    FOOD_CATEGORIES = ['vegetables', 'fruits', 'grains', 'dairy', 'protein', 'spices', 'other']
