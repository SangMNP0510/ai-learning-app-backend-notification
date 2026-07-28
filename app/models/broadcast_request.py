from pydantic import BaseModel

class BroadcastRequest(BaseModel):
    title: str
    body: str