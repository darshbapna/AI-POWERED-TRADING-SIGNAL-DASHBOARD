import logging
from datetime import datetime
import numpy as np
import pandas as pd

from ai.data_layer.provider import get_ohlcv, ASSET_REGISTRY
from ai.features.cross_asset import build_features, FEATURE_COLUMNS
from ai.models.trainer import load_or_train_model
from ai.explainability.shap_explainer import explain_prediction
from ai.sentiment.pipeline import compute_sentiment_score
from ai.backtesting.engine import run_backtest

logger = logging.getLogger(__name__)

def get_feature_snapshot(ticker: str) -> dict:
    """Returns the latest technical indicators and feature snapshot for charting overlay."""
    df_prices = get_ohlcv(ticker, start="2023-01-01")
    df_features = build_features(ticker, df_prices)
    latest = df_features.iloc[-1]
    
    return {
        "ticker": ticker,
        "timestamp": latest["timestamp"].isoformat() + "Z",
        "close": round(float(latest["close"]), 2),
        "rsi": round(float(latest["rsi_14"]), 2),
        "macd": round(float(latest["macd"]), 2),
        "macd_signal": round(float(latest["macd_signal"]), 2),
        "macd_hist": round(float(latest["macd_hist"]), 2),
        "bb_upper": round(float(latest["bb_upper"]), 2),
        "bb_middle": round(float(latest["bb_middle"]), 2),
        "bb_lower": round(float(latest["bb_lower"]), 2),
        "ema_20": round(float(latest["ema_20"]), 2),
        "ema_50": round(float(latest["ema_50"]), 2),
        "sentiment_score": round(float(latest["sentiment_score"]), 2),
        "realized_volatility_pct": round(float(latest["realized_volatility"] * 100), 2)
    }

def predict(ticker: str) -> dict:
    """
    Core AI inference function.
    Combines model prediction probabilities, SHAP explainability drivers, and top news catalysts.
    """
    model_container = load_or_train_model(ticker)
    
    # Fetch price history & compute cross-asset features
    cross_dict = {
        "SPY": get_ohlcv("SPY", start="2023-01-01"),
        "GLD": get_ohlcv("GLD", start="2023-01-01"),
        "DX-Y.NYB": get_ohlcv("DX-Y.NYB", start="2023-01-01"),
        "USO": get_ohlcv("USO", start="2023-01-01"),
        "USDINR=X": get_ohlcv("USDINR=X", start="2023-01-01")
    }
    
    df_prices = get_ohlcv(ticker, start="2023-01-01")
    df_features = build_features(ticker, df_prices, cross_dict)
    
    # Incorporate live news sentiment score into feature row
    sentiment_data = compute_sentiment_score(ticker)
    df_features.loc[df_features.index[-1], "sentiment_score"] = sentiment_data["score"]
    
    latest_row = df_features.iloc[-1]
    
    # Scale and predict
    model = model_container.model
    scaler = model_container.scaler
    raw_X = latest_row[FEATURE_COLUMNS].values.reshape(1, -1)
    scaled_X = scaler.transform(raw_X) if scaler else raw_X
    
    if hasattr(model, "predict_proba"):
        prob_up = float(model.predict_proba(scaled_X)[0, 1])
    else:
        prob_up = float(model.predict(scaled_X)[0])

    # Classify signal
    if prob_up >= 0.70:
        signal = "STRONG BUY"
        signal_code = "BUY"
    elif prob_up >= 0.58:
        signal = "BUY"
        signal_code = "BUY"
    elif prob_up <= 0.30:
        signal = "STRONG SELL"
        signal_code = "SELL"
    elif prob_up <= 0.42:
        signal = "SELL"
        signal_code = "SELL"
    else:
        signal = "HOLD"
        signal_code = "HOLD"

    confidence = round(float(prob_up if prob_up >= 0.5 else (1.0 - prob_up)), 3)
    
    # SHAP explanations in plain English
    shap_drivers = explain_prediction(model_container, latest_row, top_k=5)
    
    asset_meta = ASSET_REGISTRY.get(ticker, {"name": ticker, "category": "Asset"})
    from ai.data_layer.calendar import is_market_open
    m_info = is_market_open(ticker)
    
    return {
        "ticker": ticker,
        "name": asset_meta.get("name", ticker),
        "category": asset_meta.get("category", "Asset"),
        "instrument_type": asset_meta.get("instrument_type", "EQUITY"),
        "is_equity": asset_meta.get("is_equity", True),
        "execution_vehicle": asset_meta.get("execution_vehicle", "Corporate Equity Shares"),
        "instrument_note": asset_meta.get("instrument_note", "Corporate Equity Shares"),
        "current_price": round(float(latest_row["close"]), 2),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "exchange": m_info.get("exchange", "Exchange"),
        "timezone_id": m_info.get("timezone_id", "UTC"),
        "timezone_code": m_info.get("timezone_code", "UTC"),
        "exchange_local_time": m_info.get("local_time", ""),
        "is_market_open": m_info.get("is_open", True),
        "exchange_session": m_info.get("session", "Regular Session"),
        "status_message": m_info.get("status_message", ""),
        "signal": signal,
        "signal_code": signal_code,
        "probability_up": round(prob_up, 3),
        "confidence": confidence,
        "horizon_days": 5,
        "model_version": "v1.0-gbdt",
        "shap_drivers": shap_drivers,
        "top_headlines": sentiment_data.get("top_drivers", [])
    }

def get_backtest(ticker: str) -> dict:
    """Executes transaction-cost-aware backtest for the asset."""
    return run_backtest(ticker)
