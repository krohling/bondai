import os
from bondai.tools import Tool
from .response_formatter import format_account_response
from alpaca.trading.client import TradingClient

TOOL_NAME = 'get_account_info'
TOOL_DESCRIPTION = "This tool will provide information about your investment account including your cash balance."

ALPACA_MARKETS_API_KEY = os.environ.get('ALPACA_MARKETS_API_KEY')
ALPACA_MARKETS_SECRET_KEY = os.environ.get('ALPACA_MARKETS_SECRET_KEY')

class GetAccountTool(Tool):
    def __init__(self, alpaca_api_key=ALPACA_MARKETS_API_KEY, alpaca_secret_key=ALPACA_MARKETS_SECRET_KEY):
        super(GetAccountTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION)
        self.trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    
    def run(self, arguments):
        response = self.trading_client.get_account()
        return format_account_response(response)

