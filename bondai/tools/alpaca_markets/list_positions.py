import os
from bondai.tools.tool import Tool
from .response_formatter import format_positions_response
from alpaca.trading.client import TradingClient

TOOL_NAME = 'list_positions'
TOOL_DESCRIPTION = "This tool will list all of your currently open positions."

ALPACA_MARKETS_API_KEY = os.environ.get('ALPACA_MARKETS_API_KEY')
ALPACA_MARKETS_SECRET_KEY = os.environ.get('ALPACA_MARKETS_SECRET_KEY')

class ListPositionsTool(Tool):
    def __init__(self, alpaca_api_key=ALPACA_MARKETS_API_KEY, alpaca_secret_key=ALPACA_MARKETS_SECRET_KEY):
        super(ListPositionsTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION)
        self.trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    
    def run(self, arguments):
        response = self.trading_client.get_all_positions()

        if len(response) > 0:
            return format_positions_response(response)
        return "There are no open positions."

