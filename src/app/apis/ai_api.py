import os
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Depends, UploadFile, File, Form
from app.schemas.common_schema import ApiResponseDTO
from app.services.ai_service import get_ai_service, AiService

router = APIRouter()

@router.post(
    "/predict",
    response_model=ApiResponseDTO,
    summary="고양이/강아지 이미지 추론 모델"
)
async def predict_image_alexnet(
    file: UploadFile = File(...),
    ai_service: AiService = Depends(get_ai_service)
):
    # 사용자만 할 수 있는 토큰
    image_bytes: bytes = await file.read()
    result = ai_service.predict_image(image_bytes)

    return ApiResponseDTO(
        success=True,
        message="AI 추론 성공",
        data=result
    )