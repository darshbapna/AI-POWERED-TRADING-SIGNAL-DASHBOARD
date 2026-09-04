from fastapi import APIRouter, HTTPException
from ai.inference import predict
from backend.app.schemas.schemas import PredictResponse

router = APIRouter(prefix="/predict", tags=["Predict"])

@router.get("/{ticker}", response_model=PredictResponse)
def get_prediction(ticker: str):
    """
    Returns AI model forecast, probability, confidence, SHAP explainability drivers, and news catalysts.
    """
    try:
        result = predict(ticker)
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error for {ticker}: {str(e)}")
