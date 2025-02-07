from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Calendar(Base):
    __tablename__ = "Calendar"

    CalendarID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Date = Column(TIMESTAMP, nullable=False)
    Year = Column(Integer, nullable=False)
    Month = Column(Integer, nullable=False)
    Day = Column(Integer, nullable=False)
    DayName = Column(String(10), nullable=False)
    Hour = Column(Integer, nullable=True)
    Minute = Column(Integer, nullable=True)

    tasks_start = relationship("Task", foreign_keys="[Task.StartTimestampID]", back_populates="start_calendar")
    tasks_end = relationship("Task", foreign_keys="[Task.EndTimeStampID]", back_populates="end_calendar")