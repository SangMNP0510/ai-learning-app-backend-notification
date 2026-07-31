from fastapi import APIRouter
from fastapi import Depends

from app.api.routes.dependencies import get_current_user

from app.models.common_response import (
    ApiResponse,
)

from app.models.broadcast_notification_request import (
    BroadcastNotificationRequest,
)

from app.models.register_notification_token_request import (
    RegisterNotificationTokenRequest,
)

from app.models.unregister_notification_token_request import (
    UnregisterNotificationTokenRequest,
)

from app.schemas.notification_response import (
    NotificationResponse,
)

from app.services.notification_service import (
    NotificationService,
)

from app.services.user_notification_service import (
    UserNotificationService,
)

from app.schemas.notification_list_response import (
    NotificationListResponse,
)
from typing import Optional
from app.config.firebase import db

from pydantic import BaseModel

from app.models.notification_type import NotificationType
from app.models.notification_priority import NotificationPriority
from app.models.payment_success_notification_request import PaymentSuccessNotificationRequest

from fastapi import Header, HTTPException

import os
from dotenv import load_dotenv

load_dotenv()


def get_notification_service():

    return NotificationService()


router = APIRouter(
    prefix="/notification",
    tags=["Notification"],
)


@router.get("/ping")
async def ping():

    return ApiResponse(

        success=True,

        message="Notification router works",

    )


@router.get(
    "",
    response_model=NotificationListResponse,
)
async def get_notifications(

    limit: int = 10000,

    start_after: Optional[str] = None,

    current_user: dict = Depends(
        get_current_user,
    ),

    service: NotificationService = Depends(
        get_notification_service,
    ),

):

    user_id = current_user["uid"]

    result = await service.get_notifications(

        user_id=user_id,

        limit=limit,

        start_after=start_after,
    )

    notifications = [

        NotificationResponse(

            id=notification.id,

            title=notification.title,

            body=notification.body,

            type=notification.type.value,

            image=notification.image,

            action=(

                notification.action.value

                if notification.action

                else None

            ),

            deeplink=notification.deeplink,

            action_data=notification.action_data,

            is_read=notification.is_read,

            created_at=notification.created_at,

        )

        for notification
        in result["notifications"]

    ]

    return NotificationListResponse(

        notifications=notifications,

        has_more=(
            result["last_document"]
            is not None
        ),

        next_cursor=(
            result["last_document"].id
            if result["last_document"]
            else None
        ),
    )


@router.get("/unread-count")
async def unread_count(

    current_user: dict = Depends(
        get_current_user,
    ),

):

    user_id = current_user["uid"]

    doc = db.collection("users").document(user_id).get()

    data = doc.to_dict() or {}

    return ApiResponse(

        success=True,

        data={

            "unread_count": data.get(
                "notification_unread",
                0,
            ),

            "total_count": data.get(
                "notification_total",
                0,
            ),

        },

    )


@router.patch("/{notification_id}/read")
async def mark_read(

    notification_id: str,

    current_user: dict = Depends(
        get_current_user,
    ),

    service: NotificationService = Depends(
        get_notification_service,
    ),

):
    print("PATCH:", notification_id)

    await service.mark_read(

        current_user["uid"],

        notification_id,

    )

    return ApiResponse(

        success=True,

    )


@router.patch("/read-all")
async def mark_all_read(

    current_user: dict = Depends(
        get_current_user,
    ),

    service: NotificationService = Depends(
        get_notification_service,
    ),

):

    await service.mark_all_read(

        current_user["uid"],

    )

    return ApiResponse(

        success=True,

    )
    
@router.patch("/seen")
async def mark_seen(

    current_user: dict = Depends(
        get_current_user,
    ),

    service: NotificationService = Depends(
        get_notification_service,
    ),

):

    await service.mark_seen(
        current_user["uid"],
    )

    return ApiResponse(
        success=True,
    )


@router.delete("/{notification_id}")
async def delete_notification(

    notification_id: str,

    current_user: dict = Depends(
        get_current_user,
    ),

    service: NotificationService = Depends(
        get_notification_service,
    ),

):
    print("DELETE:", notification_id)

    await service.delete(

        current_user["uid"],

        notification_id,

    )

    return ApiResponse(

        success=True,

    )


@router.delete("")
async def delete_all(

    current_user: dict = Depends(
        get_current_user,
    ),

    service: NotificationService = Depends(
        get_notification_service,
    ),

):

    await service.delete_all(

        current_user["uid"],

    )

    return ApiResponse(

        success=True,

    )


@router.post("/register-token")
async def register_token(

    request: RegisterNotificationTokenRequest,

    current_user: dict = Depends(
        get_current_user,
    ),

    service: UserNotificationService = Depends(
        UserNotificationService,
    ),

):

    await service.register_token(

        user_id=current_user["uid"],

        token=request.token,

        platform=request.platform,

        device_id=request.device_id,

        app_version=request.app_version,

        language=request.language,

        timezone=request.timezone,
    )

    return ApiResponse(

        success=True,

    )


@router.post("/unregister-token")
async def unregister_token(

    request: UnregisterNotificationTokenRequest,

    current_user: dict = Depends(
        get_current_user,
    ),

    service: UserNotificationService = Depends(
        UserNotificationService,
    ),

):

    await service.unregister_token(

        user_id=current_user["uid"],

        token=request.token,
    )

    return ApiResponse(

        success=True,

    )
    
@router.post("/broadcast")
async def broadcast(
    request: BroadcastNotificationRequest,
    service: NotificationService = Depends(
        get_notification_service,
    ),
):

    await service.broadcast(
        title=request.title,
        body=request.body,
    )

    return ApiResponse(
        success=True,
    )
    
@router.post("/internal/payment-success")
async def payment_success_notification(
    request: PaymentSuccessNotificationRequest,
    service: NotificationService = Depends(get_notification_service),
    x_internal_key: str = Header(None),
):
    if x_internal_key != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    package_name = (
        "Pro Monthly"
        if request.package == "pro_month"
        else "Pro Yearly"
    )

    await service.create(
        user_id=request.user_id,
        title="Thanh toán thành công 🎉",
        body=f"Bạn đã nâng cấp thành công gói {package_name}. Chúc bạn học tập hiệu quả cùng RiStudy!",
        type=NotificationType.SYSTEM,
        priority=NotificationPriority.HIGH,
    )

    return ApiResponse(success=True)