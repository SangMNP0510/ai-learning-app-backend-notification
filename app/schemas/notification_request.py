from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from app.models.notification_action import NotificationAction
from app.models.notification_priority import NotificationPriority
from app.models.notification_type import NotificationType
from typing import Optional
from typing import List
from typing import Dict


class NotificationRequest(BaseModel):

    user_id: str

    title: str

    body: str

    type: NotificationType

    priority: NotificationPriority = (
        NotificationPriority.NORMAL
    )

    image: Optional[str] = None

    action: NotificationAction | None = None

    deeplink: Optional[str] = None

    action_data: dict = Field(
        default_factory=dict,
    )

    expire_at: datetime | None = None