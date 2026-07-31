from datetime import datetime
from datetime import timezone

from firebase_admin import firestore

from app.config.firebase import db

from app.models.notification import NotificationModel
import uuid


class NotificationRepository:

    USERS = "users"

    NOTIFICATIONS = "notifications"

    def _collection(
        self,
        user_id: str,
    ):
        return (
            db.collection(
                self.USERS,
            )
            .document(
                user_id,
            )
            .collection(
                self.NOTIFICATIONS,
            )
        )
        
    async def ensure_notification_fields(
        self,
        user_id: str,
    ):
        user_ref = (
            db.collection(self.USERS)
            .document(user_id)
        )

        user_doc = user_ref.get()

        if not user_doc.exists:
            return

        data = user_doc.to_dict() or {}

        updates = {}

        if "notification_unread" not in data:
            updates["notification_unread"] = 0

        if "notification_initialized" not in data:
            updates["notification_initialized"] = False
            
        if "notification_total" not in data:
            updates["notification_total"] = 0

        if updates:
            user_ref.set(
                updates,
                merge=True,
            )
            
    async def create_welcome_notification(
        self,
        user_id: str,
    ):
        user_ref = (
            db.collection(self.USERS)
            .document(user_id)
        )

        user_doc = user_ref.get()

        if not user_doc.exists:
            return

        data = user_doc.to_dict() or {}

        if data.get("notification_initialized", False):
            return

        now = datetime.now(timezone.utc)

        doc = (
            user_ref
            .collection(self.NOTIFICATIONS)
            .document()
        )

        doc.set(
            {
                "user_id": user_id,
                "title": "Chào mừng đến với RiStudy",
                "body": "Cảm ơn bạn đã sử dụng ứng dụng.",
                "type": "SYSTEM",
                "priority": "NORMAL",
                "image": None,
                "action": None,
                "action_data": {},
                "deeplink": None,
                "is_read": False,
                "created_at": now,
                "updated_at": now,
                "expire_at": None,
            }
        )

        user_ref.set(
            {
                "notification_unread": firestore.Increment(1),
                "notification_total": firestore.Increment(1),
                "notification_initialized": True,
            },
            merge=True,
        )

    async def create(
        self,
        user_id: str,
        notification: NotificationModel,
    ):

        self._collection(
            user_id,
        ).document(
            notification.id,
        ).set(
            notification.to_firestore(),
        )

        await self.increment_unread(
            user_id,
        )

    async def get(
        self,
        user_id: str,
        notification_id: str,
    ):

        doc = (
            self._collection(
                user_id,
            )
            .document(
                notification_id,
            )
            .get()
        )

        if not doc.exists:

            return None

        data = doc.to_dict()

        data["id"] = doc.id

        notification = NotificationModel.from_firestore(
            data,
        )

        now = datetime.now(
            timezone.utc,
        )

        if (
            notification.expire_at
            and notification.expire_at <= now
        ):

            return None

        return notification

    async def list(
        self,
        user_id: str,
        limit: int = 20,
        start_after=None,
    ):
        await self.ensure_notification_fields(
            user_id,
        )
        
        await self.create_welcome_notification(
            user_id,
        )

        query = (
            self._collection(
                user_id,
            )
            .order_by(
                "created_at",
                direction=firestore.Query.DESCENDING,
            )
            .limit(
                limit,
            )
        )

        if start_after:

            query = query.start_after(
                start_after,
            )

        docs = list(
            query.stream(),
        )

        notifications = []

        now = datetime.now(
            timezone.utc,
        )

        for doc in docs:

            data = doc.to_dict()

            data["id"] = doc.id

            notification = NotificationModel.from_firestore(
                data,
            )

            if (
                notification.expire_at
                and notification.expire_at <= now
            ):

                continue

            notifications.append(
                notification,
            )

        return {
            "notifications": notifications,
            "last_document": (
                docs[-1]
                if docs
                else None
            ),
        }

    async def unread_count(
        self,
        user_id: str,
    ):

        await self.ensure_notification_fields(
            user_id,
        )
        
        await self.create_welcome_notification(
            user_id,
        )

        doc = (
            db.collection(
                self.USERS,
            )
            .document(
                user_id,
            )
            .get()
        )

        data = doc.to_dict()

        return data.get(
            "notification_unread",
            0,
        )

    async def increment_unread(
        self,
        user_id: str,
    ):

        db.collection(
            self.USERS,
        ).document(
            user_id,
        ).set(
            {
                "notification_unread": firestore.Increment(1),
                "notification_total": firestore.Increment(1),
            },
            merge=True,
        )

    async def decrement_unread(
        self,
        user_id: str,
    ):

        ref = (
            db.collection(
                self.USERS,
            )
            .document(
                user_id,
            )
        )

        doc = ref.get()

        if not doc.exists:
            return

        current = doc.to_dict().get(
            "notification_unread",
            0,
        )

        ref.set(
            {
                "notification_unread": max(
                    current - 1,
                    0,
                ),
            },
            merge=True,
        )

    async def mark_as_read(
        self,
        user_id: str,
        notification_id: str,
    ):
        await self.ensure_notification_fields(
            user_id,
        )

        notification = await self.get(
            user_id,
            notification_id,
        )

        if notification is None:

            return

        if notification.is_read:

            return

        self._collection(
            user_id,
        ).document(
            notification_id,
        ).update(
            {
                "is_read": True,
                "updated_at": datetime.now(
                    timezone.utc,
                ),
            },
        )

        await self.decrement_unread(
            user_id,
        )

    async def mark_all_as_read(
        self,
        user_id: str,
    ):
        await self.ensure_notification_fields(
            user_id,
        )

        docs = self._collection(
            user_id,
        ).stream()

        batch = db.batch()

        batch_count = 0

        for doc in docs:

            data = doc.to_dict()

            if data.get(
                "is_read",
                False,
            ):

                continue

            batch.update(
                doc.reference,
                {
                    "is_read": True,
                    "updated_at": datetime.now(
                        timezone.utc,
                    ),
                },
            )

            batch_count += 1

            if batch_count == 500:

                batch.commit()

                batch = db.batch()

                batch_count = 0

        if batch_count:

            batch.commit()

        db.collection(
            self.USERS,
        ).document(
            user_id,
        ).set(
            {
                "notification_unread": 0,
            },
            merge=True,
        )

    async def delete(
        self,
        user_id: str,
        notification_id: str,
    ):
        await self.ensure_notification_fields(
            user_id,
        )

        notification = await self.get(
            user_id,
            notification_id,
        )

        if notification is None:

            return

        self._collection(
            user_id,
        ).document(
            notification_id,
        ).delete()

        if not notification.is_read:

            await self.decrement_unread(
                user_id,
            )

    async def delete_all(
        self,
        user_id: str,
    ):
        await self.ensure_notification_fields(
            user_id,
        )

        docs = self._collection(
            user_id,
        ).stream()

        batch = db.batch()

        batch_count = 0

        for doc in docs:

            batch.delete(
                doc.reference,
            )

            batch_count += 1

            if batch_count == 500:

                batch.commit()

                batch = db.batch()

                batch_count = 0

        if batch_count:

            batch.commit()

        db.collection(
            self.USERS,
        ).document(
            user_id,
        ).set(
            {
                "notification_unread": 0,
            },
            merge=True,
        )