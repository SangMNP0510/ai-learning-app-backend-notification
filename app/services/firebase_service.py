from firebase_admin import firestore
from firebase_admin import messaging

from app.config.firebase import db


class FirebaseService:

    @property
    def firestore(self):
        return db

    @property
    def messaging(self):
        return messaging