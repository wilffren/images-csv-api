from typing import Optional
from src.domain.interfaces.image_repository import ImageRepository


class GetAllImages:
    def __init__(self, repository: ImageRepository):
        self.repository = repository

    def execute(
        self,
        page: int = 1,
        limit: int = 50,
        sort_by: Optional[str] = None,
        order: str = "asc",
    ):
        limit = min(limit, 500)
        return self.repository.get_all(page=page, limit=limit, sort_by=sort_by, order=order)
