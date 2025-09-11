from fastapi import APIRouter, Depends, Path
from app.api.v1.deps import get_current_user, get_db
from app.schemas.user import UserOut , UserBookingsOut
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.crud.user import get_user
from app.crud.booking import get_user_bookings

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def read_own_profile(current_user=Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserOut)
async def get_user_info(user_id: int = Path(..., gt=0), current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

