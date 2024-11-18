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

    # Update inventory
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
