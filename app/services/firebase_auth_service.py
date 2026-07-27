from fastapi import HTTPException
from firebase_admin import auth

from app.utils.logger import logger


class FirebaseAuthService:

    @staticmethod
    def verify_token(
        id_token: str,
    ):

        if not id_token:

            raise HTTPException(
                status_code=401,
                detail="Firebase token is empty",
            )

        print("========== TOKEN LENGTH ==========")
        print(len(id_token))

        try:

            decoded_token = auth.verify_id_token(
                id_token
            )

            print("========== DECODED ==========")
            print(decoded_token)

            return decoded_token

        except Exception as e:

            logger.exception(
                "Verify Firebase token failed"
            )

            print("========== REAL ERROR ==========")
            print(type(e))
            print(e)

            raise HTTPException(
                status_code=401,
                detail="Invalid Firebase token",
            )