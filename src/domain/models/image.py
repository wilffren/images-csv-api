from typing import Optional
from pydantic import BaseModel


class Image(BaseModel):
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
