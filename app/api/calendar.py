from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.task import Task
from app.models.calendar import Calendar

router = APIRouter()

@router.get("/get_calendar")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Calendar).all()