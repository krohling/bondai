from bondai import Agent
from bondai.tools.search import GoogleSearchTool
from bondai.tools.website import WebsiteQueryTool
from bondai.tools.file import FileWriteTool

GOOGLE_API_KEY = 'XXXXXXXXXX'
GOOGLE_CSE_ID = 'XXXXXXXXXX'

task = """I want you to research the usage of Metformin as a drug to treat aging and aging related illness. 
You should only use reputable information sources, ideally peer reviewed scientific studies. 
I want you to summarize your findings in a document named metformin.md and includes links to reference and resources you used to find the information. 
Additionally, the last section of your document you should provide a recommendation for a 43 year old male, in good health and who regularly exercises as to whether he would benefit from taking Metformin. 
You should explain your recommendation and justify it with sources. 
Finally, you should highlight potential risks and tradeoffs from taking the medication."""

result = Agent(tools=[
  GoogleSearchTool(GOOGLE_API_KEY, GOOGLE_CSE_ID),
  WebsiteQueryTool(),
  FileWriteTool()
]).run(task)
print(result.output)