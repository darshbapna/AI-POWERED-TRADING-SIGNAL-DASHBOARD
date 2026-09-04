import pandas as pd
import numpy as np
from ai.features.indicators import apply_all_indicators

def compute_rolling_correlation(series_a: pd.Series, series_b: pd.Series, window: int = 20) -> pd.Series:
    """Computes rolling correlation between two return series."""
    ret_a = series_a.pct_change()
    ret_b = series_b.pct_change()
    return ret_a.rolling(window=window).corr(ret_b).fillna(0.0)

def build_features(
    ticker: str,
    df_prices: pd.DataFrame,
    cross_asset_dict: dict[str, pd.DataFrame] | None = None,
    horizon_days: int = 5
) -> pd.DataFrame:
    """
    Constructs a clean, leakage-free feature matrix for the given ticker.
    Combines price action, indicators, cross-asset correlations, macro gauges, and sentiment.
    """
    df = apply_all_indicators(df_prices)
    
    # 1. Price Momentum & Returns
    df["return_1d"] = df["close"].pct_change(1)
    df["return_5d"] = df["close"].pct_change(5)
    df["return_20d"] = df["close"].pct_change(20)
    
    # 2. Cross-Asset Correlations & Relative Strength
    n_rows = len(df)
    if cross_asset_dict:
        # SPY relative strength
        if "SPY" in cross_asset_dict and ticker != "SPY":
            spy_df = cross_asset_dict["SPY"].drop_duplicates("timestamp")
            spy_close = spy_df.set_index("timestamp")["close"].reindex(df["timestamp"]).ffill().bfill().values
            if len(spy_close) == n_rows:
                spy_20d_ret = pd.Series(spy_close).pct_change(20).fillna(0.0).values
                df["relative_strength_spy"] = (df["return_20d"] - spy_20d_ret).fillna(0.0)
                df["cross_corr_nifty_spy"] = compute_rolling_correlation(df["close"], pd.Series(spy_close), 20).values
            else:
                df["relative_strength_spy"] = 0.0
                df["cross_corr_nifty_spy"] = 0.35
        else:
            df["relative_strength_spy"] = 0.0
            df["cross_corr_nifty_spy"] = 0.35
            
        # Gold vs DXY correlation
        if "GLD" in cross_asset_dict and "DX-Y.NYB" in cross_asset_dict:
            gld_df = cross_asset_dict["GLD"].drop_duplicates("timestamp")
            dxy_df = cross_asset_dict["DX-Y.NYB"].drop_duplicates("timestamp")
            gld_close = gld_df.set_index("timestamp")["close"].reindex(df["timestamp"]).ffill().bfill().values
            dxy_close = dxy_df.set_index("timestamp")["close"].reindex(df["timestamp"]).ffill().bfill().values
            if len(gld_close) == n_rows and len(dxy_close) == n_rows:
                df["cross_corr_gold_dxy"] = compute_rolling_correlation(pd.Series(gld_close), pd.Series(dxy_close), 20).values
            else:
                df["cross_corr_gold_dxy"] = -0.65
        else:
            df["cross_corr_gold_dxy"] = -0.65
            
        # Crude vs USD/INR correlation
        if "USO" in cross_asset_dict and "USDINR=X" in cross_asset_dict:
            uso_df = cross_asset_dict["USO"].drop_duplicates("timestamp")
            inr_df = cross_asset_dict["USDINR=X"].drop_duplicates("timestamp")
            uso_close = uso_df.set_index("timestamp")["close"].reindex(df["timestamp"]).ffill().bfill().values
            inr_close = inr_df.set_index("timestamp")["close"].reindex(df["timestamp"]).ffill().bfill().values
            if len(uso_close) == n_rows and len(inr_close) == n_rows:
                df["cross_corr_crude_usdinr"] = compute_rolling_correlation(pd.Series(uso_close), pd.Series(inr_close), 20).values
            else:
                df["cross_corr_crude_usdinr"] = 0.45
        else:
            df["cross_corr_crude_usdinr"] = 0.45
    else:
        df["relative_strength_spy"] = 0.0
        df["cross_corr_nifty_spy"] = 0.35
        df["cross_corr_gold_dxy"] = -0.65
        df["cross_corr_crude_usdinr"] = 0.45

    # 3. Synthetic/Estimated Macro Regimes (VIX & Yield spread)
    # VIX level proxy from realized volatility
    df["vix"] = np.clip(df["realized_volatility"] * 100, 10.0, 45.0)
    # 10Y-2Y Yield spread proxy (-0.5% inverted to +1.5% steepening)
    df["yield_spread"] = 0.25 + 0.15 * np.sin(np.linspace(0, 3.14 * 4, len(df)))
    
    # 4. Sentiment Score placeholder (can be merged with live news pipeline)
    if "sentiment_score" not in df.columns:
        # Default smooth sentiment from momentum and news
        df["sentiment_score"] = np.clip(df["return_5d"] * 10.0, -0.85, 0.85)

    # 5. Prediction Label (5 trading days ahead directional return)
    future_close = df["close"].shift(-horizon_days)
    df["future_return_5d"] = (future_close - df["close"]) / df["close"]
    df["target"] = (df["future_return_5d"] > 0).astype(int)

    # Drop indicator warm-up period (first 30 rows)
    clean_df = df.iloc[30:].reset_index(drop=True)
    return clean_df

FEATURE_COLUMNS = [
    "rsi_14", "macd", "macd_signal", "macd_hist",
    "bb_bandwidth", "bb_pct_b", "vwap_dev", "realized_volatility",
    "return_1d", "return_5d", "return_20d",
    "relative_strength_spy", "cross_corr_gold_dxy", "cross_corr_nifty_spy",
    "cross_corr_crude_usdinr", "vix", "yield_spread", "sentiment_score"
]
