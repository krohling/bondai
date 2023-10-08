---
sidebar_position: 4
---

# Online Research Agent

**[View Agent Output](./metformin-research)**

In this example we demonstrate BondAI's ability to do online research. We have asked BondAI to research the use of Metformin as a drug to treat aging and aging related illnesses. **[Click here](metformin-research)** to see the output BondAI generated for this example.

First we will configure the environment variables for OpenAI and Google Search.

```bash
export OPENAI_API_KEY=sk-XXXXXXXXXX
export GOOGLE_API_KEY=XXXXXXXXXX
export GOOGLE_CSE_ID=XXXXXXXXXX
```

Next we will create an Agent with 3 tools:
- **GoogleSearchTool** Allows the Agent to search the internet.
- **WebsiteQueryTool** Allows the Agent to query information about websites. Note that this tool has integrated semantic search. If the content of the website exceeds the LLM's context window size BondAI will automatically convert the content to Embeddings and semantically filter it to fit inside the context window.
- **FileWriteTool** Allows the Agent to save the results to a file.

```python
from bondai import Agent
from bondai.tools.search import GoogleSearchTool
from bondai.tools.website import WebsiteQueryTool
from bondai.tools.file import FileWriteTool

task = """I want you to research the usage of Metformin as a drug to treat aging and aging related illness. 
You should only use reputable information sources, ideally peer reviewed scientific studies. 
I want you to summarize your findings in a document named metformin.md and includes links to reference and resources you used to find the information. 
Additionally, the last section of your document you should provide a recommendation for a 43 year old male, in good health and who regularly exercises as to whether he would benefit from taking Metformin. 
You should explain your recommendation and justify it with sources. 
Finally, you should highlight potential risks and tradeoffs from taking the medication."""

Agent(tools=[
  GoogleSearchTool(),
  WebsiteQueryTool(),
  FileWriteTool()
]).run(task)
```

## Agent Logs

```
Using the google_search tool
Thought: I am searching for reputable sources that provide information on the use of Metformin in treating aging and aging-related illnesses.
Arguments
query: Metformin use in treating aging and aging-related illnesses
count: 10
page: 1
Output: [Metformin in aging and aging-related diseases: clinical applications ...](https://www.ncbi.nlm.n...


Using the website_query tool
Thought: I am trying to understand the purpose of the study to see if it is relevant to the user's request.
Arguments
url: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8965502/
question: What is the purpose of the study?
Output: The purpose of the study is to provide updated information and knowledge on the clinical applicat...


Using the website_query tool
Thought: I am trying to understand the clinical applications of Metformin in the prevention and treatment of aging and aging-related diseases.
Arguments
url: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8965502/
question: What are the clinical applications of Metformin in the prevention and treatment of aging and agin...
Output: The clinical applications of Metformin in the prevention and treatment of aging and aging-related...


Using the google_search tool
Thought: I am searching for reputable sources that provide information on the potential risks and side effects of Metformin.
Arguments
query: Metformin side effects and risks
count: 10
page: 1
Output: [Side effects of metformin - NHS](https://www.nhs.uk/medicines/metformin/side-effects-of-metformi...


Using the website_query tool
Thought: I am trying to understand the side effects and risks of Metformin.
Arguments
url: https://www.nhs.uk/medicines/metformin/side-effects-of-metformin/
question: What are the side effects and risks of Metformin?
Output: The common side effects of Metformin include feeling sick (nausea), being sick (vomiting), diarrh...


Using the website_query tool
Thought: Researching the effectiveness of Metformin in treating aging-related diseases
Arguments
url: https://www.ncbi.nlm.nih.gov/pubmed/29766366
question: What is the effectiveness of Metformin in treating aging-related diseases?
Output: The provided information does not mention anything about the effectiveness of Metformin in treati...


Using the website_query tool
Thought: I am trying to find more specific information about the effectiveness of Metformin in treating aging-related diseases.
Arguments
url: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6779524/
question: What is the effectiveness of Metformin in treating aging-related diseases?
Output: The effectiveness of Metformin in treating aging-related diseases is still being studied. While o...


Using the website_query tool
Thought: I am trying to find specific information about the potential benefits of Metformin for a 43-year-old male who is in good health and exercises regularly. This information will be used to provide a recommendation for the user.
Arguments
url: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6779524/
question: What are the potential benefits of Metformin for a 43-year-old male who is in good health and exe...
Output: The potential benefits of Metformin for a 43-year-old male who is in good health and exercises re...


Using the file_write tool
Thought: I am compiling the information gathered so far into a document named 'metformin.md'. This document will summarize the findings on the usage of Metformin as a drug to treat aging and aging-related illnesses. It will also include links to the references and resources used to find the information. Finally, it will provide a recommendation for a 43-year-old male, in good health and who regularly exercises, as to whether he would benefit from taking Metformin. The recommendation will be explained and justified with sources, and potential risks and tradeoffs from taking the medication will be highlighted.
Arguments
filename: metformin.md
text: # Metformin and Aging  ## Summary of Findings  Metformin, a drug commonly used to treat diabetes,...
Output: File metformin.md written successfully


Using the final_answer tool
Arguments
input: The task has been completed. The research on the usage of Metformin as a drug to treat aging and ...
Output: The task has been completed. The research on the usage of Metformin as a drug to treat aging and ...
```