from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.calendar import Calendar
from app.models.recurring import Recurring
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitations import InvitationCreateRequest, InvitationResponse, InvitationUpdateRequest
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/invitation/send", response_model=InvitationResponse)
async def send_invitation(invite_data: InvitationCreateRequest, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.UserID == invite_data.CreatorID).first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not db.query(User).filter(User.UserID == invite_data.GuestID).first():
        raise HTTPException(status_code=404, detail="Invitado no encontrado")

    if not invite_data.TaskID and not invite_data.RecurringID:
        raise HTTPException(status_code=400, detail="Ingresar TaskID o RecurringID")

    if invite_data.TaskID and not db.query(Task).filter(Task.TaskID == invite_data.TaskID).first():
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    if invite_data.RecurringID and not db.query(Recurring).filter(Recurring.RecurringID == invite_data.RecurringID).first():
        raise HTTPException(status_code=404, detail="Recurrencia no encontrada")

    new_invitation = Invitation(
        CreatorID=invite_data.CreatorID,
        GuestID=invite_data.GuestID,
        TaskID=invite_data.TaskID,
        RecurringID=invite_data.RecurringID,
        Status="Pendiente",
        Date=datetime.utcnow()
    )
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)

    return new_invitation


@router.get("/invitation/list/{user_id}", response_model=List[InvitationResponse])
async def list_invitations(user_id: int, db: Session = Depends(get_db)):
    invitations = db.query(Invitation).filter(Invitation.GuestID == user_id).all()
    return invitations

@router.get("/invitation/list_prop/{user_id}", response_model=List[InvitationResponse])
async def list_invitations_prop(user_id: int, db: Session = Depends(get_db)):
    invitations = db.query(Invitation).filter(Invitation.CreatorID == user_id).all()
    return invitations


@router.put("/invitation/respond/{invitation_id}", response_model=dict)
async def respond_invitation(invitation_id: int, response_data: InvitationUpdateRequest, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.InvitationID == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitación no encontrada")

    invitation.Status = response_data.Status
    db.commit()

    return {
        "message": f"Invitation {response_data.Status.lower()} con éxito",
        "InvitationID": invitation_id
    }


@router.delete("/invitation/delete/{invitation_id}", response_model=dict)
async def delete_invitation(invitation_id: int, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.InvitationID == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitación no encontrada")

    db.delete(invitation)
    db.commit()

    return {"message": "Invitation eliminada satisfactoriamente"}