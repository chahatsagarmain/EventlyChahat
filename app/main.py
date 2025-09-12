from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine, Base
from app.api.v1 import auth, users, events, seats , bookings, analytics , waitlist
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv("./.env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("running startup event")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title=settings.PROJECT_NAME , lifespan=lifespan)

# include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(seats.router, prefix="/api/v1", tags=["seats"])  # seats router uses /events/... paths
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(waitlist.router , prefix="/api/v1/waitlist", tags=["waitlist"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    pass