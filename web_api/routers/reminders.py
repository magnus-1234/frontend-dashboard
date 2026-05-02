from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
import logging
from datetime import datetime

from cogs.reminder_system import ReminderStorage, TimeParser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reminders", tags=["Reminders"])

class ReminderCreate(BaseModel):
    message: str
    time_str: str
    channel_id: str

@router.get("/{guild_id}")
async def get_reminders(request: Request, guild_id: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        r = await client.get('https://discord.com/api/users/@me', headers={"Authorization": auth_header})
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = r.json()
        user_id = user["id"]

    storage = ReminderStorage()
    reminders = storage.get_user_reminders(user_id, limit=50)
    
    # Filter by guild_id
    server_reminders = [r for r in reminders if str(r.get("guild_id")) == str(guild_id)]
    
    return {"reminders": server_reminders}

@router.post("/{guild_id}")
async def create_reminder(request: Request, guild_id: int, payload: ReminderCreate):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        r = await client.get('https://discord.com/api/users/@me', headers={"Authorization": auth_header})
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = r.json()
        user_id = user["id"]

    # Parse time
    reminder_time, recurring_info = TimeParser.parse_time_string(payload.time_str)
    if not reminder_time:
        raise HTTPException(status_code=400, detail="Invalid time format. Please use a format like 'in 5 minutes' or 'tomorrow at 3pm'.")

    storage = ReminderStorage()
    reminder_id = storage.add_reminder(
        user_id=str(user_id),
        channel_id=str(payload.channel_id),
        guild_id=str(guild_id),
        message=payload.message,
        reminder_time=reminder_time,
        is_recurring=recurring_info.get("is_recurring", False),
        recurrence_type=recurring_info.get("type"),
        recurrence_interval=recurring_info.get("interval"),
        original_pattern=recurring_info.get("pattern")
    )
    
    if reminder_id == -1:
        raise HTTPException(status_code=500, detail="Failed to save reminder.")
        
    return {"status": "success", "reminder_id": reminder_id}

@router.delete("/{guild_id}/{reminder_id}")
async def delete_reminder(request: Request, guild_id: int, reminder_id: int):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        r = await client.get('https://discord.com/api/users/@me', headers={"Authorization": auth_header})
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = r.json()
        user_id = user["id"]

    storage = ReminderStorage()
    success = storage.delete_reminder(reminder_id, str(user_id))
    
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete reminder. It may not exist or does not belong to you.")
