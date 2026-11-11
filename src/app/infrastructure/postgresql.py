import os
from dotenv import load_dotenv

load_dotenv() 

POSTGRESQL_DATABASE_URL = os.getenv("POSTGRESQL_DATABASE_URL")
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 1. 비동기 전영 DB 엔진 생성
engine = create_async_engine(
    POSTGRESQL_DATABASE_URL, echo=True
)

# 2. 비동기 세션 생성기 
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False # 비동기 설정 필수값
)

# 3. Model은 반드시 Base를 상속받아서 설계해야 ORM이 관리해준다.
class Base(DeclarativeBase):
    pass 

# ※ 4. FastAPI 비동기 의존성 주입(Dependency Injection)을 처리하는 함수
async def get_postgresql_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db

        except Exception:
            await db.rollback()
            raise    

        finally:
            await db.close()


