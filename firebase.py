
import pyrebase

config = {
    "apiKey": "AIzaSyCfNW6yIbUQP4PAIr2S0CW7bxY8Dz0tt8A",
    "authDomain": "aiattendancesystem-56803.firebaseapp.com",
    "databaseURL": "https://aiattendancesystem-56803.firebaseio.com",
    "projectId": "aiattendancesystem-56803",
    "storageBucket": "aiattendancesystem-56803.appspot.com",
    "messagingSenderId": "1047117067911",
    "appId": "AIAttendanceSystem"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()