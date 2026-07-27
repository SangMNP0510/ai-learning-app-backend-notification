from datetime import datetime

from pydantic import BaseModel

from app.models.device_platform import DevicePlatform
from typing import Optional
from typing import List
from typing import Dict

class UserNotificationTokenModel(BaseModel):

    token: str

    platform: DevicePlatform

    device_id: Optional[str] = None

    app_version: Optional[str] = None

    updated_at: datetime