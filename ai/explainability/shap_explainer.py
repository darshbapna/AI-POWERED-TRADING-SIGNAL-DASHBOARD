import logging
import numpy as np
import pandas as pd
from ai.sentiment.pipeline import compute_sentiment_score

logger = logging.getLogger(__name__)

FEATURE_TRANSLATION_RULES = {
    "rsi_14": lambda val, shap: (
        f"RSI is oversold at {val:.1f} - generating strong upward mean-reversion pull" if val < 35 else
        f"RSI is overbought at {val:.1f} - indicating elevated exhaustion / downward pressure" if val > 65 else
        f"RSI is neutral at {val:.1f} - momentum is balanced"
    ),
    "macd": lambda val, shap: (
        f"MACD line ({val:.2f}) indicates strong bullish trend continuation" if shap > 0 else
        f"MACD line ({val:.2f}) reflects bearish trend divergence"
    ),
    "macd_hist": lambda val, shap: (
        f"MACD histogram expanding positive (+{val:.2f}) - acceleration of buyer volume" if val > 0 else
        f"MACD histogram contracted negative ({val:.2f}) - momentum favors sellers"
    ),
    "sentiment_score": lambda val, shap: (
        f"Live news sentiment is bullish (+{val:.2f}) across financial headlines" if val > 0.15 else
        f"Live news sentiment is bearish ({val:.2f}) due to market macro headlines" if val < -0.15 else
        f"News sentiment is neutral ({val:.2f}) with balanced press flow"
    ),
    "cross_corr_gold_dxy": lambda val, shap: (
        f"Gold vs DXY correlation is {val:.2f} - inverse decoupling reinforces asset strength" if val < -0.5 else
        f"Gold vs DXY correlation shifted to {val:.2f} - abnormal macro co-movement detected"
    ),
    "cross_corr_nifty_spy": lambda val, shap: (
        f"Nifty vs S&P 500 correlation is {val:.2f} - capturing global risk-on beta spillover" if val > 0.4 else
        f"Domestic equity momentum is decorrelating from US indices ({val:.2f})"
    ),
    "cross_corr_crude_usdinr": lambda val, shap: (
        f"Crude oil vs USD/INR correlation ({val:.2f}) reflects balanced import bill dynamics" if shap > 0 else
        f"Crude oil price pressure is impacting Rupee stability (corr {val:.2f})"
    ),
    "relative_strength_spy": lambda val, shap: (
        f"Outperforming benchmark S&P 500 by +{val*100:.1f}% over 20-day horizon" if val > 0 else
        f"Lagging broader US equity benchmark by {val*100:.1f}% over 20-day horizon"
    ),
    "vix": lambda val, shap: (
        f"Volatility index at {val:.1f} - low market stress environment favoring long exposure" if val < 20 else
        f"Volatility index elevated at {val:.1f} - risk-off hedging prevalent"
    ),
    "yield_spread": lambda val, shap: (
        f"10Y-2Y Treasury spread ({val:.2f}%) indicates stable economic expansion regime" if val > 0 else
        f"10Y-2Y Treasury spread ({val:.2f}%) signals yield curve inversion and macro caution"
    ),
    "bb_pct_b": lambda val, shap: (
        f"Price testing lower Bollinger Band ({val:.2f}) - prime oversold rebound zone" if val < 0.15 else
        f"Price extending beyond upper Bollinger Band ({val:.2f}) - stretched upside" if val > 0.85 else
        f"Price oscillating comfortably within Bollinger envelope"
    ),
    "realized_volatility": lambda val, shap: (
        f"Realized 20-day volatility ({val*100:.1f}%) is within historical normal bands" if shap > 0 else
        f"Spike in realized volatility ({val*100:.1f}%) increases risk premium"
    )
}

def explain_prediction(model_container, feature_row: pd.Series, top_k: int = 5) -> list[dict]:
    """
    Computes SHAP feature importance values and converts them to human-readable plain English.
    """
    model = model_container.model
    scaler = model_container.scaler
    feature_cols = model_container.feature_cols
    
    # Scale feature row
    raw_vals = feature_row[feature_cols].values.reshape(1, -1)
    scaled_vals = scaler.transform(raw_vals) if scaler else raw_vals
    
    # Calculate SHAP values via TreeExplainer or fast Tree/Margin attribution
    shap_values = None
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(scaled_vals)
        if isinstance(sv, list) and len(sv) == 2:
            shap_values = sv[1][0]  # Positive class SHAP
        elif isinstance(sv, np.ndarray) and sv.ndim == 2:
            shap_values = sv[0]
        elif isinstance(sv, np.ndarray) and sv.ndim == 3:
            shap_values = sv[0, :, 1]
    except Exception as e:
        logger.warning(f"TreeExplainer fallback: {e}")

    if shap_values is None:
        # High quality feature importance-weighted surrogate
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        else:
            importances = np.ones(len(feature_cols)) / len(feature_cols)
        # Sign of scaled value determines directional push
        shap_values = scaled_vals[0] * importances * 0.5

    # Rank top K features by absolute SHAP impact
    abs_shap = np.abs(shap_values)
    top_indices = np.argsort(abs_shap)[::-1][:top_k]
    
    drivers = []
    for idx in top_indices:
        col_name = feature_cols[idx]
        val = float(feature_row[col_name])
        impact = float(shap_values[idx])
        direction = "bullish" if impact > 0 else "bearish"
        
        rule_fn = FEATURE_TRANSLATION_RULES.get(
            col_name,
            lambda v, s: f"{col_name.replace('_', ' ').title()} value of {v:.2f} is exerting {'upward' if s > 0 else 'downward'} pressure"
        )
        explanation = rule_fn(val, impact)
        
        drivers.append({
            "feature": col_name,
            "feature_label": col_name.replace("_", " ").upper(),
            "value": round(val, 3),
            "shap_impact": round(impact, 4),
            "direction": direction,
            "explanation": explanation
        })
        
    return drivers
