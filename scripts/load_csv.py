"""
Script de carga idempotente: CSV → SQLite
- Si la DB ya tiene datos → skip
- Si la DB está vacía → cargar todo el CSV
- Errores por fila se loggean pero no abortan la carga
"""
import logging
import os
import csv
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CSV_FILE = Path(__file__).parent.parent / "data" / "images.csv"
# Fallback: look in project root
if not CSV_FILE.exists():
    CSV_FILE = Path(__file__).parent.parent / "images.csv"


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")


def _parse_int(value: str):
    value = value.strip()
    if not value:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _parse_float(value: str) -> float:
    value = value.strip()
    if not value:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def load_csv(db_session=None):
    from database import SessionLocal, ImageModel, create_tables

    create_tables()

    session = db_session or SessionLocal()
    try:
        count = session.query(ImageModel).count()
        if count > 0:
            logger.info("DB ya tiene %d registros — skip carga CSV", count)
            return

        if not CSV_FILE.exists():
            logger.error("CSV no encontrado en: %s", CSV_FILE)
            return

        logger.info("Cargando CSV desde: %s", CSV_FILE)

        loaded = 0
        errors = 0
        total = 0

        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                total += 1
                try:
                    record = ImageModel(
                        image_url=row.get("image_url", "").strip(),
                        alt_text=row.get("alt_text", "").strip() or None,
                        page_source=row.get("page_source", "").strip() or None,
                        width=_parse_int(row.get("width", "")),
                        height=_parse_int(row.get("height", "")),
                        format=row.get("format", "").strip(),
                        estimated_size_kb=_parse_float(row.get("estimated_size_kb", "0")),
                        category=row.get("category", "").strip(),
                        downloaded=_parse_bool(row.get("downloaded", "False")),
                        local_path=row.get("local_path", "").strip() or None,
                    )
                    session.add(record)
                    loaded += 1

                    if loaded % 100 == 0:
                        session.commit()
                        logger.info("Progreso: %d registros cargados...", loaded)

                except Exception as e:
                    errors += 1
                    logger.warning("Error en fila %d: %s — %s", row_num, row, e)
                    continue

        session.commit()
        logger.info("Cargados %d registros de %d (errores: %d)", loaded, total, errors)

    finally:
        if db_session is None:
            session.close()


if __name__ == "__main__":
    load_csv()
