from pydantic import BaseModel, field_validator, Field, model_validator
from datetime import datetime
from typing import Optional, List

class TaskCreateRequest(BaseModel):
    Title: str
    Description: Optional[str] = None
    Priority: Optional[int] = None
    CreatorID: int
    StartTimestamp: datetime
    EndTimestamp: datetime
    RecurringStart: bool = False
    Frequency: Optional[str] = None
    DayNameFrequency: Optional[str] = None
    DayFrequency: Optional[str] = None
    Occurrences: Optional[int] = 30
    GuestIDs: Optional[List[int]] = None

    @model_validator(mode='after')
    def validate_end_after_start(self):
        if self.EndTimestamp <= self.StartTimestamp:
            raise ValueError("EndTimestamp debe ser posterior a StartTimestamp.")
        return self

class TaskResponse(BaseModel):
    message: str
    TaskID: int
    CreationDate: datetime

class Attendee(BaseModel):
    UserID: int
    Username: str

class RecurringResponse(BaseModel):
    RecurringID: int
    Title: str
    Description: Optional[str]
    Priority: Optional[int]
    CreatorID: int
    Frequency: Optional[str]
    DayNameFrequency: Optional[str]
    DayFrequency: Optional[str]

class TaskSearchResponse(BaseModel):
    TaskID: int
    CreatorID: int
    Title: str
    Description: Optional[str]
    Priority: Optional[int]
    RecurringStart: bool
    StartTimestampID: int
    EndTimeStampID: int
    Recurring: Optional[RecurringResponse]
    attendees: List[Attendee]

class TaskUpdateRequest(BaseModel):
    TaskID: int
    Title: str
    Description: Optional[str] = None
    Priority: Optional[int] = None
    RecurringStart: bool
    StartTimestamp: datetime
    EndTimestamp: datetime
    RecurringID: Optional[int] = None
    GuestIDs: Optional[List[int]] = None