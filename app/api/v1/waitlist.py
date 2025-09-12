import time
from fastapi import APIRouter , Depends , status
from fastapi.exceptions import HTTPException
from app.api.v1.deps import get_current_user , get_db
from app.crud.event import get_event
from app.core.redis import insert_in_waitlist
from app.helper.helper import row_to_dict
from datetime import datetime


router = APIRouter()

@router.post("/{event_id}")
async def add_to_waitlist(event_id : int , current_user = Depends(get_current_user) , db = Depends(get_db)):
    ev = await get_event(db , event_id)
    if ev == None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    elif ev.bookings == None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        ct = 0
        for booking in ev.bookings:
            if booking.status == "BOOKED":
                ct += 1

        if ev.capacity > ct:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="MORE SEATS CAN BE BOOKED")
    
    ev = row_to_dict(ev)
    ev = {**ev ,
           "waitlist_user_id" : current_user.id ,
            "waitlist_user_email" : current_user.email}    
    # change the end time 
    await insert_in_waitlist(f"event:set:{event_id}" , ev , int(time.time()) , int(time.time()) + 360000)
    return {
        "message" : "ADDED TO WAITLIST"
    }