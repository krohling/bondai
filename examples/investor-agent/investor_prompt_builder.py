import os
from datetime import datetime
from bondai.prompt import PromptBuilder
from bondai.prompt.steps_formatter import format_previous_steps
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from bondai.tools.alpaca_markets import format_positions_response, format_account_response, format_orders_response

class InvestorPromptBuilder(PromptBuilder):

    def __init__(self, llm, alpaca_api_key, alpaca_secret_key):
        self.llm = llm
        self.trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_template_path = os.path.join(current_dir, 'investor_prompt_template.md')
        with open(prompt_template_path, 'r') as file:
            self.prompt_template = file.read()

    def build_prompt(self, task, tools, previous_steps=[], max_tokens=None):
        prompt = self.prompt_template.replace('{DATETIME}', str(datetime.now()))
        prompt = prompt.replace('{TASK}', task)

        if len(previous_steps) > 0:
            str_work = 'This is a list of previous steps that you already completed on this TASK.'
            
            if max_tokens:
                remaining_tokens = max_tokens - self.llm.count_tokens(prompt)
                str_work += format_previous_steps(self.llm, previous_steps, remaining_tokens)
            else:
                str_work += format_previous_steps(self.llm, previous_steps)
        else:
            str_work = '**No previous steps have been completed**'

        prompt = prompt.replace('{WORK}', str_work)

        get_orders_data = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            limit=25
        )
        response = self.trading_client.get_orders(filter=get_orders_data)
        prompt = prompt.replace('{ORDERS}', format_orders_response(response))

        response = self.trading_client.get_account()
        prompt = prompt.replace('{ACCOUNT}', format_account_response(response))

        response = self.trading_client.get_all_positions()
        prompt = prompt.replace('{POSITIONS}', format_positions_response(response))

        return prompt
