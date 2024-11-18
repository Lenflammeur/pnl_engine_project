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
            trading_unrealized += (current_price - cost_price) * quantity
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
