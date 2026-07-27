from pydantic import BaseModel


class UnregisterNotificationTokenRequest(
    BaseModel
):

    token: str