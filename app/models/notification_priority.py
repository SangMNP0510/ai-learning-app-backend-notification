from enum import Enum


class NotificationPriority(str, Enum):

    LOW = "LOW"

    NORMAL = "NORMAL"

    HIGH = "HIGH"

    URGENT = "URGENT"