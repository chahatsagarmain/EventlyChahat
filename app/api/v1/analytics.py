
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db, admin_required, get_current_user
from app.crud import analytics
from app.core import redis
from app.helper.helper import rows_to_dict_list
from typing import Optional

router = APIRouter()

@router.get("/overview", dependencies=[Depends(admin_required)])
async def get_booking_analytics_overview(db: AsyncSession = Depends(get_db)):
    """Get comprehensive booking analytics overview"""
    
    # Check cache first
    cache_key = redis.make_cache_key("analytics", "overview")
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    # Gather all analytics data
    total_bookings = await analytics.get_total_bookings(db)
    total_events = await analytics.get_total_events(db)
    total_users = await analytics.get_total_users(db)
    average_utilization = await analytics.get_average_capacity_utilization(db)
    most_popular_events = await analytics.get_most_popular_events(db, limit=5)
    capacity_utilization = await analytics.get_capacity_utilization(db)
    booking_trends = await analytics.get_booking_trends(db, days=30)
    
    analytics_data = {
        "total_bookings": total_bookings,
        "total_events": total_events,
        "total_users": total_users,
        "average_capacity_utilization": average_utilization,
        "most_popular_events": most_popular_events,
        "capacity_utilization": capacity_utilization,
        "booking_trends": booking_trends
    }
    
    try:
        await redis.set_cache(cache_key, analytics_data, ttl=900)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    return analytics_data

@router.get("/popular-events", dependencies=[Depends(admin_required)])
async def get_most_popular_events(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get most popular events by booking count"""
    
    cache_key = redis.make_cache_key("analytics", "popular_events", limit)
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    popular_events = await analytics.get_most_popular_events(db, limit=limit)
    
    try:
        await redis.set_cache(cache_key, popular_events, ttl=600)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    return popular_events

@router.get("/capacity-utilization", dependencies=[Depends(admin_required)])
async def get_capacity_utilization_report(db: AsyncSession = Depends(get_db)):
    """Get capacity utilization report for all events"""
    
    cache_key = redis.make_cache_key("analytics", "capacity_utilization")
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    utilization_data = await analytics.get_capacity_utilization(db)
    
    try:
        await redis.set_cache(cache_key, utilization_data, ttl=300)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    return utilization_data

@router.get("/booking-trends", dependencies=[Depends(admin_required)])
async def get_booking_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get booking trends for the specified number of days"""
    
    cache_key = redis.make_cache_key("analytics", "booking_trends", days)
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    trends = await analytics.get_booking_trends(db, days=days)
    
    try:
        await redis.set_cache(cache_key, trends, ttl=1800)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    return trends

@router.get("/user-stats/{user_id}", dependencies=[Depends(admin_required)])
async def get_user_booking_statistics(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    """Get booking statistics for a specific user"""
    
    cache_key = redis.make_cache_key("analytics", "user_stats", user_id)
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    user_stats = await analytics.get_user_booking_stats(db, user_id)
    
    # Cache for 5 minutes
    try:
        await redis.set_cache(cache_key, user_stats, ttl=300)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    return user_stats

@router.get("/my-stats")
async def get_my_booking_statistics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get booking statistics for the current user"""
    
    cache_key = redis.make_cache_key("analytics", "user_stats", current_user.id)
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    user_stats = await analytics.get_user_booking_stats(db, current_user.id)
    
    try:
        await redis.set_cache(cache_key, user_stats, ttl=300)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    return user_stats

@router.get("/venue-analytics", dependencies=[Depends(admin_required)])
async def get_venue_analytics_report(db: AsyncSession = Depends(get_db)):
    """Get analytics report for all venues"""
    
    cache_key = redis.make_cache_key("analytics", "venue_analytics")
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    venue_data = await analytics.get_venue_analytics(db)

    try:    
        await redis.set_cache(cache_key, venue_data, ttl=900)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    return venue_data

@router.get("/summary", dependencies=[Depends(admin_required)])
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Get a quick summary of key analytics metrics"""
    
    cache_key = redis.make_cache_key("analytics", "summary")
    try:
        cached = await redis.get_cache(cache_key)
        if cached:
            return cached
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")

    total_bookings = await analytics.get_total_bookings(db)
    total_events = await analytics.get_total_events(db)
    total_users = await analytics.get_total_users(db)
    average_utilization = await analytics.get_average_capacity_utilization(db)
    
    summary = {
        "total_bookings": total_bookings,
        "total_events": total_events,
        "total_users": total_users,
        "average_capacity_utilization": average_utilization,
        "last_updated": "real-time"
    }
    
    # Cache for 2 minutes for quick summary
    try:
        await redis.set_cache(cache_key, summary, ttl=120)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
        
    return summary