from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP
from app.database import Base
from sqlalchemy.orm import relationship

class Invitation(Base):
    __tablename__ = "Invitation"

    InvitationID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CreatorID = Column(Integer, ForeignKey("User.UserID"), nullable=False)
    GuestID = Column(Integer, ForeignKey("User.UserID"), nullable=False)
    TaskID = Column(Integer, ForeignKey("Task.TaskID"), nullable=True)
    RecurringID = Column(Integer, ForeignKey("Recurring.RecurringID"), nullable=True)
    Status = Column(String(20), nullable=False)
    Date = Column(TIMESTAMP, nullable=False)

    creator = relationship("User", foreign_keys=[CreatorID], back_populates="created_invitations")
    guest = relationship("User", foreign_keys=[GuestID], back_populates="received_invitations")
    task = relationship("Task", back_populates="invitations")
    recurring = relationship("Recurring", back_populates="invitations")
