import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, db as firebase_db

load_dotenv()

cred = credentials.Certificate({
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL")
})

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("DATABASE_URL")
    })

auth = firebase_auth
db = firebase_db
