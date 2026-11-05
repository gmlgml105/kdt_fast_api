from datetime import datetime, timedelta, timezone
from sqlalchemy import BigInteger, Text, Integer, DateTime, Identity, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.enums.member_enum import MemberProvider

# PostgreSQL의 Base를 상속받아서 서버가 켜질 때 동기화시킨다.
from app.infrastructure.postgresql import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.post_model import Post

KST = timezone(timedelta(hours=9)) # UTC+9

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    member_email: Mapped[str] = mapped_column(Text, nullable=False)
    member_password: Mapped[str | None] = mapped_column(Text)
    member_name: Mapped[str | None] = mapped_column(Text)
    member_age: Mapped[int | None] = mapped_column(Integer)
    member_profile: Mapped[str | None] = mapped_column(Text, default="/members/default.jpg")
    member_provider_id: Mapped[str | None] = mapped_column(Text, unique=True)
    member_provider: Mapped[MemberProvider] = mapped_column(
        SQLEnum(MemberProvider, native_enum=False), 
        nullable=False,
        default=MemberProvider.LOCAL
    )
    member_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(KST)
    )

    __table_args__ = (
        UniqueConstraint("member_email", "member_provider", name="uq_member_email_provider"),
    )

    # 관계
    # cascade: Member가 삭제되면 참조된 테이블을 모두 같이 연쇄삭제
    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="member", cascade="all, delete-orphan"
    )


