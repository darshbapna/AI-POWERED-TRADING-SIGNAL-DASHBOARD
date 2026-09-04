# API Contract: AI Trading Signal Dashboard

Specification of all FastAPI REST endpoints and WebSocket protocols.

---

## REST Endpoints

### 1. `GET /api/assets`
Returns list of all supported assets grouped by asset class with their latest real-time signal snapshot.
- **Response `200 OK`**:
```json
{
  "assets": [
    {
      "ticker": "^NSEI",
      "name": "Nifty 50",
      "asset_class": "Indian Indices",
      "current_price": 24820.50,
      "change_24h_pct": 0.65,
      "signal": "BUY",
      "confidence": 0.81,
      "is_market_open": true,
      "updated_at": "2026-08-21T14:30:00Z"
    }
  ]
}
```

---

### 2. `GET /api/price/{ticker}?interval=1d&days=90`
Returns historical OHLCV data alongside computed technical indicators (RSI, MACD, Bollinger Bands, EMA).
- **Path Parameters**:
  - `ticker` (str): e.g. `^NSEI`, `GLD`, `BTC-USD`
- **Query Parameters**:
  - `interval` (str, default: `1d`): `1m`, `5m`, `1h`, `1d`
  - `days` (int, default: `90`): Lookback window
- **Response `200 OK`**:
```json
{
  "ticker": "^NSEI",
  "name": "Nifty 50",
  "interval": "1d",
  "bars": [
    {
      "timestamp": "2026-08-21T00:00:00Z",
      "open": 24710.0,
      "high": 24850.2,
      "low": 24690.1,
      "close": 24820.5,
      "volume": 284000000,
      "rsi": 62.4,
      "macd": 114.2,
      "macd_signal": 98.6,
      "macd_hist": 15.6,
      "bb_upper": 25100.0,
      "bb_lower": 24300.0,
      "bb_middle": 24700.0,
      "ema_20": 24650.0,
      "ema_50": 24310.0
    }
  ]
}
```

---

### 3. `GET /api/predict/{ticker}`
Returns the latest AI model directional signal, probability confidence, SHAP feature drivers in plain English, and top driving news catalysts.
- **Response `200 OK`**:
```json
{
  "ticker": "^NSEI",
  "name": "Nifty 50",
  "timestamp": "2026-08-21T14:30:00Z",
  "signal": "STRONG BUY",
  "signal_code": "BUY",
  "confidence": 0.835,
  "horizon_days": 5,
  "model_version": "v1.0-gbdt",
  "shap_drivers": [
    {
      "feature": "rsi_14",
      "value": 28.4,
      "shap_impact": 0.412,
      "direction": "bullish",
      "explanation": "RSI is showing the asset is oversold (28.4) — strong upward mean-reversion pull"
    },
    {
      "feature": "sentiment_score",
      "value": 0.74,
      "shap_impact": 0.325,
      "direction": "bullish",
      "explanation": "News sentiment is strongly bullish (+0.74), reinforcing buyer momentum"
    },
    {
      "feature": "cross_corr_gold_dxy",
      "value": -0.88,
      "shap_impact": 0.218,
      "direction": "bullish",
      "explanation": "Gold and US Dollar inverse decoupling reinforces equity liquidity support"
    }
  ],
  "top_headlines": [
    {
      "headline": "India Q1 GDP growth accelerates to 7.8% on manufacturing surge",
      "source": "Economic Times",
      "sentiment_score": 0.88,
      "finbert_label": "positive",
      "published_at": "2026-08-21T11:00:00Z"
    }
  ]
}
```

---

### 4. `GET /api/backtest/{ticker}`
Returns the comprehensive backtesting evaluation for the asset with realistic transaction costs applied.
- **Response `200 OK`**:
```json
{
  "ticker": "^NSEI",
  "metrics": {
    "strategy_total_return_pct": 48.6,
    "benchmark_total_return_pct": 21.2,
    "annualized_sharpe": 1.74,
    "annualized_sortino": 2.31,
    "max_drawdown_pct": 8.4,
    "win_rate_pct": 64.2,
    "total_trades": 84,
    "profit_factor": 2.15,
    "cost_model_bps": 15
  },
  "equity_curves": [
    {
      "date": "2024-01-02",
      "strategy": 100000.0,
      "benchmark": 100000.0,
      "cash": 100000.0,
      "position": 0
    }
  ],
  "recent_trades": [
    {
      "entry_date": "2026-08-01",
      "exit_date": "2026-08-08",
      "action": "BUY",
      "entry_price": 24200.0,
      "exit_price": 24650.0,
      "pnl_pct": 1.86,
      "was_profitable": true
    }
  ]
}
```

---

### 5. `GET /api/accuracy/{ticker}`
Returns the rolling accuracy metrics (7d, 30d, all-time) and live T+5 prediction outcome audit logs.
- **Response `200 OK`**:
```json
{
  "ticker": "^NSEI",
  "summary": {
    "rolling_7d_accuracy_pct": 71.4,
    "rolling_30d_accuracy_pct": 68.2,
    "rolling_90d_accuracy_pct": 65.5,
    "all_time_accuracy_pct": 64.8,
    "total_verified_predictions": 128,
    "drift_status": "STABLE"
  },
  "outcomes": [
    {
      "prediction_id": "pred_1082",
      "prediction_date": "2026-08-14T09:15:00Z",
      "predicted_signal": "BUY",
      "predicted_confidence": 0.81,
      "price_at_prediction": 24350.0,
      "outcome_date": "2026-08-21T15:30:00Z",
      "actual_price": 24820.5,
      "actual_direction": "UP",
      "was_correct": true
    }
  ]
}
```

---

### 6. `GET /api/news/{ticker}`
Returns the latest scored news headlines with FinBERT polarity and time decay factors.

---

### 7. `GET /api/portfolio`
Returns multi-asset correlation matrix, asset ranking, and portfolio signal summary.

---

## WebSocket Protocols

### `WS /ws/live/{ticker}`
Streams real-time simulated or exchange live tick updates every 1-2 seconds.
- **Outbound Message**:
```json
{
  "type": "TICK",
  "ticker": "^NSEI",
  "timestamp": "2026-08-21T14:32:05Z",
  "price": 24824.75,
  "change": 4.25,
  "change_pct": 0.67,
  "volume": 284120000,
  "bar": {
    "open": 24820.0,
    "high": 24826.5,
    "low": 24818.0,
    "close": 24824.75,
    "volume": 12400
  }
}
```
