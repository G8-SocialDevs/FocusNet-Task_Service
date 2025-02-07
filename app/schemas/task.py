from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    CreatorID: int
    Title: str
    Description: Optional[str] = None
    Priority: Optional[int] = None
    StartTimestamp: Optional[datetime] = None  # Timestamp en entrada
    EndTimestamp: Optional[datetime] = None  # Timestamp en entrada
    RecurringStart: bool | None = False
    RecurringID: Optional[int] = None

class TaskResponse(BaseModel):
    message: str
    TaskID: int
    CreationDate: datetime
