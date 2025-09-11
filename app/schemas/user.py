from pydantic import BaseModel, EmailStr
from typing import Optional , List
from app.schemas.booking import BookingResponse

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_admin: Optional[bool] = False

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_admin: bool

    class Config:
        from_attributes = True

class UserBookingsOut(BaseModel):
    id: int 
    bookings : Optional[List[BookingResponse]]

