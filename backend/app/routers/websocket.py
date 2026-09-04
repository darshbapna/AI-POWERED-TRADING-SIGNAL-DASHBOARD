import asyncio
import json
import logging
from datetime import datetime
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ai.data_layer.provider import ASSET_REGISTRY, get_ohlcv

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket Live Feed"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ticker: str, websocket: WebSocket):
        await websocket.accept()
        if ticker not in self.active_connections:
            self.active_connections[ticker] = []
        self.active_connections[ticker].append(websocket)
        logger.info(f"WebSocket connected for {ticker}. Active clients: {len(self.active_connections[ticker])}")

    def disconnect(self, ticker: str, websocket: WebSocket):
        if ticker in self.active_connections:
            if websocket in self.active_connections[ticker]:
                self.active_connections[ticker].remove(websocket)
            if not self.active_connections[ticker]:
                del self.active_connections[ticker]
        logger.info(f"WebSocket disconnected for {ticker}")

    async def broadcast(self, ticker: str, message: dict):
        if ticker in self.active_connections:
            data_text = json.dumps(message)
            dead_sockets = []
            for ws in self.active_connections[ticker]:
                try:
                    await ws.send_text(data_text)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.disconnect(ticker, ws)

manager = ConnectionManager()

@router.websocket("/ws/live/{ticker}")
async def websocket_live_feed(websocket: WebSocket, ticker: str):
    """
    Live streaming WebSocket endpoint for high-frequency price updates and candle updates.
    """
    await manager.connect(ticker, websocket)
    meta = ASSET_REGISTRY.get(ticker, {"base_price": 100.0, "name": ticker})
    
    # Get last known close price
    try:
        df = get_ohlcv(ticker, interval="1d")
        last_close = float(df.iloc[-1]["close"]) if len(df) > 0 else meta.get("base_price", 100.0)
    except Exception:
        last_close = meta.get("base_price", 100.0)

    current_price = last_close
    bar_open = current_price
    bar_high = current_price
    bar_low = current_price
    bar_volume = 0.0
    
    volatility_step = (0.0006 if "BTC" not in ticker else 0.002) * current_price

    try:
        while True:
            # Generate microstructure tick
            tick_delta = np.random.normal(0, volatility_step)
            current_price = max(0.01, round(current_price + tick_delta, 2))
            
            bar_high = max(bar_high, current_price)
            bar_low = min(bar_low, current_price)
            tick_vol = int(np.random.lognormal(5, 1))
            bar_volume += tick_vol
            
            chg = round(current_price - last_close, 2)
            chg_pct = round((chg / last_close) * 100, 2)
            
            from ai.data_layer.calendar import is_market_open
            m_info = is_market_open(ticker)
            
            payload = {
                "type": "TICK",
                "ticker": ticker,
                "name": meta.get("name", ticker),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "exchange": m_info.get("exchange", "Exchange"),
                "timezone_id": m_info.get("timezone_id", "UTC"),
                "timezone_code": m_info.get("timezone_code", "UTC"),
                "exchange_local_time": m_info.get("local_time", ""),
                "is_market_open": m_info.get("is_open", True),
                "session_status": m_info.get("status_message", ""),
                "price": current_price,
                "change": chg,
                "change_pct": chg_pct,
                "bar": {
                    "open": bar_open,
                    "high": bar_high,
                    "low": bar_low,
                    "close": current_price,
                    "volume": bar_volume
                }
            }
            
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.8)  # 1.8 second tick interval
            
    except WebSocketDisconnect:
        manager.disconnect(ticker, websocket)
    except Exception as e:
        logger.warning(f"WebSocket error on {ticker}: {e}")
        manager.disconnect(ticker, websocket)
