from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.recurring import Recurring
from app.schemas.recurring import RecurringCreateRequest

router = APIRouter()

@router.post("/set_recurring/{creator_id}", response_model=dict)
async def set_recurring(
    creator_id: int,
    recurring_data: RecurringCreateRequest,
    db: Session = Depends(get_db)
):
    new_recurring = Recurring(
        Title=recurring_data.Title,
        Description=recurring_data.Description,
        Priority=recurring_data.Priority,
        CreatorID=creator_id,
        Frequency=recurring_data.Frequency,
        DayNameFrequency=recurring_data.DayNameFrequency,
        DayFrequency=recurring_data.DayFrequency
    )

    db.add(new_recurring)
    db.commit()
    db.refresh(new_recurring)

    return {
        "message": "Recurrencia establecida",
        "RecurringID": new_recurring.RecurringID
    }