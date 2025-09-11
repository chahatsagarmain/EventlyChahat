from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event
from app.models.seat import Seat
from app.schemas.event import EventUpdate
from typing import List, Optional
from datetime import datetime

async def create_event(db: AsyncSession, event: Event , creater_id : int) -> Optional[Event]:
    q = select(Event).where(Event.name == event.name)
    found = await db.execute(q)
    if found.scalar_one_or_none():
        return None
    event.created_by = creater_id
    db.add(event)
    await db.flush()

    seats = [
        {"event_id" : event.id , "seat_number" : i + 1}
        for i in range(event.capacity)
    ]

    await db.execute(insert(Seat) , seats)
    await db.commit()
    await db.refresh(event)
    return event

async def get_event(db: AsyncSession, event_id: int) -> Optional[Event]:
    q = select(Event).options(selectinload(Event.bookings)).where(Event.id == event_id)
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def delete_event(db: AsyncSession, event: Event):
    await db.delete(event)
    await db.commit()

async def list_events(db: AsyncSession, name: Optional[str]=None, venue: Optional[str]=None,
                      from_date: Optional[datetime]=None, to_date: Optional[datetime]=None,
                      limit: int=50, offset: int=0) -> List[Event]:
    q = select(Event)
    if name:
        q = q.where(Event.name.ilike(f"%{name}%"))
    if venue:
        q = q.where(Event.venue.ilike(f"%{venue}%"))
    if from_date:
        q = q.where(Event.start_time >= from_date)
    if to_date:
        q = q.where(Event.start_time <= to_date)
    q = q.order_by(Event.start_time.asc()).limit(limit).offset(offset)
    res = await db.execute(q)
    return res.scalars().all()

async def get_bookings(db: AsyncSession , event_id : int):
    q = (
        select(Event).options(selectinload(Event.bookings)).where(Event.id == event_id)
    )

    result = await db.execute(q)
    rows = result.scalar_one_or_none()
    if rows == None:
        raise None
    return rows

async def update_event(event_id: int, event_update: EventUpdate, db: AsyncSession) -> Optional[Event]:
    q = (
        select(Event).where(Event.id == event_id).with_for_update()
    )
    result = await db.execute(q)
    ev = result.scalar_one_or_none()
    
    if ev == None:
        return None
    
    seats_to_add = []
    
    if event_update.capacity != None and event_update.capacity > ev.capacity:
        for i in range(ev.capacity, event_update.capacity):  
            seats_to_add.append({"event_id": event_id, "seat_number": i + 1})
        ev.capacity = event_update.capacity
    elif event_update.capacity != None and event_update.capacity < ev.capacity:
        return None
    if event_update.venue != None:
        ev.venue = event_update.venue
    
    if event_update.name != None:
        ev.name = event_update.name
    
    if event_update.start_time != None and event_update.end_time != None:
        ev.start_time = event_update.start_time
        ev.end_time = event_update.end_time
    
    if event_update.description != None:
        ev.description = event_update.description
    
    if seats_to_add:
        await db.execute(insert(Seat), seats_to_add)
    
    await db.commit()
    await db.refresh(ev)
    return ev