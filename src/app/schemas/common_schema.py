from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class ApiResponseDTO(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None

class PageResponseDTO(BaseModel, Generic[T]):
    total_count: int
    total_pages: int
    offset: int
    limit: int 
    items: List[T] | None = None
