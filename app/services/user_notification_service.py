from app.models.device_platform import DevicePlatform

from app.repositories.user_notification_repository import (
    UserNotificationRepository,
)
from typing import Optional
from typing import List
from typing import Dict


class UserNotificationService:

    def __init__(self):

        self.repository = (
            UserNotificationRepository()
        )

    async def register_token(
        self,
        user_id: str,
        token: str,
        platform: DevicePlatform,
        device_id: Optional[str] = None,
        app_version: Optional[str] = None,
        language: str = "vi",
        timezone: str = "Asia/Ho_Chi_Minh",
    ):

        await self.repository.add_token(

            user_id=user_id,

            token=token,

            platform=platform,

            device_id=device_id,

            app_version=app_version,

            language=language,

            timezone_name=timezone,
        )

    async def unregister_token(
        self,
        user_id: str,
        token: str,
    ):

        await self.repository.remove_token(

            user_id=user_id,

            token=token,
        )

    async def update_language(
        self,
        user_id: str,
        language: str,
    ):

        await self.repository.update_language(

            user_id=user_id,

            language=language,
        )

    async def update_timezone(
        self,
        user_id: str,
        timezone: str,
    ):

        await self.repository.update_timezone(

            user_id=user_id,

            timezone_name=timezone,
        )

    async def enable(
        self,
        user_id: str,
    ):

        await self.repository.enable(

            user_id,
        )

    async def disable(
        self,
        user_id: str,
    ):

        await self.repository.disable(

            user_id,
        )

    async def get(
        self,
        user_id: str,
    ):

        return await self.repository.get(
            user_id,
        )