from enum import Enum


class NotificationType(str, Enum):

    SYSTEM = "SYSTEM"

    FLASHCARD = "FLASHCARD"

    QUIZ = "QUIZ"

    SUMMARY = "SUMMARY"

    DOCUMENT = "DOCUMENT"

    PREMIUM = "PREMIUM"

    PAYMENT = "PAYMENT"

    STREAK = "STREAK"

    RANKING = "RANKING"

    AI = "AI"

    ANNOUNCEMENT = "ANNOUNCEMENT"