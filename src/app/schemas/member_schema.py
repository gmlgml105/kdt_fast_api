from pydantic import BaseModel
from datetime import datetime
from app.enums.member_enum import MemberProvider

# VO
class MemberVO(BaseModel):
    id: int
    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider
    member_created_at: datetime | None = None


# DTO
class MemberCreateDTO(BaseModel):
    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None

    # ORM -> Pydantic
    class Config:
        from_attributes = True

class SocialMemberCreateDTO(BaseModel):
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None

    # ORM -> Pydantic
    class Config:
        from_attributes = True

class MemberClaimDTO(BaseModel):
    id: int
    member_email: str
    member_provider: str 

    class Config:
        from_attributes = True


class MemberResponseDTO(BaseModel):
    id: int
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider
    member_created_at: datetime | None = None
    
    class Config:
        from_attributes = True


class MemberUpdateDTO(BaseModel):
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_profile: str | None = "/members/default.jpg"

    class Config:
        from_attributes = True


class MemberSummaryDTO(BaseModel):
    id: int 
    member_email: str | None = None
    member_name: str | None = None
    member_profile: str | None = "/members/default.jpg"

    class Config:
        from_attributes = True
