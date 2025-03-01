from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import calendar as cal
from app.database import get_db
from app.models.task import Task
from app.models.calendar import Calendar
from app.models.recurring import Recurring
from app.models.user import User
from app.models.invitation import Invitation
from app.schemas.task import TaskResponse, TaskSearchResponse, TaskUpdateRequest, TaskCreateRequest, Attendee

router = APIRouter()

@router.post("/task/create_task", response_model=dict)
async def create_task(task_data: TaskCreateRequest, db: Session = Depends(get_db)):
    def create_calendar_entry(date: datetime):
        return Calendar(
            Date=date,
            Year=date.year,
            Month=date.month,
            Day=date.day,
            DayName=date.strftime('%A'),
            Hour=date.hour,
            Minute=date.minute
        )

    duration_minutes = int((task_data.EndTimestamp - task_data.StartTimestamp).total_seconds() / 60)
    recurring_id = None

    guest_ids = task_data.GuestIDs or []
    if guest_ids:
        existing_users = {user.UserID for user in db.query(User).filter(User.UserID.in_(guest_ids)).all()}
        invalid_users = set(guest_ids) - existing_users
        if invalid_users:
            raise HTTPException(status_code=400, detail=f"Usuarios no encontrados: {', '.join(map(str, invalid_users))}")


    def generate_recurrence_dates(start_date: datetime, occurrences: int):
        if task_data.Frequency == "diaria":
            return [start_date + timedelta(days=i) for i in range(occurrences)]
        elif task_data.Frequency == "semanal":
            return [start_date + timedelta(weeks=i) for i in range(occurrences)]
        elif task_data.Frequency == "mensual":
            dates, current_date = [], start_date
            for _ in range(occurrences):
                dates.append(current_date)
                month = current_date.month % 12 + 1
                year = current_date.year + (1 if current_date.month == 12 else 0)
                day = min(current_date.day, cal.monthrange(year, month)[1])
                current_date = datetime(year, month, day, current_date.hour, current_date.minute)
            return dates
        elif task_data.DayNameFrequency:
            weekdays = {"Lu": 0, "Ma": 1, "Mi": 2, "Ju": 3, "Vi": 4, "Sa": 5, "Do": 6}
            target_days = {weekdays[day.strip()] for day in task_data.DayNameFrequency.split(",")}
            dates, current_date = [], start_date
            while len(dates) < occurrences:
                if current_date.weekday() in target_days:
                    dates.append(current_date)
                current_date += timedelta(days=1)
            return dates
        elif task_data.DayFrequency:
            target_days = {int(day.strip()) for day in task_data.DayFrequency.split(",")}
            dates, current_date = [], start_date
            while len(dates) < occurrences:
                if current_date.day in target_days:
                    dates.append(current_date)
                current_date += timedelta(days=1)
            return dates
        return []

    if task_data.RecurringStart and any([task_data.Frequency, task_data.DayNameFrequency, task_data.DayFrequency]):
        new_recurring = Recurring(
            Title=task_data.Title,
            Description=task_data.Description,
            Priority=task_data.Priority,
            CreatorID=task_data.CreatorID,
            Frequency=task_data.Frequency,
            DayNameFrequency=task_data.DayNameFrequency,
            DayFrequency=task_data.DayFrequency
        )
        db.add(new_recurring)
        db.flush() 
        recurring_id = new_recurring.RecurringID

        recurrence_dates = generate_recurrence_dates(task_data.StartTimestamp, task_data.Occurrences)

        calendars = []
        for date in recurrence_dates:
            start_date = date
            end_date = date + (task_data.EndTimestamp - task_data.StartTimestamp)
            calendars.extend([create_calendar_entry(start_date), create_calendar_entry(end_date)])

        db.add_all(calendars)
        db.flush()

        calendar_ids = [calendar.CalendarID for calendar in calendars]
        paired_calendar_ids = [(calendar_ids[i], calendar_ids[i + 1]) for i in range(0, len(calendar_ids), 2)]

        tasks = [
            Task(
                CreatorID=task_data.CreatorID,
                Title=task_data.Title,
                Description=task_data.Description,
                Priority=task_data.Priority,
                StartTimestampID=start_id,
                EndTimeStampID=end_id,
                MinutesDuration=duration_minutes,
                RecurringStart=True,
                RecurringID=recurring_id,
                CreationDate=datetime.utcnow()
            )
            for start_id, end_id in paired_calendar_ids
        ]

        db.add_all(tasks)
        db.commit()

        invitations = [
            Invitation(
                CreatorID=task_data.CreatorID,
                GuestID=guest_id,
                RecurringID=recurring_id,
                Status="Pendiente",
                Date=datetime.utcnow()
            )
            for guest_id in guest_ids
        ]

        db.add_all(invitations)
        db.commit()

        return {
            "message": "Tareas recurrentes creadas con éxito",
            "RecurringID": recurring_id,
            "Tareas_creadas": len(tasks),
            "Invitaciones_creadas": len(invitations)
        }

    else:
        start_calendar = create_calendar_entry(task_data.StartTimestamp)
        end_calendar = create_calendar_entry(task_data.EndTimestamp)
        db.add_all([start_calendar, end_calendar])
        db.flush()

        new_task = Task(
            CreatorID=task_data.CreatorID,
            Title=task_data.Title,
            Description=task_data.Description,
            Priority=task_data.Priority,
            StartTimestampID=start_calendar.CalendarID,
            EndTimeStampID=end_calendar.CalendarID,
            MinutesDuration=duration_minutes,
            RecurringStart=False,
            CreationDate=datetime.utcnow()
        )

        db.add(new_task)
        db.commit()

        invitations = [
            Invitation(
                CreatorID=task_data.CreatorID,
                GuestID=guest_id,
                TaskID=new_task.TaskID,
                Status="Pendiente",
                Date=datetime.utcnow()
            )
            for guest_id in guest_ids
        ]

        db.add_all(invitations)
        db.commit()

        return {
            "message": "Tarea única creada con éxito",
            "TaskID": new_task.TaskID,
            "Invitaciones_creadas": len(invitations)
        }

@router.get("/get_tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@router.get("/search_task/", response_model=TaskSearchResponse)
def search_task(task_id: int, user_id: int, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.TaskID == task_id, Task.CreatorID == user_id).first()

    if not task:
        task = db.query(Task).join(Invitation, Task.TaskID == Invitation.TaskID).filter(
            Invitation.GuestID == user_id,
            Invitation.TaskID == task_id,
            Invitation.Status == "Aceptada"
        ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    creator = db.query(User).filter(User.UserID == task.CreatorID).first()
    attendees = [{"UserID": creator.UserID, "Username": creator.UserName}] if creator else []

    accepted_guests = db.query(User).join(Invitation, User.UserID == Invitation.GuestID).filter(
        Invitation.TaskID == task.TaskID,
        Invitation.Status == "Aceptada"
    ).all()

    attendees += [{"UserID": guest.UserID, "Username": guest.UserName} for guest in accepted_guests]

    return {
        "TaskID": task.TaskID,
        "CreatorID": task.CreatorID,
        "Title": task.Title,
        "Description": task.Description,
        "Priority": task.Priority,
        "StartTimestampID": task.StartTimestampID,
        "EndTimeStampID": task.EndTimeStampID,
        "RecurringStart": task.RecurringStart,
        "RecurringID": task.RecurringID,
        "attendees": attendees
    }

@router.get("/list_user_tasks/{user_id}", response_model=list[TaskSearchResponse])
async def list_user_tasks(user_id: int, db: Session = Depends(get_db)):
    
    created_tasks = db.query(Task).filter(Task.CreatorID == user_id).all()

    accepted_invitations = db.query(Invitation).filter(
        Invitation.GuestID == user_id,
        Invitation.Status == "Aceptada"
    ).all()

    accepted_tasks = db.query(Task).filter(Task.TaskID.in_(
        [inv.TaskID for inv in accepted_invitations if inv.TaskID]
    )).all()

    accepted_recurring_tasks = db.query(Task).filter(Task.RecurringID.in_(
        [inv.RecurringID for inv in accepted_invitations if inv.RecurringID]
    )).all()

    all_tasks = created_tasks + accepted_tasks + accepted_recurring_tasks
    unique_tasks = {task.TaskID: task for task in all_tasks}.values()

    result = []
    for task in unique_tasks:
        creator = db.query(User).filter(User.UserID == task.CreatorID).first()
        attendees = [{"UserID": creator.UserID, "Username": creator.UserName}] if creator else []

        accepted_guests = db.query(User).join(Invitation, User.UserID == Invitation.GuestID).filter(
            Invitation.TaskID == task.TaskID,
            Invitation.Status == "Aceptada"
        ).all()

        attendees += [{"UserID": guest.UserID, "Username": guest.UserName} for guest in accepted_guests]

        result.append({
            "TaskID": task.TaskID,
            "CreatorID": task.CreatorID,
            "Title": task.Title,
            "Description": task.Description,
            "Priority": task.Priority,
            "StartTimestampID": task.StartTimestampID,
            "EndTimeStampID": task.EndTimeStampID,
            "RecurringStart": task.RecurringStart,
            "RecurringID": task.RecurringID,
            "attendees": attendees
        })

    return result

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

    if task.GuestIDs is not None:
        existing_invitations = db.query(Invitation).filter(Invitation.TaskID == task.TaskID).all()
        current_guest_ids = {inv.GuestID for inv in existing_invitations} 
        new_guest_ids = set(task.GuestIDs)

        to_remove = current_guest_ids - new_guest_ids
        to_add = new_guest_ids - current_guest_ids

        if to_remove:
            db.query(Invitation).filter(Invitation.TaskID == task.TaskID, Invitation.GuestID.in_(to_remove)).delete(synchronize_session=False)

        new_invitations = [
            Invitation(
                CreatorID=db_task.CreatorID,
                GuestID=guest_id,
                TaskID=task.TaskID,
                Status="Pendiente",
                Date=datetime.utcnow()
            )
            for guest_id in to_add
        ]

        db.add_all(new_invitations)

    db.commit()
    
    return {"message": "Tarea actualizada satisfactoriamente"}

@router.delete("/delete/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: Session = Depends(get_db)):

    db_task = db.query(Task).filter(Task.TaskID == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    start_calendar_id = db_task.StartTimestampID
    end_calendar_id = db_task.EndTimeStampID

    db.query(Invitation).filter(Invitation.TaskID == task_id).delete(synchronize_session=False)

    db.delete(db_task)

    start_calendar = db.query(Calendar).filter(Calendar.CalendarID == start_calendar_id).first()
    end_calendar = db.query(Calendar).filter(Calendar.CalendarID == end_calendar_id).first()

    if start_calendar:
        linked_tasks = db.query(Task).filter(Task.StartTimestampID == start_calendar_id).count()
        if linked_tasks == 0:
            db.delete(start_calendar)

    if end_calendar:
        linked_tasks = db.query(Task).filter(Task.EndTimeStampID == end_calendar_id).count()
        if linked_tasks == 0:
            db.delete(end_calendar)

    db.commit()

    return {"message": "Tarea e invitaciones eliminadas satisfactoriamente"}