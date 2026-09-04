from fastapi import APIRouter, HTTPException
from ai.inference import get_backtest
from backend.app.schemas.schemas import BacktestResponse

router = APIRouter(prefix="/backtest", tags=["Backtest"])

@router.get("/{ticker}", response_model=BacktestResponse)
def get_asset_backtest(ticker: str):
    """
    Returns realistic transaction-cost-aware backtesting metrics and equity curve comparisons.
    """
    try:
        result = get_backtest(ticker)
        return BacktestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtesting execution failed for {ticker}: {str(e)}")
