from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    name: str
    venue: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    capacity: int = Field(..., gt=0)

class EventOut(BaseModel):
    id: int
    name: str
    venue: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    capacity: int

    class Config:
        from_attributes = True

class EventUpdate(BaseModel):
    name: Optional[str] = None
    venue: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    capacity: Optional[int] = None