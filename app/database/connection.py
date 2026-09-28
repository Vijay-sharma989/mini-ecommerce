import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

AsyncSessionlocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)