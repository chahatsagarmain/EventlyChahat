from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.session import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) #  use sql function NOW() here 

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="creator", cascade="all, delete-orphan")
