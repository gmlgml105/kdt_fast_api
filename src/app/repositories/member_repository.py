from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends

# 모델, ORM
from app.models.member_model import Member
from app.schemas.member_schema import (
    MemberCreateDTO, MemberClaimDTO, MemberUpdateDTO
)
from sqlalchemy import insert, select, update, delete, func, exists


class MemberRepository:

    # 생성자 주입
    def __init__(self, db: AsyncSession):
        self.db = db


    # 순수 함수
    # 1. 이메일 중복확인
    async def exists_member_by_id(self, id: int) -> bool:
        query = (
            select(exists().where(Member.id == id))
        )
        result = await self.db.execute(query)
        return result.scalar()


    async def exists_member_email_and_provider(self, member_email: str, member_provider: str) -> bool:
        query = select(Member).where(
            Member.member_email == member_email,
            Member.member_provider == member_provider
        )

        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member is not None

    # 2. 회원가입
    async def create_member(self, member: MemberCreateDTO):
        # pydantic -> dict
        new_member = member.model_dump()
        query = (
            insert(Member)
            .values(**new_member)
        ).returning(
            Member.id,
            Member.member_email,
            Member.member_provider
        )

        result = await self.db.execute(query)
        await self.db.commit()

        # 필요한 값을 리턴(id, email, provider)
        id, member_email, member_provider = result.first()

        payload = {
            "id": id,
            "member_email": member_email,
            "member_provider": member_provider
        }

        # dict -> pydantic
        claim_dto = MemberClaimDTO.model_validate(payload)
        return claim_dto


    # 3. 소셜 회원가입
    # 4. 회원 정보 조회(id) 
    async def find_member_by_id(self, id: int):
        query = select(Member).where(Member.id == id)
        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member


    # 5. 회원 정보 조회(email, provider)
    async def find_member_by_email_and_provider(self, member_email: str, member_provider: str):
        query = (
            select(Member)
                .where(
                    Member.member_email == member_email,
                    Member.member_provider == member_provider
                )
        )

        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member

    # 6. 회원 전체 정보 조회(테스트)
    async def find_members(self) -> list[Member]:
        query = (
            select(Member)
        )

        result = await self.db.execute(query)
        members = result.scalars().all()
        return members

    # 6-1 회원 전체 조회 + 페이지네이션
    # offset - limit
    # page - perpage
    async def find_member_by_paging(self, offset: int, limit: int) -> list[Member]:
        query = (
            select(Member)
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)
        members = result.scalars().all()
        return members


    async def count_members(self) -> int:
        query = (
            select(func.count()).select_from(Member)
        )
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count

    # 7. 회원 정보 수정
    async def update_member(self, id: int, update_data: dict) -> Member | None:
        if not update_data:
            return None

        query = (
            update(Member)
            .where(Member.id == id)
            .values(**update_data)
            .returning(Member)
        )

        result = await self.db.execute(query)
        await self.db.commit()

        updated_member = result.scalar_one_or_none()
        return updated_member


    # 8. 회원 삭제
    async def delete_member(self, id: int) -> bool:
        query = (
            delete(Member)
                .where(Member.id == id)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0




# 주입 팩토리 메서드
def get_member_repository(db: AsyncSession = Depends(get_postgresql_db)):
    return MemberRepository(db)