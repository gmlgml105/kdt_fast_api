from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from app.enums.s3_folder_enum import S3Folder

class ImageUploadResponseDTO(BaseModel):
    original_key : str | None = None
    thumb_key : str | None = None
    original_url: str | None = None
    thumb_url: str | None = None

    # ORM -> Pydantic, 카멜케이스 요청도 허용
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

class FileUploadResponseDTO(BaseModel):
    file_key : str | None = None
    file_url : str | None = None
    original_filename : str | None = None

    # ORM -> Pydantic, 카멜케이스 요청도 허용
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)