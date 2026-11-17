from fastapi import APIRouter, Query, Depends, UploadFile, File, Form
from app.enums.s3_folder_enum import S3Folder
from app.services.member_service import get_member_service, MemberService
from app.services.s3_service import S3service, get_s3_service   # ✗ 대문자 S
from app.enums.member_enum import MemberProvider

from app.schemas.member_schema import MemberCreateDTO, MemberClaimDTO, MemberUpdateDTO
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.s3_schema import ImageUploadResponseDTO
from app.dependencies.auth_dependency import get_current_member


router = APIRouter()

@router.post(
    "/check-member", 
    response_model=ApiResponseDTO
)
async def check_member(
    member_email: str, 
    member_provider: str, 
    member_service = Depends(get_member_service)
):
    await member_service.check_duplicate_member(member_email, member_provider)
    return ApiResponseDTO(
        success=True,
        message="중복되지 않은 사용자",
    )


@router.post("/join",
    summary="회원 가입",
    response_model=ApiResponseDTO,
    responses={
        409: {
            "description": "중복된 이메일(또는 사용자 이름)으로 회원가입 시도",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "이미 존재하는 이메일입니다."
                    }
                }
            }
        }
}
)
async def join(
    member: MemberCreateDTO, 
    member_service: MemberService = Depends(get_member_service)
):
    if not member.member_provider:
        member.member_provider = MemberProvider.LOCAL.value
        
    member_claim: MemberClaimDTO = await member_service.join(member)

    return ApiResponseDTO(
        success=True,
        message="회원가입 성공",
        data=member_claim
    )


@router.get(
    "/{id}",
    response_model=ApiResponseDTO,
)
async def get_member_by_id(
    id: int, 
    member_service: MemberService = Depends(get_member_service)
):
    found_member = await member_service.get_member_by_id(id)
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=found_member
    )


# Query(...): 쿼리스트링으로 데이터를 받기, (...):필수
# get방식 값을 전송하는 방법 -> ?key=value&key=value
@router.get(
    "/",
    summary="회원 정보 조회(email, provider)",
    response_model=ApiResponseDTO
)
async def get_member_by_email_and_provider(
    member_email: str = Query(...),
    member_provider: str = Query(...),
    member_service: MemberService = Depends(get_member_service)
):
    found_member = await member_service.get_member_by_email_and_provider(member_email, member_provider)
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=found_member
    )


# "": "/members"
# @router.get(
#     "",
#     summary="회원 전체 정보 조회(테스트)",
#     response_model=ApiResponseDTO
# )
# async def get_members(member_service: MemberService = Depends(get_member_service)):
#     return ApiResponseDTO(
#         success=True,
#         message="회원 전체 조회 성공",
#         data=await member_service.get_members()
#     )

@router.get(
    "",
    summary="회원 전체 정보 조회",
    response_model=ApiResponseDTO
)
async def get_members(
    offset: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    member_service: MemberService = Depends(get_member_service)
):
    page_result = await member_service.get_members_paging(offset, limit)
    
    return ApiResponseDTO(
        success=True,
        message="회원 전체 조회 성공",
        data=page_result
    )


@router.put(
    "/{id}",
    summary="회원 정보 수정",
    response_model=ApiResponseDTO
)
async def update_member(
    id: int, 
    member: MemberUpdateDTO,
    member_service: MemberService = Depends(get_member_service)
):
    updated_member = await member_service.update_member(id, member)

    return ApiResponseDTO(
        success=True,
        message="회원 정보 업데이트 완료",
        data=updated_member
    )


@router.put(
    "/{id}/profile",
    summary="회원 프로필 수정",
    response_model=ApiResponseDTO
)
async def update_profile(
    id: int, 
    file: UploadFile = File(...),
    folder: S3Folder = Form(...),
    s3_service: S3service = Depends(get_s3_service),
    member_service: MemberService = Depends(get_member_service)
):
    result: ImageUploadResponseDTO = await s3_service.upload_image_with_thumbnail(
        file=file,
        folder=folder.value
    )

    original_url = result.original_url
    member_update_dto = MemberUpdateDTO(
        member_profile=original_url
    )
    
    updated_member = await member_service.update_member(id, member_update_dto)

    return ApiResponseDTO(
        success=True,
        message="프로필 수정 완료",
        data=updated_member
    )


@router.delete(
    "/{id}",
    summary="회원 탈퇴",
    response_model=ApiResponseDTO
)
async def withdraw(id: int, member_service: MemberService = Depends(get_member_service)):
    await member_service.withdraw(id)

    return ApiResponseDTO(
        success=True,
        message="회원 탈퇴 완료"
    )


# access_token -> 사용자를 전달하는 서비스
@router.post(
    "/me",
    response_model=ApiResponseDTO,
    summary="Access Token으로 회원정보 조회"
)
async def me(
    current_member: MemberClaimDTO = Depends(get_current_member),
    member_service: MemberService = Depends(get_member_service)
):
    member_id = current_member.id
    found_member = await member_service.get_member_by_id(member_id)

    return ApiResponseDTO(
        success=True,
        message="회원 정보 조회 완료",
        data=found_member
    )












