import os

import firebase_admin

from dotenv import load_dotenv

from firebase_admin import credentials

from firebase_admin import firestore


load_dotenv()


cred = credentials.Certificate(

    os.getenv("FIREBASE_CREDENTIAL")

)


if not firebase_admin._apps:

    firebase_admin.initialize_app(
        cred,
    )


db = firestore.client()