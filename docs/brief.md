# Project Brief: AI-Powered Multi-Asset Trading Signal Dashboard

## 1. Overview
The AI-Powered Trading Signal Dashboard is an end-to-end quantitative intelligence system that combines real market price action, cross-asset macro relationships, and live financial news sentiment (FinBERT) to generate high-conviction 5-trading-day directional forecasts ($y \in \{0, 1\}$).

## 2. Asset Coverage Matrix

| Asset Class | Asset / Instrument | Ticker Symbol | Primary Source | Exchange / Hours |
| :--- | :--- | :--- | :--- | :--- |
| **Indian Indices** | Nifty 50 | `^NSEI` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | Sensex | `^BSESN` | Zerodha Kite / yfinance | BSE (09:15–15:30 IST, Mon–Fri) |
| | Bank Nifty | `^NSEBANK` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| **Indian Equities** | Reliance Industries | `RELIANCE.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | Tata Consultancy Services | `TCS.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | HDFC Bank | `HDFCBANK.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | Infosys | `INFY.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | ICICI Bank | `ICICIBANK.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | Tata Motors | `TATAMOTORS.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| | Bharti Airtel | `BHARTIARTL.NS` | Zerodha Kite / yfinance | NSE (09:15–15:30 IST, Mon–Fri) |
| **US Equities** | NVIDIA Corp | `NVDA` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| | Apple Inc | `AAPL` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| | Microsoft Corp | `MSFT` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| | Alphabet Inc | `GOOGL` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| | Amazon.com Inc | `AMZN` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| | Tesla Inc | `TSLA` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| **Precious Metals**| Gold | `GLD` (`GC=F`) | Kite (MCX) / yfinance | MCX / US (09:00–23:30 IST) |
| | Silver | `SLV` (`SI=F`) | Kite (MCX) / yfinance | MCX / US (09:00–23:30 IST) |
| **Energy** | Crude Oil | `USO` (`CL=F`) | Kite (MCX) / yfinance | MCX / NYMEX |
| | Natural Gas | `UNG` (`NG=F`) | Kite (MCX) / yfinance | MCX / NYMEX |
| **Forex** | USD / INR | `USDINR=X` | Kite (Currency) / yfinance | Interbank (24/5) |
| | EUR / USD | `EURUSD=X` | Kite (Currency) / yfinance | Forex (24/5) |
| | US Dollar Index | `DX-Y.NYB` | yfinance / ICE | ICE (24/5) |
| **Crypto** | Bitcoin | `BTC-USD` | Binance / CoinGecko | 24/7/365 |
| | Ethereum | `ETH-USD` | Binance / CoinGecko | 24/7/365 |
| **Sector ETFs** | SPDR S&P 500 | `SPY` | Alpaca / yfinance | NYSE (09:30–16:00 EST) |
| | Invesco QQQ | `QQQ` | Alpaca / yfinance | NASDAQ (09:30–16:00 EST) |
| | Financial Select | `XLF` | Alpaca / yfinance | NYSE (09:30–16:00 EST) |
| | Energy Select | `XLE` | Alpaca / yfinance | NYSE (09:30–16:00 EST) |

## 3. Prediction Horizon & Target Formulation
- **Horizon**: $T = 5$ trading days.
- **Classification Target**:
  $$y_t = \begin{cases} 1 & \text{if } \text{Close}_{t+5} > \text{Close}_t \\ 0 & \text{otherwise} \end{cases}$$
- **Signal Thresholds**:
  - Probability $\ge 0.60$: **STRONG BUY / BUY**
  - Probability $\le 0.40$: **STRONG SELL / SELL**
  - $0.40 < \text{Probability} < 0.60$: **HOLD / NEUTRAL**

## 4. Key Performance Targets
- **Sharpe Ratio**: $> 1.25$
- **Max Drawdown**: $< 12\%$
- **Win Rate**: $> 56\%$ across walk-forward folds
- **SHAP Explainability**: Top 5 quantitative feature attributions + Top 3 news catalyst headlines per inference.
