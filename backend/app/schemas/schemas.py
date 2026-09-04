from datetime import datetime
from pydantic import BaseModel, Field

class AssetSummary(BaseModel):
    ticker: str
    name: str
    asset_class: str
    instrument_type: str = "EQUITY"
    is_equity: bool = True
    execution_vehicle: str = "Corporate Equity Shares"
    instrument_note: str = "Corporate Equity Shares"
    current_price: float
    change_24h_pct: float
    signal: str
    signal_code: str
    confidence: float
    is_market_open: bool
    exchange_session: str
    exchange: str = "Exchange"
    timezone_id: str = "UTC"
    timezone_code: str = "UTC"
    exchange_local_time: str = ""
    status_message: str = ""
    updated_at: str

class AssetListResponse(BaseModel):
    assets: list[AssetSummary]
    total_count: int
    market_timestamp: str

class PriceBar(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    ema_20: float | None = None
    ema_50: float | None = None

class PriceHistoryResponse(BaseModel):
    ticker: str
    name: str
    interval: str
    instrument_type: str = "EQUITY"
    is_equity: bool = True
    execution_vehicle: str = "Corporate Equity Shares"
    instrument_note: str = "Corporate Equity Shares"
    exchange: str = "Exchange"
    timezone_id: str = "UTC"
    timezone_code: str = "UTC"
    exchange_local_time: str = ""
    is_market_open: bool = True
    status_message: str = ""
    bars: list[PriceBar]

class ShapDriver(BaseModel):
    feature: str
    feature_label: str
    value: float
    shap_impact: float
    direction: str
    explanation: str

class NewsItem(BaseModel):
    headline: str
    source: str | None = None
    sentiment_score: float
    finbert_label: str
    published_at: str
    hours_ago: float | None = None

class PredictResponse(BaseModel):
    ticker: str
    name: str
    category: str
    instrument_type: str = "EQUITY"
    is_equity: bool = True
    execution_vehicle: str = "Corporate Equity Shares"
    instrument_note: str = "Corporate Equity Shares"
    current_price: float
    timestamp: str
    exchange: str = "Exchange"
    timezone_id: str = "UTC"
    timezone_code: str = "UTC"
    exchange_local_time: str = ""
    is_market_open: bool = True
    exchange_session: str = ""
    status_message: str = ""
    signal: str
    signal_code: str
    probability_up: float
    confidence: float
    horizon_days: int
    model_version: str
    shap_drivers: list[ShapDriver]
    top_headlines: list[NewsItem]

class BacktestMetrics(BaseModel):
    strategy_total_return_pct: float
    benchmark_total_return_pct: float
    annualized_sharpe: float
    annualized_sortino: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    total_trades: int
    cost_model_bps: float

class EquityPoint(BaseModel):
    date: str
    strategy: float
    benchmark: float

class TradeRecord(BaseModel):
    entry_date: str
    exit_date: str
    action: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    was_profitable: bool

class BacktestResponse(BaseModel):
    ticker: str
    name: str
    category: str
    currency: str
    benchmark_name: str
    metrics: BacktestMetrics
    equity_curves: list[EquityPoint]
    recent_trades: list[TradeRecord]
    verdict_summary: str

class AccuracyPoint(BaseModel):
    date: str
    accuracy_7d: float
    accuracy_30d: float

class AccuracySummary(BaseModel):
    rolling_7d_accuracy_pct: float
    rolling_30d_accuracy_pct: float
    rolling_90d_accuracy_pct: float
    all_time_accuracy_pct: float
    total_verified_predictions: int
    drift_status: str

class PredictionOutcomeRecord(BaseModel):
    prediction_id: int | str
    ticker: str
    name: str
    category: str
    currency: str
    prediction_date: str
    predicted_signal: str
    predicted_confidence: float
    price_at_prediction: float
    outcome_date: str
    actual_price: float
    price_change_pct: float
    actual_direction: str
    was_correct: bool

class AccuracyResponse(BaseModel):
    ticker: str
    name: str
    category: str
    summary: AccuracySummary
    outcomes: list[PredictionOutcomeRecord]
    accuracy_timeline: list[AccuracyPoint]

class CorrelationPair(BaseModel):
    asset_a: str
    asset_b: str
    correlation: float

class PortfolioResponse(BaseModel):
    total_assets: int
    buy_signals_count: int
    sell_signals_count: int
    hold_signals_count: int
    top_picks: list[AssetSummary]
    correlation_matrix: list[CorrelationPair]
    macro_regime: str
