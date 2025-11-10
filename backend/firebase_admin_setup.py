import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

load_dotenv()

FIREBASE_SERVICE_ACCOUNT = os.getenv('FIREBASE_SERVICE_ACCOUNT')  # path to service account JSON

firebase_app = None
if FIREBASE_SERVICE_ACCOUNT and os.path.exists(FIREBASE_SERVICE_ACCOUNT):
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
    firebase_app = firebase_admin.initialize_app(cred)
else:
    # No service account provided; firebase_admin will not be initialized.
    firebase_app = None

def is_initialized():
    return firebase_app is not None

# Usage: from firebase_admin_setup import firebase_admin, is_initialized
