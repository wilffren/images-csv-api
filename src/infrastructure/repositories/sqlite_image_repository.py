import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from database import ImageModel
from src.domain.interfaces.image_repository import ImageRepository

logger = logging.getLogger(__name__)

VALID_COLUMNS = {
    "id", "image_url", "alt_text", "page_source",
    "width", "height", "format", "estimated_size_kb",
    "category", "downloaded", "local_path",
}

NUMERIC_COLUMNS = {"id", "width", "height", "estimated_size_kb"}
BOOL_COLUMNS = {"downloaded"}
STRING_COLUMNS = VALID_COLUMNS - NUMERIC_COLUMNS - BOOL_COLUMNS

COLUMN_TYPES = {
    "id": "integer",
    "image_url": "string",
    "alt_text": "string",
    "page_source": "string",
    "width": "integer",
    "height": "integer",
    "format": "string",
    "estimated_size_kb": "float",
    "category": "string",
    "downloaded": "boolean",
    "local_path": "string",
}


class SQLiteImageRepository(ImageRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        limit: int = 50,
        sort_by: Optional[str] = None,
        order: str = "asc",
    ) -> Tuple[List, int]:
        query = self.db.query(ImageModel)
        total = query.count()

        if sort_by and sort_by in VALID_COLUMNS:
            col = getattr(ImageModel, sort_by)
            query = query.order_by(col.desc() if order == "desc" else col.asc())
        else:
            query = query.order_by(ImageModel.id.asc())

        offset = (page - 1) * limit
        records = query.offset(offset).limit(limit).all()
        return records, total

    def get_by_id(self, image_id: int):
        return self.db.query(ImageModel).filter(ImageModel.id == image_id).first()

    def search(self, filters: dict, page: int = 1, limit: int = 50) -> Tuple[List, int]:
        query = self.db.query(ImageModel)

        q = filters.pop("q", None)
        if q:
            search_term = f"%{q}%"
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    ImageModel.image_url.ilike(search_term),
                    ImageModel.alt_text.ilike(search_term),
                    ImageModel.page_source.ilike(search_term),
                    ImageModel.format.ilike(search_term),
                    ImageModel.category.ilike(search_term),
                    ImageModel.local_path.ilike(search_term),
                )
            )

        for key, value in filters.items():
            if key.endswith("_contains"):
                col_name = key[: -len("_contains")]
                if col_name in STRING_COLUMNS:
                    col = getattr(ImageModel, col_name, None)
                    if col is not None:
                        query = query.filter(col.ilike(f"%{value}%"))
            elif key.endswith("_gte"):
                col_name = key[: -len("_gte")]
                if col_name in NUMERIC_COLUMNS:
                    col = getattr(ImageModel, col_name, None)
                    if col is not None:
                        try:
                            query = query.filter(col >= float(value))
                        except ValueError:
                            pass
            elif key.endswith("_lte"):
                col_name = key[: -len("_lte")]
                if col_name in NUMERIC_COLUMNS:
                    col = getattr(ImageModel, col_name, None)
                    if col is not None:
                        try:
                            query = query.filter(col <= float(value))
                        except ValueError:
                            pass
            elif key in VALID_COLUMNS:
                col = getattr(ImageModel, key, None)
                if col is not None:
                    if key in BOOL_COLUMNS:
                        query = query.filter(col == (value.lower() in ("true", "1")))
                    else:
                        query = query.filter(col == value)

        total = query.count()
        offset = (page - 1) * limit
        records = query.offset(offset).limit(limit).all()
        return records, total

    def get_columns(self) -> List[dict]:
        return [{"name": col, "type": typ} for col, typ in COLUMN_TYPES.items()]

    def get_stats(self) -> dict:
        from sqlalchemy import func

        total = self.db.query(func.count(ImageModel.id)).scalar()
        stats = {"total_records": total}

        for col_name in ("estimated_size_kb", "width", "height", "id"):
            col = getattr(ImageModel, col_name)
            row = self.db.query(
                func.min(col),
                func.max(col),
                func.avg(col),
            ).one()
            stats[col_name] = {
                "min": round(row[0], 2) if row[0] is not None else None,
                "max": round(row[1], 2) if row[1] is not None else None,
                "avg": round(row[2], 2) if row[2] is not None else None,
            }

        return stats
