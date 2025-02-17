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
    RecurringStart: bool = False
    RecurringID: Optional[int] = None

class TaskResponse(BaseModel):
    message: str
    TaskID: int
    CreationDate: datetime

class TaskSearchResponse(BaseModel):
    TaskID: int
    CreatorID: int
    Title: str
    Description: Optional[str]
    Priority: Optional[int]
    RecurringStart: bool
    StartTimestampID: int
    EndTimeStampID: int
    RecurringID: Optional[int]

class TaskUpdateRequest(BaseModel):
    TaskID: int
    Title: str
    Description: Optional[str] = None
    Priority: Optional[int] = None
    RecurringStart: bool
    StartTimestamp: datetime
    EndTimestamp: datetime
    RecurringID: Optional[int] = None