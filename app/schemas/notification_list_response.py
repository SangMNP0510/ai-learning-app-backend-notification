from app.schemas.notification_response import (
    NotificationResponse,
)

from pydantic import BaseModel
from typing import Optional
from typing import List
from typing import Dict


class NotificationListResponse(BaseModel):

    notifications: list[NotificationResponse]

    has_more: bool

    next_cursor: Optional[str] = None