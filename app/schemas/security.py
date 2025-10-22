from pydantic import BaseModel
from typing import Optional

class SecurityRegister(BaseModel):
    badge_number: str
    pin: str
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
