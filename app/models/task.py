from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from app.models import recurring, calendar, invitation, user

class Task(Base):
    __tablename__ = "Task"

    TaskID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CreatorID = Column(Integer, ForeignKey("User.UserID"), nullable=False)
    Title = Column(String(225), nullable=False)
    Description = Column(Text, nullable=True)
    Priority = Column(Integer, nullable=True)
    StartTimestampID = Column(Integer, ForeignKey("Calendar.CalendarID"), nullable=False)
    EndTimeStampID = Column(Integer, ForeignKey("Calendar.CalendarID"), nullable=False)
    MinutesDuration = Column(Integer, nullable=True)
    RecurringStart = Column(Boolean, default=False)
    RecurringID = Column(Integer, ForeignKey("Recurring.RecurringID"), nullable=True)
    CreationDate = Column(TIMESTAMP, nullable=False)

    start_calendar = relationship("Calendar", foreign_keys=[StartTimestampID])
    end_calendar = relationship("Calendar", foreign_keys=[EndTimeStampID])
    recurring = relationship("Recurring", back_populates="tasks", lazy="selectin")
    invitations = relationship("Invitation", back_populates="task")
