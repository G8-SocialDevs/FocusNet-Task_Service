from fastapi import FastAPI
from app.api import calendar
from app.api import invitations
from app.api import recurring
from app.api import task

app = FastAPI()

app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
app.include_router(recurring.router, prefix="/recurring", tags=["recurring"])
app.include_router(task.router, prefix="/task", tags=["task"])