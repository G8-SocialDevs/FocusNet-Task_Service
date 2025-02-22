from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.calendar import Calendar
from app.models.recurring import Recurring
from app.schemas.recurring import RecurringCreateRequest, RecurringUpdateRequest

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

@router.put("/recurring/update/{recurring_id}", response_model=dict)
async def update_recurring(recurring_id: int, update_data: RecurringUpdateRequest, db: Session = Depends(get_db)):
    recurring = db.query(Recurring).filter(Recurring.RecurringID == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurrencia no encontrada")

    if update_data.Title:
        recurring.Title = update_data.Title
    if update_data.Description:
        recurring.Description = update_data.Description
    if update_data.Priority is not None:
        recurring.Priority = update_data.Priority

    db.commit()

    tasks = db.query(Task).filter(Task.RecurringID == recurring_id).all()
    for task in tasks:
        if update_data.Title:
            task.Title = update_data.Title
        if update_data.Description:
            task.Description = update_data.Description
        if update_data.Priority is not None:
            task.Priority = update_data.Priority

    db.commit()

    return {
        "message": "Recurrencia y tareas actualizadas",
        "RecurringID": recurring_id,
        "Tareas actualizadas": len(tasks)
    }

@router.delete("/recurring/delete/{recurring_id}", response_model=dict)
async def delete_recurring(recurring_id: int, db: Session = Depends(get_db)):
    recurring = db.query(Recurring).filter(Recurring.RecurringID == recurring_id).first()
    if not recurring:
        raise HTTPException(status_code=404, detail="Recurrencia no encontrada")

    tasks = db.query(Task).filter(Task.RecurringID == recurring_id).all()
    calendar_ids = [task.StartTimestampID for task in tasks] + [task.EndTimeStampID for task in tasks]
    db.query(Task).filter(Task.RecurringID == recurring_id).delete()
    db.query(Calendar).filter(Calendar.CalendarID.in_(calendar_ids)).delete()
    db.query(Recurring).filter(Recurring.RecurringID == recurring_id).delete()
    db.commit()

    return {
        "message": "Recurrencia y tareas actualizadas",
        "RecurringID": recurring_id
    }