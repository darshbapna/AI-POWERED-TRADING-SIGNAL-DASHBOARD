import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.db.database import engine, Base
from backend.app.jobs.scheduler import start_scheduler, stop_scheduler
from backend.app.routers import price, predict, backtest, accuracy, news, assets, websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")

# Initialize database schema
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Trading Signal Engine & Background Schedulers...")
    start_scheduler()
    yield
    logger.info("Shutting down AI Trading Signal Engine...")
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Asset AI Trading Signal Dashboard with Real Market Data, FinBERT Sentiment & SHAP Explainability",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(assets.router, prefix=settings.API_V1_STR)
app.include_router(price.router, prefix=settings.API_V1_STR)
app.include_router(predict.router, prefix=settings.API_V1_STR)
app.include_router(backtest.router, prefix=settings.API_V1_STR)
app.include_router(accuracy.router, prefix=settings.API_V1_STR)
app.include_router(news.router, prefix=settings.API_V1_STR)
app.include_router(websocket.router)

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for container orchestrators and uptime monitors."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "connected",
        "engine": "active"
    }

# Frontend Static Assets directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

if (FRONTEND_DIR / "index.html").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend_root():
        return FileResponse(FRONTEND_DIR / "index.html")
