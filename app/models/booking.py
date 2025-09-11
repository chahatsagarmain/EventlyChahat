from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.db.session import Base
from sqlalchemy.orm import relationship

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    seat_id = Column(Integer , ForeignKey("seats.id" , ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookings",uselist=False)
    seat = relationship("Seat", back_populates="booking",uselist=False)
    event = relationship("Event" , back_populates="bookings",uselist=False)
