from fastapi import FastAPI, HTTPException
import redis
import json

app = FastAPI()

# Redis connection
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# Portfolio name
PORTFOLIO_NAME = "Portfolio1"


@app.get("/pnl/{portfolio_name}")
def get_current_pnl(portfolio_name: str):
    """
    Fetch the latest PnL for a given portfolio.
    """
    pnl_key = f"{portfolio_name}_pnl"
    pnl_data = redis_client.get(pnl_key)
    if not pnl_data:
        raise HTTPException(status_code=404, detail="PnL data not found")
    return json.loads(pnl_data)
