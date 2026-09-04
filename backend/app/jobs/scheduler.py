import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.db.models import Prediction, PredictionOutcome, Price
from ai.data_layer.provider import ASSET_REGISTRY, get_ohlcv
from ai.data_layer.calendar import is_market_open
from ai.inference import predict

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def job_hourly_predictions():
    """Generates and logs fresh AI signals for all tracked assets."""
    logger.info("Executing scheduled hourly prediction job...")
    db: Session = SessionLocal()
    try:
        for ticker in ASSET_REGISTRY.keys():
            try:
                res = predict(ticker)
                pred_obj = Prediction(
                    ticker=ticker,
                    timestamp=datetime.utcnow(),
                    signal=res["signal_code"],
                    confidence=res["confidence"],
                    price_at_prediction=res["current_price"],
                    horizon_days=res["horizon_days"],
                    model_version=res["model_version"],
                    shap_summary=str(res["shap_drivers"])
                )
                db.add(pred_obj)
            except Exception as e:
                logger.warning(f"Prediction job failed for {ticker}: {e}")
        db.commit()
        logger.info("Hourly predictions successfully recorded.")
    finally:
        db.close()

def job_daily_t5_verification():
    """
    Evaluates predictions made ~5 days ago against actual current market prices.
    Computes outcome correctness and logs to prediction_outcomes table.
    """
    logger.info("Executing daily T+5 outcome verification job...")
    db: Session = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=5)
        # Find predictions older than 5 days without an outcome record
        pending_preds = db.query(Prediction).outerjoin(PredictionOutcome).filter(
            Prediction.timestamp <= cutoff_date,
            PredictionOutcome.id == None
        ).limit(50).all()
        
        for pred in pending_preds:
            try:
                df = get_ohlcv(pred.ticker, interval="1d")
                if df is not None and len(df) > 0:
                    current_price = float(df.iloc[-1]["close"])
                    p_orig = float(pred.price_at_prediction)
                    chg_pct = round(((current_price - p_orig) / p_orig) * 100, 2)
                    
                    actual_direction = "UP" if chg_pct > 0 else ("DOWN" if chg_pct < 0 else "FLAT")
                    was_correct = (
                        (pred.signal == "BUY" and chg_pct > 0) or
                        (pred.signal == "SELL" and chg_pct < 0) or
                        (pred.signal == "HOLD" and abs(chg_pct) < 1.0)
                    )
                    
                    outcome = PredictionOutcome(
                        prediction_id=pred.id,
                        outcome_timestamp=datetime.utcnow(),
                        actual_price=current_price,
                        price_change_pct=chg_pct,
                        actual_direction=actual_direction,
                        was_correct=was_correct
                    )
                    db.add(outcome)
            except Exception as e:
                logger.warning(f"T+5 verification failed for pred #{pred.id}: {e}")
        db.commit()
        logger.info(f"T+5 verification completed for {len(pending_preds)} records.")
    finally:
        db.close()

def start_scheduler():
    """Initializes and starts background scheduled jobs."""
    if not scheduler.running:
        scheduler.add_job(
            job_hourly_predictions,
            trigger=IntervalTrigger(hours=1),
            id="hourly_predictions",
            replace_existing=True
        )
        scheduler.add_job(
            job_daily_t5_verification,
            trigger=IntervalTrigger(hours=4),
            id="daily_t5_verification",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler initialized and running.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
