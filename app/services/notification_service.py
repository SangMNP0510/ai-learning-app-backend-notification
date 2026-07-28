import uuid
import logging

from datetime import datetime
from datetime import timezone

from app.models.notification import NotificationModel
from app.models.notification_action import NotificationAction
from app.models.notification_priority import NotificationPriority
from app.models.notification_type import NotificationType

from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_notification_repository import (
    UserNotificationRepository,
)

from app.services.fcm_service import FcmService
from typing import Optional
from typing import List
from typing import Dict
from typing import Optional


logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self):

        self.notification_repository = NotificationRepository()

        self.user_repository = UserNotificationRepository()

        self.fcm = FcmService()

    def _build_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        type: NotificationType,
        priority: NotificationPriority,
        image: Optional[str] = None,
        action: Optional[NotificationAction] = None,
        action_data: Optional[dict] = None,
        expire_at=None,
        deeplink: Optional[str] = None,
    ):

        now = datetime.now(
            timezone.utc,
        )

        return NotificationModel(

            id=str(uuid.uuid4()),

            user_id=user_id,

            title=title,

            body=body,

            type=type,

            priority=priority,

            image=image,

            action=action,

            action_data=action_data or {},

            created_at=now,

            updated_at=now,

            expire_at=expire_at,

            deeplink=deeplink,
        )

    async def create(
        self,
        user_id: str,
        title: str,
        body: str,
        type: NotificationType,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        image: Optional[str] = None,
        action: Optional[NotificationAction] = None,
        deeplink: Optional[str] = None,
        action_data: Optional[dict] = None,
        send_push: bool = True,
        expire_at=None,
    ):

        logger.info(

            "Create notification user=%s type=%s",

            user_id,

            type.value,
        )

        notification = self._build_notification(

            user_id=user_id,

            title=title,

            body=body,

            type=type,

            priority=priority,

            image=image,

            action=action,

            deeplink=deeplink,

            action_data=action_data,

            expire_at=expire_at,
        )

        await self.notification_repository.create(

            user_id,

            notification,
        )

        logger.info(

            "Notification created id=%s",

            notification.id,
        )

        if not send_push:

            return notification

        user = await self.user_repository.get(
            user_id,
        )

        if user is None:

            return notification

        if not user.notification_settings.get(
            "enabled",
            True,
        ):

            return notification

        if not user.devices:

            return notification

        tokens = [

            item.token

            for item in user.devices

            if item.token
        ]

        if not tokens:

            return notification

        fcm_priority = (

            "high"

            if priority in (
                NotificationPriority.HIGH,
                NotificationPriority.URGENT,
            )

            else "normal"
        )

        try:

            response = await self.fcm.send_to_tokens(

                tokens=tokens,

                title=title,

                body=body,

                priority=fcm_priority,

                data={

                    "notification_id": notification.id,

                    "type": notification.type.value,

                    "action": (
                        action.value
                        if action
                        else ""
                    ),

                    "deeplink": deeplink or "",

                },
            )

            if response is None:

                logger.warning(

                    "FCM push failed but notification was saved. "

                    "user_id=%s, notification_id=%s",

                    user_id,

                    notification.id,
                )

        except Exception:

            logger.exception(

                "Failed to send notification push via FCM. "

                "user_id=%s, notification_id=%s",

                user_id,

                notification.id,

            )

        return notification
    
    async def broadcast(
        self,
        title: str,
        body: str,
        type: NotificationType = NotificationType.SYSTEM,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ):
        user_ids = await self.user_repository.get_all_user_ids()

        for uid in user_ids:
            await self.create(
                user_id=uid,
                title=title,
                body=body,
                type=type,
                priority=priority,
                send_push=False,
            )

        await self.fcm.send_to_topic(
            topic="all",
            title=title,
            body=body,
            priority="high",
            data={
                "type": type.value,
            },
        )

    async def get_notifications(
        self,
        user_id: str,
        limit: int = 20,
        start_after=None,
    ):

        return await self.notification_repository.list(

            user_id,

            limit,

            start_after,
        )

    async def unread_count(
        self,
        user_id: str,
    ):

        return await self.notification_repository.unread_count(

            user_id,
        )

    async def mark_read(
        self,
        user_id: str,
        notification_id: str,
    ):

        await self.notification_repository.mark_as_read(

            user_id,

            notification_id,
        )

    async def mark_all_read(
        self,
        user_id: str,
    ):

        await self.notification_repository.mark_all_as_read(

            user_id,
        )

    async def delete(
        self,
        user_id: str,
        notification_id: str,
    ):

        await self.notification_repository.delete(

            user_id,

            notification_id,
        )

    async def delete_all(
        self,
        user_id: str,
    ):

        await self.notification_repository.delete_all(

            user_id,
        )