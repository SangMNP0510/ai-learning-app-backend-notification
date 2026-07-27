from datetime import datetime
from datetime import timezone

from app.config.firebase import db

from app.models.device_platform import DevicePlatform

from app.models.user_notification import (
    UserNotificationModel,
)

from app.models.user_notification_token import (
    UserNotificationTokenModel,
)
from typing import Optional
from typing import List
from typing import Dict
from typing import Optional


class UserNotificationRepository:

    COLLECTION = "users"

    async def save(
        self,
        model: UserNotificationModel,
    ):

        db.collection(
            self.COLLECTION,
        ).document(
            model.user_id,
        ).set(
            {
                "notification_settings": (
                    model.notification_settings
                ),
                "devices": [
                    item.model_dump(
                        mode="json",
                    )
                    for item in model.devices
                ],
                "device_id": model.device_id,
                "app_version": model.app_version,
                "created_at": model.created_at,
                "updated_at": model.updated_at,
            },
            merge=True,
        )

    async def get(
        self,
        user_id: str,
    ):

        doc = (
            db.collection(
                self.COLLECTION,
            )
            .document(
                user_id,
            )
            .get()
        )

        if not doc.exists:

            return None

        data = doc.to_dict()

        settings = data.get(
            "notification_settings",
            {},
        )

        devices = data.get(
            "devices",
            [],
        )

        created_at = data.get(
            "created_at",
        )

        updated_at = data.get(
            "updated_at",
        )

        now = datetime.now(
            timezone.utc,
        )

        return UserNotificationModel(

            user_id=user_id,

            devices=[
                UserNotificationTokenModel.model_validate(
                    item,
                )
                for item in devices
            ],

            notification_settings={
                "language": settings.get(
                    "language",
                    "vi",
                ),
                "timezone": settings.get(
                    "timezone",
                    "Asia/Ho_Chi_Minh",
                ),
                "enabled": settings.get(
                    "enabled",
                    True,
                ),
            },

            device_id=data.get(
                "device_id",
            ),

            app_version=data.get(
                "app_version",
            ),

            created_at=(
                created_at
                if created_at
                else now
            ),

            updated_at=(
                updated_at
                if updated_at
                else now
            ),
        )

    async def add_token(
        self,
        user_id: str,
        token: str,
        platform: DevicePlatform,
        device_id: Optional[str] = None,
        app_version: Optional[str] = None,
        language: str = "vi",
        timezone_name: str = "Asia/Ho_Chi_Minh",
    ):

        user_ref = (
            db.collection(
                self.COLLECTION,
            )
            .document(
                user_id,
            )
        )

        doc = user_ref.get()

        now = datetime.now(
            timezone.utc,
        )

        if doc.exists:

            data = doc.to_dict()

            settings = data.get(
                "notification_settings",
                {},
            )

            devices_data = data.get(
                "devices",
                [],
            )

            created_at = data.get(
                "created_at",
                now,
            )

            devices = [

                UserNotificationTokenModel.model_validate(
                    item,
                )

                for item in devices_data

                if item.get(
                    "token",
                ) != token
            ]

        else:

            settings = {}

            devices = []

            created_at = now

        devices.append(

            UserNotificationTokenModel(

                token=token,

                platform=platform,

                device_id=device_id,

                app_version=app_version,

                updated_at=now,
            )
        )

        model = UserNotificationModel(

            user_id=user_id,

            devices=devices,

            notification_settings={

                "language": settings.get(
                    "language",
                    language,
                ),

                "timezone": settings.get(
                    "timezone",
                    timezone_name,
                ),

                "enabled": settings.get(
                    "enabled",
                    True,
                ),
            },

            device_id=device_id,

            app_version=app_version,

            created_at=created_at,

            updated_at=now,
        )

        await self.save(
            model,
        )

    async def remove_token(
        self,
        user_id: str,
        token: str,
    ):

        user_ref = (
            db.collection(
                self.COLLECTION,
            )
            .document(
                user_id,
            )
        )

        doc = user_ref.get()

        if not doc.exists:

            return

        data = doc.to_dict()

        settings = data.get(
            "notification_settings",
            {},
        )

        devices_data = data.get(
            "devices",
            [],
        )

        devices = [

            UserNotificationTokenModel.model_validate(
                item,
            )

            for item in devices_data

            if item.get(
                "token",
            ) != token
        ]

        now = datetime.now(
            timezone.utc,
        )

        model = UserNotificationModel(

            user_id=user_id,

            devices=devices,

            notification_settings={

                "language": settings.get(
                    "language",
                    "vi",
                ),

                "timezone": settings.get(
                    "timezone",
                    "Asia/Ho_Chi_Minh",
                ),

                "enabled": settings.get(
                    "enabled",
                    True,
                ),
            },

            device_id=data.get(
                "device_id",
            ),

            app_version=data.get(
                "app_version",
            ),

            created_at=data.get(
                "created_at",
                now,
            ),

            updated_at=now,
        )

        await self.save(
            model,
        )

    async def update_language(
        self,
        user_id: str,
        language: str,
    ):

        await self._update_settings(
            user_id=user_id,
            language=language,
        )

    async def update_timezone(
        self,
        user_id: str,
        timezone_name: str,
    ):

        await self._update_settings(
            user_id=user_id,
            timezone=timezone_name,
        )

    async def enable(
        self,
        user_id: str,
    ):

        await self._update_settings(
            user_id=user_id,
            enabled=True,
        )

    async def disable(
        self,
        user_id: str,
    ):

        await self._update_settings(
            user_id=user_id,
            enabled=False,
        )

    async def _update_settings(
        self,
        user_id: str,
        language: Optional[str] = None,
        timezone: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):

        model = await self.get(
            user_id,
        )

        now = datetime.now(
            timezone.utc,
        )

        if model is None:

            model = UserNotificationModel(

                user_id=user_id,

                created_at=now,

                updated_at=now,
            )

        settings = dict(
            model.notification_settings,
        )

        if language is not None:

            settings["language"] = language

        if timezone is not None:

            settings["timezone"] = timezone

        if enabled is not None:

            settings["enabled"] = enabled

        model.notification_settings = settings

        model.updated_at = now

        await self.save(
            model,
        )