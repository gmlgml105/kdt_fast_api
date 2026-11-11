from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel # JS 카멜을 Snake로 변경
from datetime import datetime
from app.enums.member_enum import MemberProvider

# VO
class MemberVO(BaseModel):
    id: int
    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_phone: str | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider
    member_created_at: datetime | None = None


# DTO
class MemberCreateDTO(BaseModel):
    # ORM -> Pydantic, 카멜케이스 요청도 허용
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_phone: str | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None
    member_provider_id: str | None = None


class SocialMemberCreateDTO(BaseModel):
    # ORM -> Pydantic, 카멜케이스 요청도 허용
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_phone: str | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None
    member_provider_id: str | None = None


class MemberResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_phone: str | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider
    member_created_at: datetime | None = None


class MemberUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_phone: str | None = None
    member_profile: str | None = "/members/default.jpg"


class MemberSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_email: str | None = None
    member_name: str | None = None
    member_profile: str | None = "/members/default.jpg"


# 토큰에 들어갈 최소한의 유저 정보
class MemberClaimDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_email: str
    member_provider: str