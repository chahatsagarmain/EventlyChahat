from pydantic import BaseModel
from typing import Optional

class SeatCreate(BaseModel):
    seat_label: str
    status: Optional[str] = "AVAILABLE"
    extradata: Optional[str] = None

class SeatOut(BaseModel):
    id: int
    event_id: int
    status: str
    seat_number: int
    extradata: Optional[str]

    class Config:
        from_attributes = True
