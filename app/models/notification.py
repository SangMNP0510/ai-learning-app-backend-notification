from datetime import datetime
from datetime import timezone

from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from .notification_action import NotificationAction
from .notification_type import NotificationType
from .notification_priority import NotificationPriority


class NotificationModel(BaseModel):

    id: str

    user_id: str

    title: str

    body: str

    type: NotificationType

    priority: NotificationPriority = NotificationPriority.NORMAL

    image: Optional[str] = None

    action: Optional[NotificationAction] = None

    deeplink: Optional[str] = None

    action_data: dict = Field(default_factory=dict)

    is_read: bool = False

    created_at: datetime

    updated_at: datetime

    expire_at: Optional[datetime] = None

    def to_firestore(self):

        return {

            "user_id": self.user_id,

            "title": self.title,

            "body": self.body,

            "type": self.type.value,

            "priority": self.priority.value,

            "image": self.image,

            "action": (
                self.action.value
                if self.action
                else None
            ),

            "deeplink": self.deeplink,

            "action_data": self.action_data,

            "is_read": self.is_read,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "expire_at": self.expire_at,
        }

    @classmethod
    def from_firestore(
        cls,
        data: dict,
    ):

        return cls(

            id=data["id"],

            user_id=data["user_id"],

            title=data["title"],

            body=data["body"],

            type=NotificationType(
                data["type"],
            ),

            priority=NotificationPriority(
                data["priority"],
            ),

            image=data.get(
                "image",
            ),

            action=(
                NotificationAction(
                    data["action"],
                )
                if data.get(
                    "action",
                )
                else None
            ),

            deeplink=data.get(
                "deeplink",
            ),

            action_data=data.get(
                "action_data",
                {},
            ),

            is_read=data.get(
                "is_read",
                False,
            ),

            created_at=data["created_at"],

            updated_at=data["updated_at"],

            expire_at=data.get(
                "expire_at",
            ),
        )