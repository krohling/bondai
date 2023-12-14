import os
from bondai.tools import Tool
from .response_formatter import format_account_response
from .env_vars import ALPACA_MARKETS_API_KEY_ENV_VAR, ALPACA_MARKETS_SECRET_KEY_ENV_VAR
from alpaca.trading.client import TradingClient

TOOL_NAME = "get_investment_account_info"
TOOL_DESCRIPTION = "This tool will provide information about your investment account including your cash balance."


class GetAccountTool(Tool):
    def __init__(
        self,
        alpaca_api_key=os.environ.get(ALPACA_MARKETS_API_KEY_ENV_VAR),
        alpaca_secret_key=os.environ.get(ALPACA_MARKETS_SECRET_KEY_ENV_VAR),
    ):
        super(GetAccountTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION)
        self.trading_client = TradingClient(
            alpaca_api_key, alpaca_secret_key, paper=True
        )

    def run(self, arguments):
        response = self.trading_client.get_account()
        return format_account_response(response)
