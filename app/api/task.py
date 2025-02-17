from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.task import Task
from app.models.calendar import Calendar
from app.schemas.task import TaskCreate, TaskResponse, TaskSearchResponse, TaskUpdateRequest

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

@router.get("/search_task/", response_model=TaskSearchResponse)
def search_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.TaskID == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return task

@router.get("/list_user_tasks/{user_id}", response_model=list[TaskSearchResponse])
async def list_user_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.CreatorID == user_id).all()
    
    if not tasks:
        raise HTTPException(status_code=404, detail="No se encontraron tareas para el usuario")
    
    return tasks

@router.put("/update", response_model=dict)
async def update_task(task: TaskUpdateRequest, db: Session = Depends(get_db)):

    db_task = db.query(Task).filter(Task.TaskID == task.TaskID).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarea no ecntontrada")
    
    start_datetime = task.StartTimestamp
    end_datetime = task.EndTimestamp

    new_start_calendar = Calendar(
        Date=start_datetime,
        Year=start_datetime.year,
        Month=start_datetime.month,
        Day=start_datetime.day,
        DayName=start_datetime.strftime('%A'),
        Hour=start_datetime.hour,
        Minute=start_datetime.minute
    )

    new_end_calendar = Calendar(
        Date=end_datetime,
        Year=end_datetime.year,
        Month=end_datetime.month,
        Day=end_datetime.day,
        DayName=end_datetime.strftime('%A'),
        Hour=end_datetime.hour,
        Minute=end_datetime.minute
    )

    db.add(new_start_calendar)
    db.add(new_end_calendar)
    db.commit()

    new_start_calendar_id = new_start_calendar.CalendarID
    new_end_calendar_id = new_end_calendar.CalendarID

    db_task.Title = task.Title
    db_task.Description = task.Description
    db_task.Priority = task.Priority
    db_task.RecurringStart = task.RecurringStart
    db_task.StartTimestampID = new_start_calendar_id
    db_task.EndTimeStampID = new_end_calendar_id
    db_task.RecurringID = task.RecurringID
    
    db.commit()
    db.refresh(db_task)
    
    return {"message": "Tarea actualizada satisfactoriamente"}

@router.delete("/delete/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: Session = Depends(get_db)):

    db_task = db.query(Task).filter(Task.TaskID == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    start_calendar_id = db_task.StartTimestampID
    end_calendar_id = db_task.EndTimeStampID

    db.delete(db_task)

    start_calendar = db.query(Calendar).filter(Calendar.CalendarID == start_calendar_id).first()
    end_calendar = db.query(Calendar).filter(Calendar.CalendarID == end_calendar_id).first()

    if start_calendar and not start_calendar.tasks_start:
        db.delete(start_calendar)

    if end_calendar and not end_calendar.tasks_end:
        db.delete(end_calendar)

    db.commit()

    return {"message": "Tarea eliminada satisfactoriamente"}