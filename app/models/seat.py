from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.db.session import Base
from sqlalchemy.orm import relationship

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(Integer , nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(32), nullable=False, default="AVAILABLE")  # AVAILABLE, BOOKED
    extradata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="seats",uselist=False)
    booking = relationship("Booking", back_populates="seat", uselist=False)
