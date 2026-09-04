import unittest
import numpy as np
import pandas as pd
from ai.features.indicators import compute_rsi, compute_macd, compute_bollinger_bands, compute_sma, compute_ema
from ai.features.cross_asset import build_features
from ai.data_layer.provider import generate_realistic_ohlcv
from ai.sentiment.pipeline import analyze_headline_finbert, compute_sentiment_score
from ai.backtesting.engine import run_backtest
from ai.inference import predict

class TestAIEngine(unittest.TestCase):
    
    def setUp(self):
        self.df = generate_realistic_ohlcv("^NSEI", start_date="2023-01-01")

    def test_indicator_math(self):
        """Validates that technical indicators compute correct bounds and shapes."""
        rsi = compute_rsi(self.df["close"], 14).dropna()
        self.assertTrue(len(rsi) > 0)
        self.assertTrue((rsi >= 0).all() and (rsi <= 100).all())

        macd_line, sig_line, hist = compute_macd(self.df["close"])
        self.assertEqual(len(macd_line), len(self.df))

        upper, mid, lower = compute_bollinger_bands(self.df["close"], 20, 2.0)
        valid_idx = ~upper.isna()
        self.assertTrue((upper[valid_idx] >= mid[valid_idx]).all())
        self.assertTrue((mid[valid_idx] >= lower[valid_idx]).all())

    def test_sentiment_pipeline(self):
        """Validates FinBERT financial lexicon and score bounds."""
        score, label = analyze_headline_finbert("RBI rate cut triggers rally in banking shares")
        self.assertGreater(score, 0.2)
        self.assertEqual(label, "positive")

        score_neg, label_neg = analyze_headline_finbert("Crude oil surge triggers rupee plunge and inflation fears")
        self.assertLess(score_neg, -0.2)
        self.assertEqual(label_neg, "negative")

        sent_res = compute_sentiment_score("^NSEI")
        self.assertIn("score", sent_res)
        self.assertIn("top_drivers", sent_res)

    def test_backtest_engine(self):
        """Validates backtest simulation metrics and transaction cost deductions."""
        res = run_backtest("^NSEI")
        self.assertIn("metrics", res)
        self.assertIn("equity_curves", res)
        metrics = res["metrics"]
        self.assertIn("strategy_total_return_pct", metrics)
        self.assertIn("annualized_sharpe", metrics)
        self.assertIn("max_drawdown_pct", metrics)
        self.assertIn("win_rate_pct", metrics)
        self.assertTrue(len(res["equity_curves"]) > 10)

    def test_inference_predict(self):
        """Validates the unified predict() interface."""
        pred = predict("^NSEI")
        self.assertEqual(pred["ticker"], "^NSEI")
        self.assertIn(pred["signal_code"], ["BUY", "SELL", "HOLD"])
        self.assertTrue(0.0 <= pred["confidence"] <= 1.0)
        self.assertTrue(len(pred["shap_drivers"]) > 0)

if __name__ == "__main__":
    unittest.main()
