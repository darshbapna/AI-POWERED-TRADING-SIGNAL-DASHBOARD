from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean, 
    ForeignKey, Index, Text
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    interval = Column(String(16), default="1d")

    __table_args__ = (
        Index("idx_prices_ticker_timestamp", "ticker", "timestamp", unique=True),
    )


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    headline = Column(Text, nullable=False)
    source = Column(String(64), nullable=True)
    url = Column(String(255), nullable=True)
    sentiment_score = Column(Float, default=0.0)  # -1.0 to +1.0
    finbert_label = Column(String(16), default="neutral")  # positive, negative, neutral


class FeatureRecord(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    ema_200 = Column(Float, nullable=True)
    obv = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    realized_volatility = Column(Float, nullable=True)
    sentiment_score = Column(Float, default=0.0)
    cross_corr_gold_dxy = Column(Float, nullable=True)
    cross_corr_nifty_spy = Column(Float, nullable=True)
    cross_corr_crude_usdinr = Column(Float, nullable=True)
    relative_strength_spy = Column(Float, nullable=True)
    vix = Column(Float, nullable=True)
    yield_spread = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_features_ticker_timestamp", "ticker", "timestamp", unique=True),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    signal = Column(String(16), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)   # 0.0 - 1.0
    price_at_prediction = Column(Float, nullable=False)
    horizon_days = Column(Integer, default=5)
    model_version = Column(String(32), default="v1.0-gbdt")
    shap_summary = Column(Text, nullable=True)  # JSON string of top drivers

    outcome = relationship("PredictionOutcome", back_populates="prediction", uselist=False)


class PredictionOutcome(Base):
    __tablename__ = "prediction_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, unique=True)
    outcome_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    actual_price = Column(Float, nullable=False)
    price_change_pct = Column(Float, nullable=False)
    actual_direction = Column(String(16), nullable=False)  # UP, DOWN, FLAT
    was_correct = Column(Boolean, nullable=False)

    prediction = relationship("Prediction", back_populates="outcome")
