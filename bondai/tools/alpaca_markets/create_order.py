import os
from pydantic import BaseModel
from bondai.tools import Tool
from .response_formatter import format_order_response
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.common.exceptions import APIError

TOOL_NAME = 'create_order'
TOOL_DESCRIPTION = """This tool allows you to create an Order to buy or sell a stock. 
When using this tool, you must specify either 'buy' or 'sell' for the 'side' parameter. 
You must also specify the 'symbol' parameter which is the stock symbol of the stock you want to buy or sell. 
You must also specify the 'quantity' parameter which is the number of shares you want to buy or sell. 
The 'order_type' parameter is optional. It will default to a 'market' order by you can also specify a 'limit' order.
The 'limit_price' parameter is only required if you specify a 'limit' order.
The 'time_in_force' parameter is optional. It will default to 'day' but you can also specify 'gtc', 'opg', 'cls', 'ioc', or 'fok'."""

ALPACA_MARKETS_API_KEY = os.environ.get('ALPACA_MARKETS_API_KEY')
ALPACA_MARKETS_SECRET_KEY = os.environ.get('ALPACA_MARKETS_SECRET_KEY')

class Parameters(BaseModel):
    side: str
    symbol: str
    quantity: str
    order_type: str
    time_in_force: str
    limit_price: str
    thought: str

class CreateOrderTool(Tool):
    def __init__(self, alpaca_api_key=ALPACA_MARKETS_API_KEY, alpaca_secret_key=ALPACA_MARKETS_SECRET_KEY):
        super(CreateOrderTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self.trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    
    def run(self, arguments):
        side = arguments.get('side')
        symbol = arguments.get('symbol')
        quantity = arguments.get('quantity')
        order_type = arguments.get('order_type', 'market')
        time_in_force = arguments.get('time_in_force', 'day')
        limit_price = arguments.get('limit_price', None)

        if not side in ['buy', 'sell']:
            return 'Invalid side. Must be either "buy" or "sell".'
        if not symbol:
            return 'Invalid symbol.'
        if not quantity:
            return 'Invalid quantity.'
        if not order_type in ['market', 'limit']:
            return 'Invalid order type. Must be either "market" or "limit".'
        if not time_in_force in ['day', 'gtc', 'opg', 'cls', 'ioc', 'fok']:
            return 'Invalid time in force. Must be either "day", "gtc", "opg", "cls", "ioc", or "fok".'
        if order_type == 'limit' and not limit_price:
            return 'Invalid limit price.'

        if order_type == 'market':
            order = MarketOrderRequest(symbol=symbol, qty=quantity, side=side, time_in_force=time_in_force)
        else:
            order = LimitOrderRequest(symbol=symbol, limit_price=limit_price, qty=quantity, side=side, time_in_force=time_in_force)

        try:
            response = self.trading_client.submit_order(order_data=order)
            return format_order_response(response)
        except APIError as e:
            return e.message

