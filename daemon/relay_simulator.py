import redis
import json
import time
import random

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

def generate_trade():
    """Simulate a random trade."""
    return {
        "asset": random.choice(["AAPL", "MSFT", "GOOG"]),
        "quantity": random.randint(-10, 10),  # Negative for sell, positive for buy
        "price": round(random.uniform(100, 3000), 2),
        "timestamp": time.time()
    }

def publish_trade():
    """Push trades to a Redis list."""
    while True:
        trade = generate_trade()
        redis_client.rpush("trades_queue", json.dumps(trade))  # Add trade to the queue
        print(f"Queued Trade: {trade}")
        time.sleep(1)  # Simulate trade frequency

if __name__ == "__main__":
    publish_trade()
