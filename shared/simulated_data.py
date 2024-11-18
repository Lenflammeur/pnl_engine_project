import random
from datetime import datetime

def generate_random_inventory():
    """
    Generate random incoming inventory for a portfolio.
    Returns:
        dict: Simulated inventory data.
    """
    return {
        "AAPL": {"quantity": random.randint(1, 20), "cost_price": round(random.uniform(100, 200), 2)},
        "MSFT": {"quantity": random.randint(1, 10), "cost_price": round(random.uniform(200, 400), 2)},
        "GOOG": {"quantity": random.randint(1, 5), "cost_price": round(random.uniform(2000, 3000), 2)},
    }

def generate_random_prices():
    """
    Generate random current prices for assets.
    Returns:
        dict: Simulated price data.
    """
    return {
        "AAPL": round(random.uniform(100, 200), 2),
        "MSFT": round(random.uniform(200, 400), 2),
        "GOOG": round(random.uniform(2000, 3000), 2),
    }

def generate_random_trade():
    """
    Generate a random trade.
    Returns:
        dict: Simulated trade details.
    """
    return {
        "asset": random.choice(["AAPL", "MSFT", "GOOG"]),
        "quantity": random.randint(-10, 10),  # Negative for sell, positive for buy
        "price": round(random.uniform(100, 3000), 2),
        "timestamp": datetime.now().isoformat()
    }

def generate_portfolio_data():
    """
    Generate a simulated portfolio with inventory and prices.
    Returns:
        dict: Simulated portfolio data.
    """
    inventory = generate_random_inventory()
    prices = generate_random_prices()

    return {
        "incoming_inventory": inventory,
        "trading_inventory": {},  # Empty at the start of the day
        "prices": prices
    }

if __name__ == "__main__":
    # Example usage
    print("Simulated Portfolio Data:")
    print(generate_portfolio_data())

    print("\nSimulated Trade:")
    print(generate_random_trade())
