from pydantic import BaseModel

class BroadcastNotificationRequest(BaseModel):
    title: str
    body: str