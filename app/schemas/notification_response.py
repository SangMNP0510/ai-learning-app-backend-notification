from datetime import datetime

from pydantic import BaseModel
from typing import Optional
from typing import List
from typing import Dict


class NotificationResponse(BaseModel):

    id: str

    title: str

    body: str

    type: str

    image: Optional[str] = None

    action: Optional[str] = None

    deeplink: Optional[str] = None

    action_data: dict

    is_read: bool

    created_at: datetime