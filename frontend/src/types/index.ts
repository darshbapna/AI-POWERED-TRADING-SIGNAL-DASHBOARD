export interface AssetSummary {
  ticker: str;
  name: str;
  asset_class: str;
  current_price: number;
  change_24h_pct: number;
  signal: string;
  signal_code: string;
  confidence: number;
  is_market_open: boolean;
  exchange_session: string;
  updated_at: string;
}

export interface PriceBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  rsi?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;
  ema_20?: number;
  ema_50?: number;
}

export interface ShapDriver {
  feature: string;
  feature_label: string;
  value: number;
  shap_impact: number;
  direction: 'bullish' | 'bearish';
  explanation: string;
}

export interface NewsItem {
  headline: string;
  source?: string;
  sentiment_score: number;
  finbert_label: string;
  published_at: string;
  hours_ago?: number;
}

export interface PredictResponse {
  ticker: string;
  name: string;
  category: string;
  current_price: number;
  timestamp: string;
  signal: string;
  signal_code: string;
  probability_up: number;
  confidence: number;
  horizon_days: number;
  model_version: string;
  shap_drivers: ShapDriver[];
  top_headlines: NewsItem[];
}

export interface BacktestMetrics {
  strategy_total_return_pct: number;
  benchmark_total_return_pct: number;
  annualized_sharpe: number;
  annualized_sortino: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  profit_factor: number;
  total_trades: number;
  cost_model_bps: number;
}

export interface EquityPoint {
  date: string;
  strategy: number;
  benchmark: number;
}

export interface TradeRecord {
  entry_date: string;
  exit_date: string;
  action: string;
  entry_price: number;
  exit_price: number;
  pnl_pct: number;
  was_profitable: boolean;
}

export interface BacktestResponse {
  ticker: string;
  metrics: BacktestMetrics;
  equity_curves: EquityPoint[];
  recent_trades: TradeRecord[];
}

export interface AccuracyOutcome {
  prediction_id: string | number;
  prediction_date: string;
  predicted_signal: string;
  predicted_confidence: number;
  price_at_prediction: number;
  outcome_date: string;
  actual_price: number;
  price_change_pct: number;
  actual_direction: string;
  was_correct: boolean;
}

export interface AccuracyResponse {
  ticker: string;
  summary: {
    rolling_7d_accuracy_pct: number;
    rolling_30d_accuracy_pct: number;
    rolling_90d_accuracy_pct: number;
    all_time_accuracy_pct: number;
    total_verified_predictions: number;
    drift_status: string;
  };
  outcomes: AccuracyOutcome[];
}
