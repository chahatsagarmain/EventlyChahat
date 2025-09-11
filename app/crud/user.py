from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from typing import Optional

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    q = select(User).where(User.email == email)
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def create_user(db: AsyncSession, user_obj: User) -> User:
    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)
    return user_obj
