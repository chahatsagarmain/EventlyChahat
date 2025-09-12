import json
from fastapi import APIRouter , Depends , status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db , get_current_user
from app.crud.booking import get_user_bookings , cancel_booking , get_booking
from app.core import redis
# from app.helper.helper import row_to_dict , rows_to_dict_list

router = APIRouter()

@router.get("/")
async def get_all_user_bookings(current_user= Depends(get_current_user) , db: AsyncSession = Depends(get_db)):
    key = redis.make_cache_key("user:bookings" , current_user.id)
    try:
        cached = await redis.get_cache(key)
        if cached != None:
            return [json.loads(booking) if isinstance(booking, str) else booking for booking in cached]
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    bookings = await get_user_bookings(current_user.id , db)
    try:
        await redis.set_cache(key,[booking.model_dump_json() for booking in bookings])
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    return bookings

@router.delete("/cancel/{book_id}")
async def cancel_user_booking(book_id : int , current_user=Depends(get_current_user) , db: AsyncSession = Depends(get_db)):
    booking = await get_booking(book_id , db)
    if booking == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="BOOKING NOT FOUND")
    deleted = await cancel_booking(book_id , db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail="ERROR CANCELING TICKET")
    try:
        await redis.delete_booking_cache(booking.event_id , current_user.id)
    except Exception as e:
        print(f"CACHE fetch error : {str(e)}")
    # now we fetch from waitlist 
    # start - 0 , end - -1 ( gets us the top 1 )
    # start - 0 , end - 1 ( gets us the top 2 )
    # start - 1 , end - 1 ( gets us exactly the 2nd )
    try:
        result = await redis.fetch_from_waitlist(f"event:set:{booking.event_id}" , 0 , -1)
        if result != None:
            print("call notification service")
            print(result)
            await redis.delete_from_waitlist(f"event:set:{booking.event_id}" , result)
    except Exception as e:
        print(f"WAITLIST ERROR : {e}")
    return deleted