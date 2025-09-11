from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class BookingCreate(BaseModel):
    event_id : int
    status : str
    seat_number : int

class BookingResponse(BaseModel):
    booking_id : int
    event_id : int
    status : str
    seat_number : int
    venue: str
    created_at: datetime