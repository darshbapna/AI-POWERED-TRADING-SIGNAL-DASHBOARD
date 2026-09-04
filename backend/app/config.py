import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "AI-Powered Trading Signal Dashboard"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{DATA_DIR / 'trading_dashboard.db'}"
    )
    
    # API Keys / Integrations (Optional with automatic live/cached fallback)
    KITE_API_KEY: str = os.getenv("KITE_API_KEY", "")
    KITE_SECRET: str = os.getenv("KITE_SECRET", "")
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    
    # Market & Model Settings
    DEFAULT_HORIZON_DAYS: int = 5
    PREDICTION_THRESHOLD_BUY: float = 0.58
    PREDICTION_THRESHOLD_SELL: float = 0.42
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]

settings = Settings()
