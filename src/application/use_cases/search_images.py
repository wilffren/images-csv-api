from src.domain.interfaces.image_repository import ImageRepository


class SearchImages:
    def __init__(self, repository: ImageRepository):
        self.repository = repository

    def execute(self, filters: dict, page: int = 1, limit: int = 50):
        limit = min(limit, 500)
        return self.repository.search(filters=filters, page=page, limit=limit)
