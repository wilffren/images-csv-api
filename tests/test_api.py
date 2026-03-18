"""
Tests de integración para la API de imágenes.
Usa una DB en memoria para no afectar datos reales.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, ImageModel, get_db
from main import app

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Insert test records
    session = TestingSession()
    for i in range(1, 11):
        session.add(ImageModel(
            image_url=f"https://example.com/img{i}.jpg",
            alt_text=f"Imagen {i}",
            page_source="https://example.com",
            width=800,
            height=600,
            format="jpg",
            estimated_size_kb=float(i * 10),
            category="test",
            downloaded=True,
            local_path=f"data/output/test/img{i}.jpg",
        ))
    session.commit()
    session.close()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "endpoints" in body["data"]


def test_list_images(client):
    r = client.get("/images")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert len(body["data"]) == 10
    assert body["meta"]["total"] == 10


def test_get_image_by_id(client):
    r = client.get("/images/1")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["id"] == 1


def test_get_image_not_found(client):
    r = client.get("/images/9999")
    assert r.status_code == 404


def test_pagination(client):
    r = client.get("/images?page=2&limit=3")
    assert r.status_code == 200
    body = r.json()
    assert len(body["data"]) == 3
    assert body["meta"]["page"] == 2


def test_search_q(client):
    r = client.get("/images/search?q=Imagen")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["meta"]["total"] > 0


def test_search_exact_filter(client):
    r = client.get("/images/search?category=test")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] == 10


def test_search_contains(client):
    r = client.get("/images/search?image_url_contains=example")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] == 10


def test_search_numeric_gte(client):
    r = client.get("/images/search?estimated_size_kb_gte=50")
    assert r.status_code == 200
    body = r.json()
    # records with estimated_size_kb >= 50: ids 5..10 → 6 records
    assert body["meta"]["total"] == 6


def test_columns(client):
    r = client.get("/images/columns")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    columns = {c["name"] for c in body["data"]}
    assert "image_url" in columns
    assert "category" in columns


def test_stats(client):
    r = client.get("/images/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total_records" in body["data"]
    assert body["data"]["total_records"] == 10


def test_sort_by(client):
    r = client.get("/images?sort_by=estimated_size_kb&order=desc")
    assert r.status_code == 200
    data = r.json()["data"]
    sizes = [d["estimated_size_kb"] for d in data]
    assert sizes == sorted(sizes, reverse=True)
