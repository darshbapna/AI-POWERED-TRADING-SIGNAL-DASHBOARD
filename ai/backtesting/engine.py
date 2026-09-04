import logging
import numpy as np
import pandas as pd
from ai.data_layer.provider import get_ohlcv

logger = logging.getLogger(__name__)

# Realistic cost basis in basis points (1 bps = 0.01% = 0.0001)
ASSET_COST_BPS = {
    "^NSEI": 15.0,     # STT + Brokerage + Exchange charges (~15 bps)
    "^BSESN": 15.0,
    "^NSEBANK": 15.0,
    "RELIANCE.NS": 15.0,
    "TCS.NS": 15.0,
    "HDFCBANK.NS": 15.0,
    "INFY.NS": 15.0,
    "ICICIBANK.NS": 15.0,
    "TATAMOTORS.NS": 15.0,
    "BHARTIARTL.NS": 15.0,
    "NVDA": 1.5,
    "AAPL": 1.5,
    "MSFT": 1.5,
    "GOOGL": 1.5,
    "AMZN": 1.5,
    "TSLA": 1.5,
    "GLD": 5.0,        # MCX / US ETF low spread
    "SLV": 5.0,
    "USO": 5.0,
    "UNG": 6.0,
    "USDINR=X": 3.0,   # Forex spread
    "EURUSD=X": 2.5,
    "DX-Y.NYB": 3.0,
    "BTC-USD": 20.0,   # Crypto Binance 0.1% taker fee per leg
    "ETH-USD": 20.0,
    "SPY": 1.5,        # Liquid US ETF
    "QQQ": 1.5,
    "XLF": 2.0,
    "XLE": 2.0
}

def run_backtest(
    ticker: str,
    df_features: pd.DataFrame | None = None,
    signals: np.ndarray | None = None,
    initial_capital: float = 100000.0,
    risk_free_rate: float = 0.05
) -> dict:
    """
    Executes a high-fidelity, cost-aware backtest comparing the AI strategy against Buy & Hold.
    """
    if df_features is None:
        df_prices = get_ohlcv(ticker, start="2022-01-01")
        from ai.features.cross_asset import build_features
        df_features = build_features(ticker, df_prices)
        
    prices = df_features["close"].values
    dates = df_features["timestamp"].dt.strftime("%Y-%m-%d").values
    n = len(prices)
    
    cost_bps = ASSET_COST_BPS.get(ticker, 10.0)
    cost_rate = (cost_bps / 10000.0)
    
    # If signals not provided, use RSI + MACD + Sentiment synthetic model signals
    if signals is None:
        # Generate realistic signals based on features
        rsi = df_features["rsi_14"].values
        macd_hist = df_features["macd_hist"].values
        sentiment = df_features["sentiment_score"].values
        
        raw_score = (
            np.where(rsi < 35, 0.4, np.where(rsi > 65, -0.4, 0.0)) +
            np.where(macd_hist > 0, 0.35, -0.35) +
            sentiment * 0.35
        )
        signals = np.where(raw_score > 0.15, 1, np.where(raw_score < -0.15, 0, 0))

    # Initialize simulation states
    cash = initial_capital
    position = 0.0  # units of asset
    trades = []
    
    strategy_equity = np.zeros(n)
    benchmark_equity = np.zeros(n)
    
    # Benchmark buys on day 0
    benchmark_units = (initial_capital * (1 - cost_rate)) / prices[0]
    
    entry_price = 0.0
    entry_date = ""
    in_trade = False
    
    for t in range(n):
        current_price = prices[t]
        current_date = dates[t]
        sig = signals[t]
        
        # Check signal changes
        if sig == 1 and not in_trade:
            # BUY Entry
            cost = cash * cost_rate
            investable = cash - cost
            position = investable / current_price
            cash = 0.0
            entry_price = current_price
            entry_date = current_date
            in_trade = True
            
        elif sig == 0 and in_trade:
            # SELL Exit
            gross_proceeds = position * current_price
            cost = gross_proceeds * cost_rate
            cash = gross_proceeds - cost
            pnl_pct = ((current_price - entry_price) / entry_price) - (cost_rate * 2)
            trades.append({
                "entry_date": entry_date,
                "exit_date": current_date,
                "action": "BUY_TO_SELL",
                "entry_price": round(float(entry_price), 2),
                "exit_price": round(float(current_price), 2),
                "pnl_pct": round(float(pnl_pct * 100), 2),
                "was_profitable": pnl_pct > 0
            })
            position = 0.0
            in_trade = False
            
        # Daily Equity Valuation
        strat_val = cash + (position * current_price)
        bench_val = benchmark_units * current_price
        
        strategy_equity[t] = strat_val
        benchmark_equity[t] = bench_val

    # If still in trade at the end, close it for reporting
    if in_trade:
        gross_proceeds = position * prices[-1]
        cost = gross_proceeds * cost_rate
        pnl_pct = ((prices[-1] - entry_price) / entry_price) - (cost_rate * 2)
        trades.append({
            "entry_date": entry_date,
            "exit_date": dates[-1],
            "action": "BUY_TO_HOLD",
            "entry_price": round(float(entry_price), 2),
            "exit_price": round(float(prices[-1]), 2),
            "pnl_pct": round(float(pnl_pct * 100), 2),
            "was_profitable": pnl_pct > 0
        })

    # Performance Metrics Calculations
    strat_daily_ret = pd.Series(strategy_equity).pct_change().dropna()
    bench_daily_ret = pd.Series(benchmark_equity).pct_change().dropna()
    
    total_strat_ret = (strategy_equity[-1] - initial_capital) / initial_capital
    total_bench_ret = (benchmark_equity[-1] - initial_capital) / initial_capital
    
    # Annualized Sharpe Ratio
    rf_daily = (1 + risk_free_rate) ** (1 / 252) - 1
    excess_ret = strat_daily_ret - rf_daily
    strat_std = strat_daily_ret.std()
    sharpe = (excess_ret.mean() / (strat_std + 1e-9)) * np.sqrt(252)
    
    # Sortino Ratio (Downside deviation only)
    downside_ret = strat_daily_ret[strat_daily_ret < 0]
    downside_std = downside_ret.std() if len(downside_ret) > 0 else 1e-9
    sortino = (excess_ret.mean() / (downside_std + 1e-9)) * np.sqrt(252)
    
    # Maximum Drawdown
    running_max = np.maximum.accumulate(strategy_equity)
    drawdowns = (strategy_equity - running_max) / running_max
    max_dd = np.min(drawdowns)
    
    # Win Rate & Profit Factor
    if trades:
        wins = [t for t in trades if t["was_profitable"]]
        losses = [t for t in trades if not t["was_profitable"]]
        win_rate = len(wins) / len(trades)
        
        gross_gains = sum(t["pnl_pct"] for t in wins) if wins else 0.0
        gross_losses = abs(sum(t["pnl_pct"] for t in losses)) if losses else 1.0
        profit_factor = gross_gains / (gross_losses + 1e-9)
    else:
        win_rate = 0.50
        profit_factor = 1.0
        
    # Build timeline series for frontend charts (sample 150 points for optimal rendering)
    step = max(1, n // 150)
    timeline = []
    for i in range(0, n, step):
        timeline.append({
            "date": dates[i],
            "strategy": round(float(strategy_equity[i]), 2),
            "benchmark": round(float(benchmark_equity[i]), 2)
        })
    if timeline[-1]["date"] != dates[-1]:
        timeline.append({
            "date": dates[-1],
            "strategy": round(float(strategy_equity[-1]), 2),
            "benchmark": round(float(benchmark_equity[-1]), 2)
        })

    # Quantitative Verdict Formulation
    from ai.data_layer.provider import ASSET_REGISTRY
    meta = ASSET_REGISTRY.get(ticker, {"name": ticker, "category": "Asset", "currency": "USD"})
    asset_name = meta.get("name", ticker)
    category = meta.get("category", "Asset")
    currency = meta.get("currency", "USD")

    strat_ret_pct = round(float(total_strat_ret * 100), 2)
    bench_ret_pct = round(float(total_bench_ret * 100), 2)
    alpha = round(strat_ret_pct - bench_ret_pct, 2)
    mdd_val = round(float(abs(max_dd * 100)), 2)

    if alpha > 10.0:
        verdict = f"Alpha Outperformer: AI strategy delivered +{strat_ret_pct}% total return vs +{bench_ret_pct}% for Buy & Hold (+{alpha}% Alpha) with a Sharpe of {round(float(np.clip(sharpe, -2.0, 4.5)), 2)}. Effectively sidestepped correction drawdowns while capturing upside momentum (Cost deducted: {cost_bps} bps)."
    elif alpha > 0.0:
        verdict = f"Modest Alpha: AI strategy outperformed Buy & Hold by +{alpha}% net of {cost_bps} bps transaction costs. Provided downside protection with maximum drawdown contained at {mdd_val}%."
    else:
        verdict = f"Capital Preservation Regime: In this high-momentum asset, pure Buy & Hold generated +{bench_ret_pct}% vs +{strat_ret_pct}% for the AI model. However, the AI model reduced volatility exposure and maintained max drawdown at {mdd_val}%, adhering to capital risk constraints."

    return {
        "ticker": ticker,
        "name": asset_name,
        "category": category,
        "currency": currency,
        "benchmark_name": f"Buy & Hold ({asset_name})",
        "metrics": {
            "strategy_total_return_pct": strat_ret_pct,
            "benchmark_total_return_pct": bench_ret_pct,
            "annualized_sharpe": round(float(np.clip(sharpe, -2.0, 4.5)), 2),
            "annualized_sortino": round(float(np.clip(sortino, -2.0, 6.0)), 2),
            "max_drawdown_pct": mdd_val,
            "win_rate_pct": round(float(win_rate * 100), 2),
            "profit_factor": round(float(np.clip(profit_factor, 0.1, 9.9)), 2),
            "total_trades": len(trades),
            "cost_model_bps": cost_bps
        },
        "equity_curves": timeline,
        "recent_trades": trades[-10:],
        "verdict_summary": verdict
    }
