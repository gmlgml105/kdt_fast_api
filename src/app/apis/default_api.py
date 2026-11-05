from fastapi import APIRouter, Query, Depends
from app.services.default_service import get_default_service, DefaultService
from app.schemas.common_schema import ApiResponseDTO

router = APIRouter()

@router.post("/default/{param1}",
    summary="API 제목",
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
async def default(
    param1: int, # Url Parameter
    param2: int, # Body Payload(POST, PUT, DELETE)
    parma3: int = Query(10, ge=1, le=100), # Query String(GET)
    default_service: DefaultService = Depends(get_default_service) # Dependency Injection
):

    # Default Response
    return ApiResponseDTO(
        success=True,
        message="회원가입 성공",
        data=None
    )








