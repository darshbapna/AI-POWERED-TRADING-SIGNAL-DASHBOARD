# 🚀 AI-Powered Multi-Asset Trading Signal Dashboard (v2.0-PRO)

> **Multi-Asset • Indian Blue-Chips & US Tech Equities • Indices • Real Market Data • Live News Sentiment (FinBERT) • Leakage-Free Walk-Forward ML • SHAP Explainability • Transaction-Cost Backtesting**

An institutional-grade quantitative trading platform covering **29 total instruments** across **Indian Blue-Chip Companies**, **US Tech & Global Giants**, **Indian Indices**, **Precious Metals**, **Energy Commodities**, **Forex Pairs**, and **Crypto**.

---

## 📁 Repository Folder Structure (For GitHub Upload)

```text
trading-signal-dashboard/
│
├── .gitignore                     # Git ignore rules (virtualenvs, cache, DBs)
├── README.md                      # Comprehensive documentation & setup guide
├── requirements.txt               # Complete Python dependencies
├── Dockerfile                     # Container deployment image
├── docker-compose.yml             # Single-command Docker Compose stack
│
├── ai/                            # Quantitative AI & Modeling Layer
│   ├── __init__.py
│   ├── inference.py               # Top-level inference (predict, backtest, features)
│   ├── data_layer/                # Market Data & Exchange Schedules
│   │   ├── __init__.py
│   │   ├── calendar.py            # Market hours & exchange timezones (IST, EDT, UTC)
│   │   └── provider.py            # Real-time asset registry & OHLCV data provider
│   ├── features/                  # Quantitative Feature Engineering
│   │   ├── __init__.py
│   │   ├── indicators.py          # Pure Python indicators (RSI-14, MACD, BB, VWAP, Vol)
│   │   └── cross_asset.py         # Intermarket correlations & macro regime features
│   ├── sentiment/                 # News Sentiment & NLP Pipeline
│   │   ├── __init__.py
│   │   └── pipeline.py            # FinBERT polarity scoring with exponential time decay
│   ├── models/                    # Walk-Forward Validation & ML Models
│   │   ├── __init__.py
│   │   ├── trainer.py             # 8-12 fold walk-forward trainer & scaler isolation
│   │   └── artifacts/             # Serialized versioned model binaries (.pkl)
│   ├── backtesting/               # Realistic Cost-Aware Backtesting Engine
│   │   ├── __init__.py
│   │   └── engine.py              # Brokerage/STT friction deductions, Sharpe, Drawdown
│   └── explainability/            # Explainable AI (XAI) Layer
│       ├── __init__.py
│       └── shap_explainer.py      # TreeExplainer & plain-English rule translation
│
├── backend/                       # FastAPI High-Performance Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entrypoint, CORS, static mounting
│   │   ├── db/                    # SQLAlchemy SQLite Database & Models
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── models.py          # Price, Prediction, Outcome, Trade tables
│   │   ├── schemas/               # Pydantic Request & Response Schemas
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── routers/               # REST API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── assets.py          # /api/assets & /api/portfolio
│   │   │   ├── price.py           # /api/price/{ticker}
│   │   │   ├── predict.py         # /api/predict/{ticker}
│   │   │   ├── backtest.py        # /api/backtest/{ticker}
│   │   │   ├── accuracy.py        # /api/accuracy/{ticker}
│   │   │   └── websocket.py       # /ws/live/{ticker}
│   │   └── jobs/                  # APScheduler Background Automation
│   │       ├── __init__.py
│   │       └── scheduler.py       # Hourly predictions & daily T+5 outcome evaluations
│   └── tests/                     # Automated Test Suites
│       ├── __init__.py
│       ├── test_ai.py             # Math indicators & cross-asset feature unit tests
│       └── test_api.py            # REST endpoints & integration tests
│
├── frontend/                      # User Interface & Trading Terminal
│   ├── static/
│   │   └── index.html             # Bloomberg-style Dark Terminal SPA (Vanilla JS + Tailwind + Chart.js)
│   └── src/                       # Optional Modular React + TypeScript Components
│       ├── App.tsx
│       ├── components/
│       │   ├── PriceChart.tsx
│       │   ├── SignalCard.tsx
│       │   ├── ShapWaterfall.tsx
│       │   ├── BacktestView.tsx
│       │   └── AccuracyTracker.tsx
│       └── types/
│           └── index.ts
│
├── data/                          # Local data caching directory
│   └── signals.db
│
└── docs/                          # Quantitative Methodology & API Documentation
    ├── brief.md                   # Multi-asset platform specifications
    ├── api_contract.md            # Detailed REST & WebSocket API contracts
    └── methodology.md             # Quantitative ML, sentiment, and backtesting whitepaper
```

---

## 💡 Important Market Concept: Companies vs. Indices

In financial markets:
- **Corporate Equities (Companies)**: (e.g. *Reliance Industries*, *TCS*, *NVIDIA*, *Apple*) Represent purchasable shares of corporate stock. You directly buy and sell equity shares on cash exchanges (NSE, NASDAQ).
- **Benchmark Indices**: (e.g. *Nifty 50*, *Sensex*, *Bank Nifty*) Are mathematical benchmark baskets measuring overall market performance. **You cannot directly buy an index as a physical share.**
  - To gain exposure to an Index, traders/investors execute via:
    1. **Index Exchange Traded Funds (ETFs)**: e.g. `NIFTYBEES.NS`, `BANKBEES.NS`, `SPY`.
    2. **Index Futures & Options (F&O Derivatives)**: Trading Nifty/Bank Nifty futures contracts.
    3. **Underlying Constituent Basket Replication**.

Our dashboard cleanly distinguishes between **Corporate Equities** (direct share purchases) and **Benchmark Indices** (directional exposure via Index Futures / Index ETFs).

---

## ⚡ How to Run the Project (Step-by-Step)

### Option 1: Run Locally on Windows, Mac, or Linux

#### Step 1: Open Terminal / PowerShell and Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/trading-signal-dashboard.git
cd trading-signal-dashboard
```

#### Step 2: Create and Activate a Python Virtual Environment
```bash
# On Windows PowerShell:
python -m venv .venv
.venv\Scripts\Activate.ps1

# On macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Run the FastAPI Server & Interactive Web Terminal
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Step 5: Open the Interactive Terminal
Open your web browser and navigate to:
- **Trading Dashboard UI**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Run via Docker (Zero Configuration)

```bash
# Build and run with Docker Compose:
docker-compose up --build
```
Then visit **`http://localhost:8000/`**.

---

## 🧪 Running Automated Unit & Integration Tests

```bash
# Run AI engine, math indicators, and cross-asset feature tests
python -m unittest backend/tests/test_ai.py

# Run FastAPI REST endpoints and database verification tests
python -m unittest backend/tests/test_api.py
```

---

## 📤 How to Upload this Project to GitHub (Step-by-Step)

If you haven't uploaded it to your GitHub yet, run these commands inside the `trading-signal-dashboard` folder:

```bash
# 1. Initialize Git repository
git init

# 2. Add all project files
git add .

# 3. Commit your project
git commit -m "feat: complete AI-powered multi-asset trading signal dashboard v2.0"

# 4. Set default branch to main
git branch -M main

# 5. Link to your GitHub repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 🏛️ System Features & Highlights

1. **29 Total Instruments**: Covers Indian Blue-Chips, US Tech Giants, Indices, Precious Metals, Energy, Forex, and Crypto.
2. **Dynamic Live Exchange Clocks**: Real-time 1-second ticking clocks updating in the native exchange timezones (`Asia/Kolkata` IST, `America/New_York` EDT, `UTC`).
3. **FinBERT News NLP**: Continuous polarity $[-1.0, +1.0]$ with exponential time decay $0.5^{(\Delta t / 12)}$ and headline driver attribution.
4. **Walk-Forward ML Validation**: 8–12 sequential expanding folds with strictly isolated feature scalers to guarantee zero lookahead bias.
5. **Cost-Aware Realistic Backtesting**: Deducts statutory exchange fees, STT, and brokerage per market class.
6. **Plain-English SHAP Explainability**: Translates TreeExplainer Shapley vectors into clear causal reasoning.
7. **T+5 Accuracy Verification & Drift Tracker**: Evaluates frozen forecasts against 5-day future closing prices to monitor model performance and detect drift.

---

## 📄 License
MIT License. Built for institutional quantitative analysis, academic research, and algorithmic trading education.

