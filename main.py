import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.image_router import router as image_router
from src.api.middleware.error_handler import global_exception_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API — verificando datos...")
    try:
        from scripts.load_csv import load_csv
        load_csv()
    except Exception as e:
        logger.error("Error durante carga inicial del CSV: %s", e)
    yield
    logger.info("API detenida.")


app = FastAPI(
    title=os.getenv("API_TITLE", "Images CSV API"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description="REST API generada desde images.csv — Juliao Boticarios",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.include_router(image_router)


@app.get("/", tags=["health"])
def root():
    return {
        "success": True,
        "data": {
            "name": os.getenv("API_TITLE", "Images CSV API"),
            "version": os.getenv("API_VERSION", "1.0.0"),
            "resource": "/images",
            "docs": "/docs",
            "redoc": "/redoc",
            "endpoints": [
                "GET /images",
                "GET /images/{id}",
                "GET /images/search",
                "GET /images/columns",
                "GET /images/stats",
            ],
        },
    }
