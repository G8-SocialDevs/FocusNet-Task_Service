from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InvitationCreateRequest(BaseModel):
    CreatorID: int
    GuestID: int
    TaskID: Optional[int] = None
    RecurringID: Optional[int] = None
    Status: str = Field(default="Pendiente", pattern="^(Pendiente|Aceptada|Rechazada)$")

class InvitationResponse(BaseModel):
    InvitationID: int
    CreatorID: int
    GuestID: int
    TaskID: Optional[int]
    RecurringID: Optional[int]
    Status: str
    Date: datetime

class InvitationUpdateRequest(BaseModel):
    Status: str = Field(pattern="^(Aceptada|Rechazada)$")