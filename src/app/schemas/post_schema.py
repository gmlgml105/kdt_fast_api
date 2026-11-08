from pydantic import BaseModel
from datetime import datetime
from app.schemas.member_schema import MemberSummaryDTO

# VO
class PostVO(BaseModel):
    id: int
    post_title: str
    post_content: str
    post_read_count: int
    post_updated_at: datetime | None = None
    post_created_at: datetime | None = None
    member_id: int 

# DTO
class PostCreateDTO(BaseModel):
    post_title: str
    post_content: str

    class Config:
        from_attributes = True

# DTO
class PostDetailResponseDTO(BaseModel):
    id: int
    post_title: str
    post_content: str
    post_read_count: int
    post_updated_at: datetime | None = None
    post_created_at: datetime | None = None

    member: MemberSummaryDTO

    class Config:
        from_attributes = True

class PostListResponseDTO(BaseModel):
    id: int
    post_title: str
    post_read_count: int
    post_updated_at: datetime | None = None
    post_created_at: datetime | None = None

    member: MemberSummaryDTO

    class Config:
        from_attributes = True


class PostUpdateDTO(BaseModel):
    post_title: str
    post_content: str