from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db, admin_required , get_current_user
from app.schemas.seat import SeatOut
from app.schemas.booking import BookingResponse
from app.crud.seat import list_seats_for_event 
from app.crud.booking import book_seat
from app.crud.event import get_event
from typing import List
from app.core import redis
from app.helper.helper import row_to_dict , rows_to_dict_list


router = APIRouter()

@router.get("/events/{event_id}/seats", response_model=List[SeatOut])
async def list_seats_route(event_id: int, db: AsyncSession = Depends(get_db)):
    key = redis.make_cache_key("event:seats"  , event_id)
    try:
        cached = await redis.get_cache(key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    
    ev = await get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    seats = await list_seats_for_event(db, event_id)
    seats = rows_to_dict_list(seats)
    try:
        await redis.set_cache(key , seats)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    return seats


@router.post("/events/{event_id}/book/{seat_number}")
async def book_seat_route(event_id : int , seat_number : int, db: AsyncSession = Depends(get_db) , current_user = Depends(get_current_user),):
    ev = await get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    ct = 0
    for booking in ev.bookings:
        if booking.status == "BOOKED":
            ct += 1
    if ct == ev.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SEAT CAPACITY FULL")
    ( booked , seat_num ) = await book_seat(db,event_id, seat_number , current_user.id)
    response = BookingResponse(
        booking_id=booked.id,
        event_id=booked.event_id,
        status=booked.status,
        venue=ev.venue,
        seat_number=seat_num,
        created_at=booked.created_at
    )
    try:
        await redis.delete_booking_cache(event_id , current_user.id)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    return response
