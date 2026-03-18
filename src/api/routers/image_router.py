import math
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from src.application.use_cases.get_all_images import GetAllImages
from src.application.use_cases.get_image_by_id import GetImageById
from src.application.use_cases.search_images import SearchImages
from src.infrastructure.repositories.sqlite_image_repository import SQLiteImageRepository
from src.api.schemas.image_schema import (
    ImageResponse,
    PaginatedResponse,
    SingleResponse,
    Meta,
)

router = APIRouter(prefix="/images", tags=["images"])
logger = logging.getLogger(__name__)


def _make_paginated(records, total: int, page: int, limit: int) -> PaginatedResponse:
    pages = math.ceil(total / limit) if limit else 1
    return PaginatedResponse(
        success=True,
        data=[ImageResponse.model_validate(r) for r in records],
        meta=Meta(total=total, page=page, limit=limit, pages=pages),
    )


@router.get("", response_model=PaginatedResponse)
def list_images(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    sort_by: Optional[str] = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    repo = SQLiteImageRepository(db)
    records, total = GetAllImages(repo).execute(page=page, limit=limit, sort_by=sort_by, order=order)
    return _make_paginated(records, total, page, limit)


@router.get("/columns", response_model=SingleResponse)
def get_columns(db: Session = Depends(get_db)):
    repo = SQLiteImageRepository(db)
    cols = repo.get_columns()
    return SingleResponse(success=True, data=cols)


@router.get("/stats", response_model=SingleResponse)
def get_stats(db: Session = Depends(get_db)):
    repo = SQLiteImageRepository(db)
    stats = repo.get_stats()
    return SingleResponse(success=True, data=stats)


@router.get("/search", response_model=PaginatedResponse)
def search_images(
    q: Optional[str] = Query(None, description="Full-text search en columnas string"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    # Exact filters
    image_url: Optional[str] = Query(None),
    alt_text: Optional[str] = Query(None),
    page_source: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    downloaded: Optional[str] = Query(None),
    local_path: Optional[str] = Query(None),
    # Contains filters
    image_url_contains: Optional[str] = Query(None),
    alt_text_contains: Optional[str] = Query(None),
    category_contains: Optional[str] = Query(None),
    format_contains: Optional[str] = Query(None),
    local_path_contains: Optional[str] = Query(None),
    # Numeric range filters
    estimated_size_kb_gte: Optional[float] = Query(None),
    estimated_size_kb_lte: Optional[float] = Query(None),
    width_gte: Optional[int] = Query(None),
    width_lte: Optional[int] = Query(None),
    height_gte: Optional[int] = Query(None),
    height_lte: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    filters = {}
    if q:
        filters["q"] = q
    if image_url:
        filters["image_url"] = image_url
    if alt_text:
        filters["alt_text"] = alt_text
    if page_source:
        filters["page_source"] = page_source
    if format:
        filters["format"] = format
    if category:
        filters["category"] = category
    if downloaded is not None:
        filters["downloaded"] = downloaded
    if local_path:
        filters["local_path"] = local_path
    if image_url_contains:
        filters["image_url_contains"] = image_url_contains
    if alt_text_contains:
        filters["alt_text_contains"] = alt_text_contains
    if category_contains:
        filters["category_contains"] = category_contains
    if format_contains:
        filters["format_contains"] = format_contains
    if local_path_contains:
        filters["local_path_contains"] = local_path_contains
    if estimated_size_kb_gte is not None:
        filters["estimated_size_kb_gte"] = str(estimated_size_kb_gte)
    if estimated_size_kb_lte is not None:
        filters["estimated_size_kb_lte"] = str(estimated_size_kb_lte)
    if width_gte is not None:
        filters["width_gte"] = str(width_gte)
    if width_lte is not None:
        filters["width_lte"] = str(width_lte)
    if height_gte is not None:
        filters["height_gte"] = str(height_gte)
    if height_lte is not None:
        filters["height_lte"] = str(height_lte)

    repo = SQLiteImageRepository(db)
    records, total = SearchImages(repo).execute(filters=filters, page=page, limit=limit)
    return _make_paginated(records, total, page, limit)


@router.get("/{image_id}", response_model=SingleResponse)
def get_image(image_id: int, db: Session = Depends(get_db)):
    repo = SQLiteImageRepository(db)
    record = GetImageById(repo).execute(image_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Registro con id={image_id} no encontrado",
                },
            },
        )
    return SingleResponse(success=True, data=ImageResponse.model_validate(record))
