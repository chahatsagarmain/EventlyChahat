from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Evently (Async)"
    # asyncpg format: postgresql+asyncpg://user:password@host:port/dbname
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/evently"
    JWT_SECRET: str = "secret_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"

settings = Settings()
