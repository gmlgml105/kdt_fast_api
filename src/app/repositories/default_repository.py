from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from sqlalchemy import insert, select, update, delete, func, exists

class DefaultRepository:

    # 생성자 주입
    def __init__(self, db: AsyncSession):
        self.db = db

    # 순수 함수



# 주입 팩토리 메서드
def get_default_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return DefaultRepository(db)