from src.domain.interfaces.image_repository import ImageRepository


class GetImageById:
    def __init__(self, repository: ImageRepository):
        self.repository = repository

    def execute(self, image_id: int):
        return self.repository.get_by_id(image_id)
