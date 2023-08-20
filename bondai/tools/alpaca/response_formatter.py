
def format_order_response(response):
    return f"""Order ID: {response.id}
Status: {response.status}
Filled At: {response.filled_at}
Symbol: {response.symbol}
Asset Class: {response.asset_class}
Notional: {response.notional}
Quantity: {response.qty}
Filled Quantity: {response.filled_qty}
Filled Average Price: {response.filled_avg_price}
Filled Price: {response.filled_avg_price}
Order Class: {response.order_class}
Order Type: {response.order_type}
Side: {response.side}
Time In Force: {response.time_in_force}
Limit Price: {response.limit_price}
Stop Price: {response.stop_price}"""

def format_account_response(response):
    return f"""Cash: {response.cash}
Currency: {response.currency}
Buying Power: {response.buying_power}
Regt Buying Power: {response.regt_buying_power}
Daytrading Buying Power: {response.daytrading_buying_power}  
Non Marginable Buying Power: {response.non_marginable_buying_power}
Accrued Fees: {response.accrued_fees}
Portfolio Value: {response.portfolio_value}
Shorting Enabled: {response.shorting_enabled}
Crypto Status: {response.crypto_status}
Long Market Value: {response.long_market_value}
Short Market Value: {response.short_market_value}
Initial Margin: {response.initial_margin}
Maintenance Margin: {response.maintenance_margin}
Last Maintenance Margin: {response.last_maintenance_margin}"""

def format_positions_response(response):
    result = ''
    for position in response:
        result += format_position(position) + '\n\n'
    return result

def format_position(position):
    return f"""Symbol: {position.symbol}
Quantity: {position.qty}
Entry Share Price: {position.avg_entry_price}
Current Share Price: {position.current_price}
Unrealized Profit/Loss: {position.unrealized_pl}
Market Value: {position.market_value}
Cost Basis: {position.cost_basis}"""

def format_orders_response(response):
    result = ''
    for order in response:
        result += format_order(order) + '\n\n'
    return result

def format_order(order):
    return f"""Order ID: {order.id}
Type: {order.type}
Symbol: {order.symbol}
Status: {order.status}
Side: {order.side}
Limit Price: {order.limit_price}
Quantity: {order.qty}"""
