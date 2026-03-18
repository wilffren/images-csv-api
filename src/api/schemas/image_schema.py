from typing import Any, List, Optional
from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: int
    image_url: str
    alt_text: Optional[str] = None
    page_source: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    estimated_size_kb: float
    category: str
    downloaded: bool
    local_path: Optional[str] = None

    model_config = {"from_attributes": True}


class Meta(BaseModel):
    total: int
    page: int
    limit: int
    pages: int


class PaginatedResponse(BaseModel):
    success: bool = True
    data: List[Any]
    meta: Meta


class SingleResponse(BaseModel):
    success: bool = True
    data: Any


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
