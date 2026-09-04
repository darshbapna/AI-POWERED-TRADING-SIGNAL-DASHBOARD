# Quantitative Methodology & Financial Engineering Guide

## 1. Mathematical Feature Engineering

### 1.1 Momentum & Trend
- **Relative Strength Index (RSI - 14 Days)**:
  $$RS = \frac{\text{EMA}_{14}(\text{Gain})}{\text{EMA}_{14}(\text{Loss})}, \quad \text{RSI} = 100 - \frac{100}{1 + RS}$$
- **Moving Average Convergence Divergence (MACD 12, 26, 9)**:
  $$\text{MACD Line} = \text{EMA}_{12}(P) - \text{EMA}_{26}(P)$$
  $$\text{Signal Line} = \text{EMA}_9(\text{MACD Line})$$
  $$\text{Histogram} = \text{MACD Line} - \text{Signal Line}$$
- **Bollinger Bands ($20\text{d}, 2\sigma$)**:
  $$\text{Middle Band} = \text{SMA}_{20}(P), \quad \text{Upper/Lower} = \text{SMA}_{20}(P) \pm 2\sigma_{20}(P)$$
- **Realized Volatility**:
  $$\sigma_{\text{ann}} = \sqrt{252} \times \text{std}\left(\ln\frac{P_t}{P_{t-1}}\right)_{20\text{d}}$$

### 1.2 Cross-Asset Intermarket Analysis
1. **Gold vs. US Dollar Index (DXY) 20-day Rolling Correlation**:
   - Gold priced in USD generally exhibits strong negative correlation ($\rho < -0.6$).
   - Decoupling ($\rho > 0$) signals stagflation, geopolitical flight to safety, or sovereign reserve diversification.
2. **Nifty 50 vs. S&P 500 (SPY)**:
   - Captures global risk-on beta spillover and foreign institutional investment (FII) momentum.
3. **Crude Oil (Brent/WTI) vs. USD/INR**:
   - India imports $>85\%$ of crude oil. Spikes in crude oil increase current account deficits and put direct depreciation pressure on INR.
4. **VIX Regimes & 10Y-2Y Treasury Yield Spread**:
   - Macro risk-on/risk-off regime filters.

---

## 2. Live News Sentiment Pipeline (FinBERT + Time Decay)

Financial language is context-specific (e.g., *"debt reduction boosts cash flow"* is positive, whereas standard sentiment models might mark *"debt"* as negative).
We utilize **FinBERT** (ProsusAI/FinBERT) with continuous sentiment polarity $s_i \in [-1.0, +1.0]$.

### Exponential Time-Decay Weighting
For any news item published $\Delta t$ hours ago:
$$w_i = 0.5^{\frac{\Delta t}{12}}$$
$$\bar{S}_t = \frac{\sum_{i} w_i \cdot s_i}{\sum_{i} w_i}$$
News from 12 hours ago receives 50% weight, while 24 hours ago receives 25% weight.

---

## 3. Walk-Forward Validation & Model Training
To strictly eliminate lookahead bias and data leakage:
- **No random train-test splitting**.
- **Expanding window walk-forward validation**: 8 to 12 sequential folds over 3+ years of historical data.
- Standardized feature scalers fitted *strictly* on training windows.
- Models: **Gradient Boosting Decision Trees / XGBoost** tuned per individual asset class.

---

## 4. Realistic Backtesting Cost Model

| Asset Class | Brokerage + Exchange Fees | Statutory Charges / STT / Spread | Round-Trip Cost Basis |
| :--- | :--- | :--- | :--- |
| **Indian Equities / Indices** | 0.05% brokerage | 0.1% STT (delivery) / 0.0125% intraday | **15 bps** |
| **MCX Metals / Energy** | ₹20/order or 0.02% | MCX turnover charges + GST | **5 bps** |
| **Forex** | Spread-based | Interbank bid-ask spread | **3 bps** |
| **Crypto** | Binance Maker/Taker | 0.10% per trade | **20 bps** |
| **US Sector ETFs** | Zero commission | Bid-ask spread on liquid ETFs | **1.5 bps** |

---

## 5. SHAP Explainability & Translation Layer
We compute SHAP (SHapley Additive exPlanations) values for every real-time feature vector:
$$\hat{f}(x) = \phi_0 + \sum_{j=1}^{M} \phi_j$$
Where $\phi_j$ represents the marginal contribution of feature $j$ to the prediction log-odds.
The translation engine categorizes top positive and negative contributors and converts them into natural language explanations coupled with news catalysts.
