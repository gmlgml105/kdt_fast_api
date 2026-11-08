from fastapi import APIRouter, Query, Depends
from app.services.post_service import get_post_service, PostService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.post_schema import PostCreateDTO, PostUpdateDTO
from app.enums.post_enum import PostSortEnum, PostSearchEnum

from app.models.post_model import Post
from app.infrastructure.postgresql import get_postgresql_db, AsyncSession
import random

router = APIRouter()

# /posts, POST
@router.post(
    "",
    summary="게시글 작성",
    response_model=ApiResponseDTO
)
async def write_post(
    member_id: int,
    post:PostCreateDTO,
    post_service: PostService = Depends(get_post_service)
):
    new_post_id = await post_service.write_post(member_id, post)

    return ApiResponseDTO(
        success=True,
        message="게시글 작성 성공",
        data={
            "newPostId": new_post_id
        }
    )



# 게시글 전체 조회(페이지네이션 + 정렬 + 검색)
@router.get(
    "/search",
    summary="게시판 전체 조회(검색)",
    response_model=ApiResponseDTO
)
async def search_posts(
    offset: int = Query(0, ge=0, description="시작 오프셋"),
    limit: int = Query(10, ge=1, le=100, description="가져올 개수"),
    sort_by: PostSortEnum = Query(
        PostSortEnum.LATEST.value, 
        description="정렬 기준(LATEST, OLDEST, VIEWS)"
    ),
    search_keyword: PostSearchEnum = Query(
        PostSearchEnum.TITLE,
        description="검색 기준(TITLE, CONTENT, WRITER, TITLE_CONTENT)"
    ),
    keyword: str | None = Query(None, description="검색할 키워드"),
    post_service: PostService = Depends(get_post_service)
):

    paged_posts = await post_service.search_posts_by_paging(
        offset, 
        limit, 
        sort_by, 
        search_keyword, 
        keyword
    ) 

    return ApiResponseDTO(
        success=True,
        message="전체 게시글 조회 성공",
        data=paged_posts
    )


@router.get(
    "/{post_id}",
    summary="게시글 조회(post_id)",
    response_model=ApiResponseDTO
)
async def read_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service)
):
    found_post = await post_service.read_post(post_id)

    return ApiResponseDTO(
        success=True,
        message=f"{post_id}번 게시글 조회 성공",
        data=found_post
    )


# 게시글 전체 조회(페이지네이션 + 정렬)
@router.get(
    "",
    summary="게시판 전체 조회",
    response_model=ApiResponseDTO
)
async def get_posts(
    offset: int = Query(0, ge=0, description="시작 오프셋"),
    limit: int = Query(10, ge=1, le=100, description="가져올 개수"),
    sort_by: PostSortEnum = Query(
        PostSortEnum.LATEST.value, 
        description="정렬 기준(LATEST, OLDEST, VIEWS)"
    ),
    post_service: PostService = Depends(get_post_service)
):
    paged_posts = await post_service.read_posts_by_paging(offset, limit, sort_by)
    
    return ApiResponseDTO(
        success=True,
        message="전체 게시글 조회 성공",
        data=paged_posts
    )


@router.put(
        "/{id}",
        summary="게시글 수정",
        response_model=ApiResponseDTO
)
async def edit_post(
    id: int,
    post: PostUpdateDTO,
    post_service: PostService = Depends(get_post_service)
):

    updated_post_id = await post_service.edit_post(id, post)

    return ApiResponseDTO(
        success=True,
        message= "게시글 수정 완료",
        data={
            "updated_post_id": updated_post_id
        }
    )


@router.delete(
    "/{id}",
    summary="게시글 삭제",
    response_model=ApiResponseDTO
)
async def remove_post(
    id: int,
    post_service: PostService = Depends(get_post_service)
):
    await post_service.remove_post(id)

    return ApiResponseDTO(
        success=True, 
        message="게시글 삭제 완료."
    )



# 더미 데이터 추가
@router.post("/dummies", summary="게시판 더미데이터 추가")
async def get_dummies(
    count: int = 100,
    db:AsyncSession = Depends(get_postgresql_db)
):
    target_member_ids = [1, 2, 3]

    for i in range(1, count + 1):
        random_member_id = random.choice(target_member_ids)
        random_view = random.randint(0, 10000)

        new_post = Post(
            post_title=f"랜덤 테스트 제목 {i}",
            post_content=f"랜덤한 글 내용 {i}",
            post_read_count=random_view,
            member_id=random_member_id
        )

        db.add(new_post)

    await db.commit()

    return {
        "message": "더미데이터 추가 성공!"
    }
