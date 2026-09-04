from fastapi import APIRouter, Query, HTTPException
from ai.data_layer.provider import get_ohlcv, ASSET_REGISTRY
from ai.features.indicators import apply_all_indicators
from backend.app.schemas.schemas import PriceHistoryResponse, PriceBar

router = APIRouter(prefix="/price", tags=["Price"])

@router.get("/{ticker}", response_model=PriceHistoryResponse)
def get_price_history(
    ticker: str,
    interval: str = Query("1d", pattern="^(1m|5m|1h|1d)$"),
    days: int = Query(90, ge=7, le=1000)
):
    """Returns OHLCV price history and computed technical indicators."""
    meta = ASSET_REGISTRY.get(ticker, {"name": ticker})
    
    from ai.data_layer.calendar import is_market_open
    m_info = is_market_open(ticker)

    try:
        df = get_ohlcv(ticker, interval=interval)
        df_indicators = apply_all_indicators(df)
        
        # Filter to requested lookback days
        df_filtered = df_indicators.tail(days).reset_index(drop=True)
        
        bars = []
        for _, row in df_filtered.iterrows():
            ts_str = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row["timestamp"], "strftime") else str(row["timestamp"])
            bars.append(PriceBar(
                timestamp=ts_str,
                open=round(float(row["open"]), 2),
                high=round(float(row["high"]), 2),
                low=round(float(row["low"]), 2),
                close=round(float(row["close"]), 2),
                volume=round(float(row["volume"]), 0),
                rsi=round(float(row["rsi_14"]), 2) if not row.isna().get("rsi_14", True) else None,
                macd=round(float(row["macd"]), 2) if not row.isna().get("macd", True) else None,
                macd_signal=round(float(row["macd_signal"]), 2) if not row.isna().get("macd_signal", True) else None,
                macd_hist=round(float(row["macd_hist"]), 2) if not row.isna().get("macd_hist", True) else None,
                bb_upper=round(float(row["bb_upper"]), 2) if not row.isna().get("bb_upper", True) else None,
                bb_middle=round(float(row["bb_middle"]), 2) if not row.isna().get("bb_middle", True) else None,
                bb_lower=round(float(row["bb_lower"]), 2) if not row.isna().get("bb_lower", True) else None,
                ema_20=round(float(row["ema_20"]), 2) if not row.isna().get("ema_20", True) else None,
                ema_50=round(float(row["ema_50"]), 2) if not row.isna().get("ema_50", True) else None,
            ))
            
        return PriceHistoryResponse(
            ticker=ticker,
            name=meta.get("name", ticker),
            interval=interval,
            exchange=m_info.get("exchange", "Exchange"),
            timezone_id=m_info.get("timezone_id", "UTC"),
            timezone_code=m_info.get("timezone_code", "UTC"),
            exchange_local_time=m_info.get("local_time", ""),
            is_market_open=m_info.get("is_open", True),
            status_message=m_info.get("status_message", ""),
            bars=bars
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price data for {ticker}: {str(e)}")
