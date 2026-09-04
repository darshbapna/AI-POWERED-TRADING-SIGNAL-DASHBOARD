import numpy as np
import pandas as pd

def compute_sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()

def compute_ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average: EMA_t = alpha * P_t + (1 - alpha) * EMA_{t-1}."""
    return series.ewm(span=window, adjust=False).mean()

def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI - 14):
    RS = EMA_gain / EMA_loss, RSI = 100 - (100 / (1 + RS))
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0))
    loss = (-delta.where(delta < 0, 0.0))
    
    # Wilder's Smoothing (alpha = 1 / window)
    avg_gain = gain.ewm(alpha=1.0 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, min_periods=window, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi

def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD (12, 26, 9):
    MACD Line = EMA(12) - EMA(26)
    Signal Line = EMA(9) of MACD Line
    Histogram = MACD Line - Signal Line
    """
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist

def compute_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands:
    Middle = SMA(20)
    Upper = Middle + 2 * std(20)
    Lower = Middle - 2 * std(20)
    """
    middle = compute_sma(series, window)
    std = series.rolling(window=window).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    return upper, middle, lower

def compute_obv(df: pd.DataFrame) -> pd.Series:
    """
    On-Balance Volume (OBV):
    OBV_t = OBV_{t-1} + Volume if Close_t > Close_{t-1} else -Volume
    """
    price_change = df["close"].diff()
    direction = np.where(price_change > 0, 1.0, np.where(price_change < 0, -1.0, 0.0))
    obv = (direction * df["volume"]).cumsum()
    return pd.Series(obv, index=df.index)

def compute_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Volume-Weighted Average Price (VWAP):
    VWAP = cumsum(Typical Price * Volume) / cumsum(Volume)
    Typical Price = (High + Low + Close) / 3
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    cum_pv = (typical_price * df["volume"]).cumsum()
    cum_vol = df["volume"].cumsum()
    vwap = cum_pv / (cum_vol + 1e-9)
    return pd.Series(vwap, index=df.index)

def compute_realized_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Realized Volatility:
    Annualized standard deviation of daily log returns: sqrt(252) * std(log(P_t / P_{t-1}))
    """
    log_returns = np.log(series / series.shift(1))
    rolling_std = log_returns.rolling(window=window).std()
    annualized_vol = rolling_std * np.sqrt(252)
    return annualized_vol

def apply_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes and appends all indicators to OHLCV dataframe."""
    res = df.copy()
    res["sma_10"] = compute_sma(res["close"], 10)
    res["sma_20"] = compute_sma(res["close"], 20)
    res["sma_50"] = compute_sma(res["close"], 50)
    res["sma_200"] = compute_sma(res["close"], 200)
    
    res["ema_10"] = compute_ema(res["close"], 10)
    res["ema_20"] = compute_ema(res["close"], 20)
    res["ema_50"] = compute_ema(res["close"], 50)
    res["ema_200"] = compute_ema(res["close"], 200)
    
    res["rsi_14"] = compute_rsi(res["close"], 14)
    
    macd_line, signal_line, macd_hist = compute_macd(res["close"], 12, 26, 9)
    res["macd"] = macd_line
    res["macd_signal"] = signal_line
    res["macd_hist"] = macd_hist
    
    bb_up, bb_mid, bb_low = compute_bollinger_bands(res["close"], 20, 2.0)
    res["bb_upper"] = bb_up
    res["bb_middle"] = bb_mid
    res["bb_lower"] = bb_low
    res["bb_bandwidth"] = (bb_up - bb_low) / (bb_mid + 1e-9)
    res["bb_pct_b"] = (res["close"] - bb_low) / (bb_up - bb_low + 1e-9)
    
    res["obv"] = compute_obv(res)
    res["vwap"] = compute_vwap(res)
    res["vwap_dev"] = (res["close"] - res["vwap"]) / (res["vwap"] + 1e-9)
    res["realized_volatility"] = compute_realized_volatility(res["close"], 20)
    
    return res
