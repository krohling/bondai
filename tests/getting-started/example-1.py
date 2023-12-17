# from bondai.agents import Agent
# from bondai.models.openai import DefaultOpenAIConnectionParams
# from bondai.tools.search import DuckDuckGoSearchTool
# from bondai.tools.website import WebsiteQueryTool
# from bondai.tools.file import FileWriteTool

# DefaultOpenAIConnectionParams.configure_openai_connection(api_key="<OPENAI-API-KEY>")


# task = """I want you to research the usage of Metformin as a drug to treat aging and aging related illness.
# You should only use reputable information sources, ideally peer reviewed scientific studies.
# I want you to summarize your findings in a document named metformin.md and includes links to reference and resources you used to find the information.
# Additionally, the last section of your document you should provide a recommendation for a 43 year old male, in good health and who regularly exercises as to whether he would benefit from taking Metformin.
# You should explain your recommendation and justify it with sources.
# Finally, you should highlight potential risks and tradeoffs from taking the medication."""

# Agent(tools=[
#   DuckDuckGoSearchTool(),
#   WebsiteQueryTool(),
#   FileWriteTool()
# ]).run(task)

from bondai.agents import Agent
from bondai.models.openai import (
    OpenAILLM,
    OpenAIConnectionParams,
    OpenAIConnectionType,
    OpenAIModelNames,
)


connection_params = OpenAIConnectionParams(
    connection_type=OpenAIConnectionType.AZURE,
    api_key="",
    api_version="",
    azure_endpoint="",
    azure_deployment="",
)

llm = OpenAILLM(model=OpenAIModelNames.GPT4_32K, connection_params=connection_params)

agent = Agent(llm=llm)
