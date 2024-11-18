from fastapi import APIRouter, HTTPException
import redis
import json
from pydantic import BaseModel

router = APIRouter()

# Redis client
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# PnL Data Model
class PnLData(BaseModel):
    incoming_pnl: float
    trading_pnl: float
    trading_unrealized: float
    trading_realized: float
    total_pnl: float

@router.get("/{portfolio_name}", response_model=PnLData)
def get_pnl(portfolio_name: str):
    """
    Fetch PnL data from Redis.
    """
    data = redis_client.get(f"{portfolio_name}_pnl")
    if data is None:
        raise HTTPException(status_code=404, detail="PnL data not found.")
    return json.loads(data)

@router.get("/pnl/{portfolio_name}/history")
def get_pnl_history(portfolio_name: str):
    """
    Fetch full day's historical PnL for the given portfolio.
    """
    try:
        history_key = f"{portfolio_name}_pnl_history"
        history = redis_client.lrange(history_key, 0, -1)  # Fetch all timestamps
        return [float(value) for value in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching PnL history: {e}")
