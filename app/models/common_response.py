from typing import Any

from pydantic import BaseModel
from typing import Optional


class ApiResponse(BaseModel):

    success: bool

    message: Optional[str] = None

    data: Any = None