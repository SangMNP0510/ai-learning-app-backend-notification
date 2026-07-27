from typing import Optional

from fastapi import Header, HTTPException

from app.services.firebase_auth_service import (
    FirebaseAuthService,
)


def get_current_user(
    authorization: Optional[str] = Header(
        default=None
    ),
):

    if authorization is None:

        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    print("========== AUTH HEADER ==========")
    print(authorization)

    id_token = authorization.split(
        " ",
        1,
    )[1]

    print("========== TOKEN LENGTH ==========")
    print(len(id_token))

    try:

        decoded_token = (
            FirebaseAuthService.verify_token(
                id_token
            )
        )

        print("========== DECODED TOKEN ==========")
        print(decoded_token)

        return decoded_token

    except Exception as e:

        print("========== VERIFY ERROR ==========")
        print(e)

        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase ID token",
        )