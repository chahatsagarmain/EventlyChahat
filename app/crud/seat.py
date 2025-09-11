from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.seat import Seat
from app.models.booking import Booking
from typing import List, Optional


async def create_seat(db: AsyncSession, seat: Seat) -> Seat:
    db.add(seat)
    await db.commit()
    await db.refresh(seat)
    return seat

async def get_seat(db: AsyncSession, seat_id: int) -> Optional[Seat]:
    q = select(Seat).where(Seat.id == seat_id)
    res = await db.execute(q)
    return res.scalar_one_or_none()

# async def update_seat(db: AsyncSession, seat: Seat):
#     db.add(seat)
#     await db.commit()
#     await db.refresh(seat)
#     return seat

async def list_seats_for_event(db: AsyncSession, event_id: int) -> List[Seat]:
    q = select(Seat).where(Seat.event_id == event_id).order_by(Seat.id.asc())
    res = await db.execute(q)
    return res.scalars().all()
