import redis
import pandas as pd
from datetime import datetime
import json

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def store_pnl(portfolio_name, pnl_df):
    """
    Store PnL data in Redis with a timestamp.

    Args:
        portfolio_name (str): Name of the portfolio.
        pnl_df (pandas.DataFrame): PnL data to store.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    key = f"pnl:{portfolio_name}:{timestamp}"
    redis_client.set(key, pnl_df.to_json(orient="records"))


def get_pnl_history(portfolio_name):
    """
    Retrieve historical PnL data from Redis for a portfolio.

    Args:
        portfolio_name (str): Name of the portfolio.

    Returns:
        list: Historical PnL data.
    """
    keys = redis_client.keys(f"pnl:{portfolio_name}:*")
    pnl_history = []
    for key in keys:
        data = redis_client.get(key)
        pnl_history.extend(json.loads(data))
    return pnl_history
