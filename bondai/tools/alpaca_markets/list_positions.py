import os
from bondai.tools.tool import Tool
from .response_formatter import format_positions_response
from .env_vars import ALPACA_MARKETS_API_KEY_ENV_VAR, ALPACA_MARKETS_SECRET_KEY_ENV_VAR
from alpaca.trading.client import TradingClient

TOOL_NAME = "list_investment_positions"
TOOL_DESCRIPTION = (
    "This tool will list all of your currently open investment positions."
)


class ListPositionsTool(Tool):
    def __init__(
        self,
        alpaca_api_key=os.environ.get(ALPACA_MARKETS_API_KEY_ENV_VAR),
        alpaca_secret_key=os.environ.get(ALPACA_MARKETS_SECRET_KEY_ENV_VAR),
    ):
        super(ListPositionsTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION)
        self.trading_client = TradingClient(
            alpaca_api_key, alpaca_secret_key, paper=True
        )

    def run(self, arguments):
        response = self.trading_client.get_all_positions()

        if len(response) > 0:
            return format_positions_response(response)
        return "There are no open positions."
