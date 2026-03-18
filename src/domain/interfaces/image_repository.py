from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class ImageRepository(ABC):

    @abstractmethod
    def get_all(
        self,
        page: int,
        limit: int,
        sort_by: Optional[str],
        order: str,
    ) -> Tuple[List, int]:
        ...

    @abstractmethod
    def get_by_id(self, image_id: int):
        ...

    @abstractmethod
    def search(self, filters: dict, page: int, limit: int) -> Tuple[List, int]:
        ...

    @abstractmethod
    def get_columns(self) -> List[dict]:
        ...

    @abstractmethod
    def get_stats(self) -> dict:
        ...
