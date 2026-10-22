import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não foi encontrada no arquivo .env")

# SSL e cache de statements só para PostgreSQL (Supabase / pgbouncer)
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args = {"ssl": "require", "statement_cache_size": 0}

engine = create_async_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO") == "1",  # defina SQL_ECHO=1 no .env para ver o SQL
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
