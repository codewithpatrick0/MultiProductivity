from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv('NEON_DATABASE_STRING')

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False 
)

#Class base important
Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
            
        yield session
        

