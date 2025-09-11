from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from app.schemas.event import EventCreate, EventOut
from app.api.v1.deps import get_db, admin_required, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event
from app.models.user import User
from app.core import redis
from app.schemas.event import EventUpdate
from app.crud import event
from typing import Optional, List , Annotated
from datetime import datetime
from app.helper.helper import row_to_dict , rows_to_dict_list

router = APIRouter()

@router.post("/", response_model=EventOut, status_code=201, dependencies=[Depends(admin_required)])
async def create_event_route(user: Annotated[User , Depends(get_current_user)], payload: EventCreate, db: AsyncSession = Depends(get_db)):
    if payload.capacity == 0 or (payload.end_time and payload.start_time >= payload.end_time):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Invalid requirements")
    ev = Event(
        name=payload.name,
        venue=payload.venue,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        capacity=payload.capacity
    )
    created = await event.create_event(db, ev , user.id)
    if not created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="ENSURE THE EVENT IS UNIQUE")
    return created

@router.delete("/{event_id}", status_code=204, dependencies=[Depends(admin_required)])
async def delete_event_route(event_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    ev = await event.get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    await event.delete_event(db, ev)
    await redis.delete_event_cache(event_id)
    return True

@router.get("/", response_model=List[EventOut])
async def list_events_route(
    name: Optional[str] = Query(None),
    venue: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(50, gt=0, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    key = redis.make_cache_key("event" , name , venue , from_date , to_date , limit , offset)
    cached = await redis.get_cache(key)
    if cached != None:
        return cached
    events = await event.list_events(db, name=name, venue=venue, from_date=from_date, to_date=to_date, limit=limit, offset=offset)
    events = rows_to_dict_list(events)
    await redis.set_cache(key , events)
    return events

@router.get("/{event_id}")
async def get_event_route(event_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    key = redis.make_cache_key("event" , event_id)
    cached = await redis.get_cache(key)
    print(cached)
    if cached != None:
        return {**cached , "cached" : True}
    ev = await event.get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="EVENT NOT FOUND")
    ev = row_to_dict(ev)
    await redis.set_cache(key,ev)
    return ev

@router.get("/bookings/{event_id}")
async def get_event_bookings(event_id : int = Path(... , gt=0) , db: AsyncSession = Depends(get_db)):
    key = redis.make_cache_key("event:bookings" , event_id)
    cached = await redis.get_cache(key)
    if cached != None:
        return cached
    ev = await event.get_bookings(db , event_id)
    if ev == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="EVENT NOT FOUND")
    bookings = ev.bookings
    valid_bookings = [booking for booking in bookings if booking.status == "BOOKED"]
    ev.bookings = valid_bookings
    ev = row_to_dict(ev)
    await redis.set_cache(key,ev)
    return ev

@router.put("/{event_id}" , dependencies=[Depends(admin_required)])
async def update_event(event_update: EventUpdate , event_id : int = Path(... , gt = 0), db : AsyncSession = Depends(get_db)):
    updated_event = await event.update_event(event_id , event_update , db)
    if updated_event == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="INVALID UPDATED VALUES")
    await redis.delete_event_cache(event_id)
    return updated_event
    