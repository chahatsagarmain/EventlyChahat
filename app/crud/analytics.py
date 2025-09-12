from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking
from app.models.event import Event
from app.models.user import User
from app.models.seat import Seat
from typing import List, Dict, Any
from datetime import datetime, timedelta

async def get_total_bookings(db: AsyncSession) -> int:
    """Get total number of bookings"""
    q = select(func.count(Booking.id)).where(Booking.status == "BOOKED")
    result = await db.execute(q)
    return result.scalar() or 0

async def get_total_events(db: AsyncSession) -> int:
    """Get total number of events"""
    q = select(func.count(Event.id))
    result = await db.execute(q)
    return result.scalar() or 0

async def get_total_users(db: AsyncSession) -> int:
    """Get total number of users"""
    q = select(func.count(User.id))
    result = await db.execute(q)
    return result.scalar() or 0

async def get_most_popular_events(db: AsyncSession, limit: int = 5) -> List[Dict[str, Any]]:
    """Get most popular events by booking count"""
    q = (
        select(
            Event.id,
            Event.name,
            Event.venue,
            Event.capacity,
            func.count(Booking.id).label("total_bookings")
        )
        .join(Booking, Booking.event_id == Event.id)
        .where(Booking.status == "BOOKED")
        .group_by(Event.id, Event.name, Event.venue, Event.capacity)
        .order_by(desc("total_bookings"))
        .limit(limit)
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    popular_events = []
    for row in rows:
        utilization_percentage = (row.total_bookings / row.capacity) * 100 if row.capacity > 0 else 0
        popular_events.append({
            "event_id": row.id,
            "event_name": row.name,
            "venue": row.venue,
            "total_bookings": row.total_bookings,
            "capacity": row.capacity,
            "utilization_percentage": round(utilization_percentage, 2)
        })
    
    return popular_events

async def get_capacity_utilization(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get capacity utilization for all events"""
    q = (
        select(
            Event.id,
            Event.name,
            Event.venue,
            Event.capacity,
            func.count(Booking.id).label("booked_seats")
        )
        .outerjoin(Booking, (Booking.event_id == Event.id) & (Booking.status == "BOOKED"))
        .group_by(Event.id, Event.name, Event.venue, Event.capacity)
        .order_by(Event.name)
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    utilization_data = []
    for row in rows:
        booked_seats = row.booked_seats or 0
        available_seats = row.capacity - booked_seats
        utilization_percentage = (booked_seats / row.capacity) * 100 if row.capacity > 0 else 0
        
        # Determine status based on utilization
        if utilization_percentage == 100:
            status = "Full"
        elif utilization_percentage >= 80:
            status = "High"
        elif utilization_percentage >= 50:
            status = "Medium"
        else:
            status = "Low"
        
        utilization_data.append({
            "event_id": row.id,
            "event_name": row.name,
            "venue": row.venue,
            "total_capacity": row.capacity,
            "booked_seats": booked_seats,
            "available_seats": available_seats,
            "utilization_percentage": round(utilization_percentage, 2),
            "status": status
        })
    
    return utilization_data

async def get_average_capacity_utilization(db: AsyncSession) -> float:
    """Get average capacity utilization across all events"""
    q = (
        select(
            Event.capacity,
            func.count(Booking.id).label("booked_seats")
        )
        .outerjoin(Booking, (Booking.event_id == Event.id) & (Booking.status == "BOOKED"))
        .group_by(Event.id, Event.capacity)
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    if not rows:
        return 0.0
    
    total_utilization = 0
    event_count = 0
    
    for row in rows:
        if row.capacity > 0:
            utilization = (row.booked_seats / row.capacity) * 100
            total_utilization += utilization
            event_count += 1
    
    return round(total_utilization / event_count, 2) if event_count > 0 else 0.0

async def get_booking_trends(db: AsyncSession, days: int = 30) -> List[Dict[str, Any]]:
    """Get booking trends for the last N days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    q = (
        select(
            func.date(Booking.created_at).label("booking_date"),
            func.count(Booking.id).label("total_bookings"),
            func.count(func.distinct(Booking.event_id)).label("events_count")
        )
        .where(
            (Booking.created_at >= start_date) &
            (Booking.status == "BOOKED")
        )
        .group_by(func.date(Booking.created_at))
        .order_by("booking_date")
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    trends = []
    for row in rows:
        trends.append({
            "date": row.booking_date.isoformat(),
            "total_bookings": row.total_bookings,
            "events_count": row.events_count
        })
    
    return trends

async def get_user_booking_stats(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Get booking statistics for a specific user"""
    # Total bookings
    total_q = select(func.count(Booking.id)).where(Booking.user_id == user_id)
    total_result = await db.execute(total_q)
    total_bookings = total_result.scalar() or 0
    
    # Active bookings
    active_q = select(func.count(Booking.id)).where(
        (Booking.user_id == user_id) & (Booking.status == "BOOKED")
    )
    active_result = await db.execute(active_q)
    active_bookings = active_result.scalar() or 0
    
    # Cancelled bookings
    cancelled_q = select(func.count(Booking.id)).where(
        (Booking.user_id == user_id) & (Booking.status == "CANCELLED")
    )
    cancelled_result = await db.execute(cancelled_q)
    cancelled_bookings = cancelled_result.scalar() or 0
    
    # Most booked venue
    venue_q = (
        select(Event.venue, func.count(Booking.id).label("booking_count"))
        .join(Event, Event.id == Booking.event_id)
        .where(Booking.user_id == user_id)
        .group_by(Event.venue)
        .order_by(desc("booking_count"))
        .limit(1)
    )
    venue_result = await db.execute(venue_q)
    venue_row = venue_result.first()
    most_booked_venue = venue_row.venue if venue_row else None
    
    # Get user email
    user_q = select(User.email).where(User.id == user_id)
    user_result = await db.execute(user_q)
    user_email = user_result.scalar()
    
    return {
        "user_id": user_id,
        "user_email": user_email,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "cancelled_bookings": cancelled_bookings,
        "most_booked_venue": most_booked_venue
    }

async def get_venue_analytics(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get analytics for all venues"""
    q = (
        select(
            Event.venue,
            func.count(func.distinct(Event.id)).label("total_events"),
            func.count(Booking.id).label("total_bookings"),
            func.avg(
                func.cast(func.count(Booking.id), func.Float) / 
                func.cast(Event.capacity, func.Float) * 100
            ).label("avg_utilization")
        )
        .outerjoin(Booking, (Booking.event_id == Event.id) & (Booking.status == "BOOKED"))
        .where(Event.venue.isnot(None))
        .group_by(Event.venue)
        .order_by(desc("total_bookings"))
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    venue_analytics = []
    for row in rows:
        # Get most popular event for this venue
        popular_event_q = (
            select(Event.name, func.count(Booking.id).label("booking_count"))
            .join(Booking, Booking.event_id == Event.id)
            .where((Event.venue == row.venue) & (Booking.status == "BOOKED"))
            .group_by(Event.name)
            .order_by(desc("booking_count"))
            .limit(1)
        )
        popular_result = await db.execute(popular_event_q)
        popular_row = popular_result.first()
        most_popular_event = popular_row.name if popular_row else None
        
        venue_analytics.append({
            "venue": row.venue,
            "total_events": row.total_events,
            "total_bookings": row.total_bookings or 0,
            "average_utilization": round(row.avg_utilization or 0, 2),
            "most_popular_event": most_popular_event
        })
    
    return venue_analytics
