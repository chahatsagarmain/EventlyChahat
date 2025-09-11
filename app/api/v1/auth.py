import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut
from app.crud.user import get_user_by_email, create_user
from app.models.user import User
from app.core.config import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(payload=to_encode, algorithm=settings.JWT_ALGORITHM , key=settings.JWT_SECRET )

@router.post("/register", response_model=UserOut, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, user_in.email.lower())
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email.lower(),
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        is_admin=user_in.is_admin
    )
    created = await create_user(db, user)
    return created

@router.post("/token", response_model=Token)
async def login_for_token(username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, username.lower())
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    data = {"user_id": user.id, "email": user.email, "is_admin": user.is_admin}
    token = create_access_token(data)
    return Token(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
