from fastapi import APIRouter, HTTPException
import redis
import json
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

# Redis client
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# Portfolio Data Model
class PortfolioData(BaseModel):
    incoming_inventory: Dict[str, Dict[str, float]]
    trading_inventory: Dict[str, Dict[str, float]]
    prices: Dict[str, float]

@router.get("/{portfolio_name}", response_model=PortfolioData)
def get_portfolio(portfolio_name: str):
    """
    Fetch portfolio data from Redis.
    """
    data = redis_client.get(f"{portfolio_name}_inventory")
    if data is None:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    return json.loads(data)
