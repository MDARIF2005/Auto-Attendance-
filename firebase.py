
import pyrebase
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

config = {
    "apiKey": os.getenv("APIKEY"),
    "authDomain": os.getenv("AUTHDOMAIN"),
    "databaseURL": os.getenv("DATABASEURL"),
    "projectId": os.getenv("PROJECTID"),
    "storageBucket": os.getenv("STORAGEBUCKET"),
    "messagingSenderId": os.getenv("MESSAGINGSENDERID"),
    "appId": os.getenv("APPID")
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()