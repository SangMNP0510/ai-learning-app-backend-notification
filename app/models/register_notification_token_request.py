from pydantic import BaseModel

from app.models.device_platform import DevicePlatform
from typing import Optional
from typing import List
from typing import Dict


class RegisterNotificationTokenRequest(
    BaseModel
):

    token: str

    platform: DevicePlatform

    device_id: Optional[str] = None

    app_version: Optional[str] = None

    language: str = "vi"

    timezone: str = "Asia/Ho_Chi_Minh"