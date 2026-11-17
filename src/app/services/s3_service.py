import io
import os
from dotenv import load_dotenv
from fastapi import Depends, UploadFile
from app.enums.s3_folder_enum import S3Folder
from app.infrastructure.s3 import get_s3_client
from botocore.client import BaseClient
from datetime import datetime
from app.schemas.s3_schema import ImageUploadResponseDTO, FileUploadResponseDTO

import uuid
import urllib
from PIL import Image

load_dotenv()

load_dotenv()

AWS_S3_BUCKET=os.getenv("AWS_S3_BUCKET")
AWS_REGION=os.getenv("AWS_REGION")

# 예외처리
# 트랜잭션 관리
class S3service:
    def __init__(self, s3_client: BaseClient):
        self.s3_client = s3_client

    # 1. 업로드 이미지 + 썸네일
    async def upload_image_with_thumbnail(
        self, file: UploadFile, folder=S3Folder.PROFILE.value
    ) -> ImageUploadResponseDTO:
        original_filename = os.path.basename(file.filename)
        file_ext = original_filename.split(".")[-1].lower()
        file_uuid = str(uuid.uuid4())

        save_filename = f"{file_uuid}_{original_filename}"
        thumb_filename = f"t_{file_uuid}_{original_filename}"

        today_date_path = datetime.now().strftime("%Y/%m/%d")

        # S3에서 파일을 찾아가는 key == 폴더
        original_key = f"{folder}/{today_date_path}/original/{save_filename}"
        thumb_key = f"{folder}/{today_date_path}/thumb/{thumb_filename}"

        # 원본 이미지 업로드
        await self.s3_client.upload_fileobj(
            file.file,
            AWS_S3_BUCKET,
            original_key,
            ExtraArgs = {
                "ContentType": file.content_type
            }
        )

        # 썸네일 이미지 만들기
        file.file.seek(0)
        image = Image.open(file.file)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail((100, 100))
        buffer = io.BytesIO()

        if file_ext in ["jpg", "jpeg"]:
            save_format = "JPEG"
            thumb_content_type = "image/jpeg"

        elif file_ext == "png":
            save_format = "PNG"
            thumb_content_type = "image/png"

        elif file_ext == "webp":
            save_format = "WEBP"
            thumb_content_type = "image/webp"

        else: 
            save_format = "JPEG"
            thumb_content_type = "image/jpeg"

        image.save(buffer, format=save_format)
        buffer.seek(0)

        await self.s3_client.upload_fileobj(
            buffer,
            AWS_S3_BUCKET,
            thumb_key,
            ExtraArgs = {
                "ContentType": thumb_content_type
            }
        )

        return ImageUploadResponseDTO(
            original_key=original_key,
            thumb_key=thumb_key,
            original_url=self.get_url(original_key),
            thumb_url=self.get_url(thumb_key)
        )
 
    # 2. 이미지 URL 가져오기
    def get_url(self, key:str):
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    
    # 3. 이미지 삭제
    async def delete_file(self, key):
        await self.s3_client.delete_object(
            Bucket=AWS_S3_BUCKET,
            Key=key
        )

    # 4. 일반 파일 다운로드
    async def upload_file(
            self,
            file: UploadFile,
            folder: S3Folder
    ): 
        original_filename = os.path.basename(file.filename)
        file_uuid = str(uuid.uuid4())

        save_filename = f"{file_uuid}_{original_filename}"

        today_date_path = datetime.now().strftime("%Y/%m/%d")

        # S3에서 파일을 찾아가는 key == 폴더
        file_key = f"{folder}/{today_date_path}/original/{save_filename}"

        # 원본 이미지 업로드
        await self.s3_client.upload_fileobj(
            file.file,
            AWS_S3_BUCKET,
            file_key,
            ExtraArgs = {
                "ContentType": file.content_type
            }
        )

        return FileUploadResponseDTO(
            file_key=file_key,
            file_url=self.get_url(file_key),
            original_filename=original_filename
        )


    # 5. 파일 다운로드
    async def get_download_url(self, key: str):
        filename = os.path.basename(key)
        encoded_filename = urllib.parse.quote(filename)

        result = await self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket":AWS_S3_BUCKET,
                "Key": key,
                "ResponseContentDisposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            },
            ExpiresIn = 3600
        )

        return result

# 레포지토리 주입 팩토리 함수
def get_s3_service(s3_client: S3service = Depends(get_s3_client)):
    return S3service(s3_client)