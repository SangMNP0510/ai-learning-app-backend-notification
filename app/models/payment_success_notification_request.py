from pydantic import BaseModel

class PaymentSuccessNotificationRequest(BaseModel):
    user_id: str
    package: str