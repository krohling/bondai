from bondai.agent import Agent
from bondai.models.openai import OpenAILLM, MODEL_GPT4_0613
from bondai.tools.alpaca_markets import CreateOrderTool
from bondai.tools.search import GoogleSearchTool
from bondai.tools.website import WebsiteQueryTool
from investor_prompt_builder import InvestorPromptBuilder

TASK_BUDGET = 10.00
ALPACA_API_KEY = 'XXXXXXXXXX'
ALPACA_SECRET_KEY = 'XXXXXXXXXX'
GOOGLE_API_KEY = 'XXXXXXXXXX'
GOOGLE_CSE_ID = 'XXXXXXXXXX'

tools = [
    CreateOrderTool(ALPACA_API_KEY, ALPACA_SECRET_KEY),
    GoogleSearchTool(GOOGLE_API_KEY, GOOGLE_CSE_ID),
    WebsiteQueryTool()
]

llm = OpenAILLM(MODEL_GPT4_0613)
agent = Agent(prompt_builder=InvestorPromptBuilder(llm, ALPACA_API_KEY, ALPACA_SECRET_KEY), tools=tools, llm=llm, budget=TASK_BUDGET)
result = agent.run()
print(result.output)