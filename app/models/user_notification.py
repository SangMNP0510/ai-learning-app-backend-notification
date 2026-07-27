from datetime import datetime
from datetime import timezone

from pydantic import BaseModel
from pydantic import Field

from app.models.user_notification_token import (
    UserNotificationTokenModel,
)
from typing import Optional
from typing import List
from typing import Dict

class UserNotificationModel(BaseModel):

    user_id: str

    devices: list[UserNotificationTokenModel] = Field(
        default_factory=list,
    )

    notification_settings: dict = Field(
        default_factory=lambda: {
            "language": "vi",
            "timezone": "Asia/Ho_Chi_Minh",
            "enabled": True,
        },
    )

    device_id: Optional[str] = None

    app_version: Optional[str] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc,
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc,
        ),
    )