from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from fastapi import status
from app.models import seat , booking , event
from app.schemas.booking import BookingCreate , BookingResponse
from typing import List  , Tuple

async def get_booking(book_id : int , db : AsyncSession):
    q = (
        select(booking.Booking).where(booking.Booking.id == book_id)
    )

    result = await db.execute(q)
    row = result.scalar_one_or_none()
    if row == None:
        return None
    return row

async def book_seat(db: AsyncSession, event_id: int, seat_number : int, user_id: int) -> Tuple[booking.Booking , int]:
    # Lock the seat row
    q = ( 
        select(seat.Seat)
        .where(seat.Seat.seat_number == seat_number, seat.Seat.event_id == event_id)
        .with_for_update()
    )
    result = await db.execute(q)
    seat_res = result.scalar_one_or_none()

    if not seat_res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SEAT NOT FOUND")
    if seat_res.status != "AVAILABLE":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SEAT ALREADY RESERVED")

    # Mark seat as reserved
    seat_res.status = "BOOKED"
    db.add(seat_res)

    # Create booking record
    new_booking = booking.Booking(
        user_id=user_id, 
        event_id=event_id, 
        seat_id=seat_res.id,  
        status="BOOKED"
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(seat_res)
    await db.refresh(new_booking)
    return (
        new_booking , 
        seat_res.seat_number
    )


async def get_user_bookings(user_id : int , db : AsyncSession) -> List[BookingResponse]:
    # inner join events , bookings and table
    q = (
        select(event.Event, seat.Seat, booking.Booking)
        .join(seat.Seat, seat.Seat.event_id == event.Event.id)
        .join(booking.Booking, booking.Booking.seat_id == seat.Seat.id)
        .where(booking.Booking.user_id == user_id)
    )

    result = await db.execute(q)
    rows = result.all()

    bookings : List[BookingResponse] = []
    for event_row , seat_row , booking_row in rows:
        bookings.append(
            BookingResponse(
                booking_id=booking_row.id,
                event_id=event_row.id,
                status=booking_row.status,
                venue=event_row.venue,
                created_at=booking_row.created_at,
                seat_number=seat_row.seat_number
            )
        )

    return bookings

async def cancel_booking(book_id : int , db : AsyncSession) -> bool:
    q = ( select(booking.Booking).where(booking.Booking.id == book_id).with_for_update())
    result = await db.execute(q)
    rows = result.scalar_one_or_none()
    if rows == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="BOOKING NOT FOUND")
    if rows.status == "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="BOOKING NOT BOOKED")
    elif rows.status == "CANCELLED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="BOOKING ALREADY CANCELLED")
    seat_q = ( select(seat.Seat).where(seat.Seat.id == rows.seat_id).with_for_update())
    seat_result = await db.execute(seat_q)
    seat_rows = seat_result.scalar_one_or_none()
    if seat_rows == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="SEAT FOR THE BOOKING NOT FOUND")
    seat_rows.status = "AVAILABLE"
    rows.status = "CANCELLED"
    db.add(seat_rows)
    db.add(rows)
    await db.commit()

    return True