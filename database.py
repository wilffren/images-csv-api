import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Use Render disk path in production, local path otherwise
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./data/api_data.db")

engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    image_url = Column(String, nullable=False, index=True)
    alt_text = Column(String, nullable=True)
    page_source = Column(String, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String, nullable=False, index=True)
    estimated_size_kb = Column(Float, nullable=False)
    category = Column(String, nullable=False, index=True)
    downloaded = Column(Boolean, nullable=False, default=False)
    local_path = Column(String, nullable=True)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
