from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Recurring(Base):
    __tablename__ = "Recurring"

    RecurringID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Title = Column(String(225), nullable=False)
    Description = Column(Text, nullable=True)
    Priority = Column(Integer, nullable=True)
    CreatorID = Column(Integer, ForeignKey("User.UserID"), nullable=False)
    Frequency = Column(String(20), nullable=True)
    DayNameFrequency = Column(String(20), nullable=True)
    DayFrequency = Column(String(20), nullable=True)

    creator = relationship("User", back_populates="recurring_tasks")
    tasks = relationship("Task", back_populates="recurring")
    invitations = relationship("Invitation", back_populates="recurring")
