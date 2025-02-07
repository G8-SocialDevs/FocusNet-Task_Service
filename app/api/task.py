from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.task import Task
from app.models.calendar import Calendar
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter()

@router.post("/create_task", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    start_calendar_id, end_calendar_id, duration = None, None, None

    # Insertar StartTimestamp en Calendar si existe
    if task.StartTimestamp:
        start_calendar = Calendar(
            Date=task.StartTimestamp,
            Year=task.StartTimestamp.year,
            Month=task.StartTimestamp.month,
            Day=task.StartTimestamp.day,
            DayName=task.StartTimestamp.strftime("%A"),
            Hour=task.StartTimestamp.hour,
            Minute=task.StartTimestamp.minute
        )
        db.add(start_calendar)
        db.flush()  # Obtener ID antes de commit
        start_calendar_id = start_calendar.CalendarID

    # Insertar EndTimestamp en Calendar si existe
    if task.EndTimestamp:
        end_calendar = Calendar(
            Date=task.EndTimestamp,
            Year=task.EndTimestamp.year,
            Month=task.EndTimestamp.month,
            Day=task.EndTimestamp.day,
            DayName=task.EndTimestamp.strftime("%A"),
            Hour=task.EndTimestamp.hour,
            Minute=task.EndTimestamp.minute
        )
        db.add(end_calendar)
        db.flush()  # Obtener ID antes de commit
        end_calendar_id = end_calendar.CalendarID

    # Calcular duración en minutos si ambas fechas están presentes
    if task.StartTimestamp and task.EndTimestamp:
        duration = (task.EndTimestamp - task.StartTimestamp).total_seconds() / 60

    # Crear la tarea
    new_task = Task(
        CreatorID=task.CreatorID,
        Title=task.Title,
        Description=task.Description,
        Priority=task.Priority,
        StartTimestampID=start_calendar_id,
        EndTimeStampID=end_calendar_id,
        MinutesDuration=duration,
        RecurringStart=task.RecurringStart,
        RecurringID=task.RecurringID,
        CreationDate=datetime.utcnow()
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return TaskResponse(
        message="Tarea registrada con éxito",
        TaskID=new_task.TaskID,
        CreationDate=new_task.CreationDate
    )

@router.get("/get_tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()