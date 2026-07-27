import json
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

firebase_credentials = os.getenv(
    "FIREBASE_CREDENTIAL"
)

if firebase_credentials is None:
    raise RuntimeError(
        "FIREBASE_CREDENTIAL is not configured."
    )

# Render
if firebase_credentials.strip().startswith("{"):

    cred = credentials.Certificate(
        json.loads(firebase_credentials)
    )

# Local
else:

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        .parent
    )

    service_account_path = (
        BASE_DIR / firebase_credentials
    )

    if not service_account_path.exists():

        raise FileNotFoundError(
            f"Firebase credential not found: "
            f"{service_account_path}"
        )

    cred = credentials.Certificate(
        str(service_account_path)
    )

if not firebase_admin._apps:

    firebase_admin.initialize_app(
        cred
    )

db = firestore.client()