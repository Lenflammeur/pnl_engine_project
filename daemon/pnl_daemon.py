import redis
import json
import time

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

PORTFOLIO_NAME = "Portfolio1"


def process_trade_chunk(trades):
    """
    Process a chunk of trades and update PnL.
    """
    raw_data = redis_client.get(f"{PORTFOLIO_NAME}_inventory")
    portfolio_data = json.loads(raw_data) if raw_data else initialize_portfolio()

    if not portfolio_data:
        portfolio_data = initialize_portfolio()

    trading_inventory = portfolio_data["trading_inventory"]
    prices = portfolio_data["prices"]

    for trade in trades:
        trading_inventory = process_trade(trading_inventory, trade, prices)

    # Compute PnL
    portfolio_data["trading_inventory"] = trading_inventory
    pnl_data = compute_pnl(portfolio_data)

    # Store updated inventory and PnL in Redis
    redis_client.set(f"{PORTFOLIO_NAME}_inventory", json.dumps(portfolio_data))
    redis_client.set(f"{PORTFOLIO_NAME}_pnl", json.dumps(pnl_data))

    print(f"Processed {len(trades)} trades. Updated PnL: {pnl_data}")


def initialize_portfolio():
    """
    Initialize the portfolio with default data.
    """
    portfolio_data = {
        "incoming_inventory": {
            "AAPL": {"quantity": 10, "cost_price": 150},
            "MSFT": {"quantity": 5, "cost_price": 300},
        },
        "trading_inventory": {},
        "prices": {"AAPL": 155, "MSFT": 310},
    }
    redis_client.set(f"{PORTFOLIO_NAME}_inventory", json.dumps(portfolio_data))
    return portfolio_data


def process_trade(trading_inventory, trade, prices):
    """
    Process a single trade and update the inventory.
    """
    asset = trade["asset"]
    quantity = trade["quantity"]
    price = trade["price"]

    if asset not in trading_inventory:
        trading_inventory[asset] = {"quantity": 0, "average_cost": 0.0, "realized_pnl": 0.0, "unrealized_pnl": 0.0}

    asset_data = trading_inventory[asset]
    current_quantity = asset_data["quantity"]
    average_cost = asset_data["average_cost"]

    # Update inventory logic
    if current_quantity == 0:
        asset_data["quantity"] = quantity
        asset_data["average_cost"] = price
    elif (current_quantity > 0 and quantity > 0) or (current_quantity < 0 and quantity < 0):
        total_quantity = current_quantity + quantity
        asset_data["average_cost"] = (
            (current_quantity * average_cost + quantity * price) / total_quantity
        )
        asset_data["quantity"] = total_quantity
    else:
        realized_quantity = min(abs(current_quantity), abs(quantity))
        realized_pnl = (price - average_cost) * realized_quantity
        if current_quantity < 0:
            realized_pnl = (average_cost - price) * realized_quantity

        asset_data["realized_pnl"] += realized_pnl
        remaining_quantity = current_quantity + quantity
        if remaining_quantity == 0:
            asset_data["quantity"] = 0
            asset_data["average_cost"] = 0.0
        else:
            asset_data["quantity"] = remaining_quantity
            asset_data["average_cost"] = price

    # Update unrealized PnL
    last_trade_price = prices.get(asset, price)
    unrealized_pnl = 0
    if asset_data["quantity"] > 0:
        unrealized_pnl = (last_trade_price - asset_data["average_cost"]) * asset_data["quantity"]
    elif asset_data["quantity"] < 0:
        unrealized_pnl = (asset_data["average_cost"] - last_trade_price) * abs(asset_data["quantity"])

    asset_data["unrealized_pnl"] = unrealized_pnl

    return trading_inventory


def compute_pnl(portfolio_data):
    """
    Compute the PnL for the portfolio.
    """
    incoming_inventory = portfolio_data.get("incoming_inventory", {})
    trading_inventory = portfolio_data.get("trading_inventory", {})
    prices = portfolio_data.get("prices", {})

    incoming_pnl = 0
    trading_unrealized = 0
    trading_realized = 0

    # Compute Incoming PnL
    for asset, data in incoming_inventory.items():
        current_price = prices.get(asset, 0)
        incoming_pnl += (current_price - data["cost_price"]) * data["quantity"]

    # Compute Trading PnL
    for asset, data in trading_inventory.items():
        current_price = prices.get(asset, 0)
        quantity = data["quantity"]
        cost_price = data["average_cost"]

        if quantity > 0:
            unrealized = (current_price - cost_price) * quantity
            trading_unrealized += (current_price - cost_price) * quantity
            print(f"[DEBUG] Unrealized PnL for {asset}: (Current Price: {current_price} - Average Cost: {cost_price}) * Quantity: {quantity} = {unrealized}")
        elif quantity < 0:
            trading_realized += data["realized_pnl"]

    trading_pnl = trading_unrealized + trading_realized
    total_pnl = incoming_pnl + trading_pnl

    return {
        "incoming_pnl": incoming_pnl,
        "trading_pnl": trading_pnl,
        "trading_unrealized": trading_unrealized,
        "trading_realized": trading_realized,
        "total_pnl": total_pnl,
    }


def daemon_run():
    """
    Main loop for the PnL daemon to fetch and process trade chunks.
    """
    print("PnL Daemon is running...")
    while True:
        trades = fetch_trade_chunk("trades_queue", chunk_size=10)
        if trades:
            process_trade_chunk(trades)
        else:
            print("No trades in queue. Waiting...")
            time.sleep(1)


def fetch_trade_chunk(queue_name, chunk_size):
    """
    Fetch a chunk of trades from the Redis queue.
    """
    trades = redis_client.lrange(queue_name, 0, chunk_size - 1)  # Fetch a chunk
    redis_client.ltrim(queue_name, chunk_size, -1)  # Remove processed trades
    return [json.loads(trade) for trade in trades]


if __name__ == "__main__":
    daemon_run()
