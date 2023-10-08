---
sidebar_position: 1
---

import bondaiLogo from '../img/bondai-logo.png'
import googleLogo from '../img/google-logo.png'
import alpacaMarketsLogo from '../img/alpaca-markets-logo.jpeg'
import postgresLogo from '../img/postgres-logo.jpeg'
import blandaiLogo from '../img/blandai-logo.jpeg'
import duckduckgoLogo from '../img/duckduckgo-logo.png'
import gmailLogo from '../img/gmail-logo.png'
import openaiLogo from '../img/openai-logo.png'
import azureLogo from '../img/azure-logo.png'
import langchainLogo from '../img/langchain-logo.jpeg'

# BondAI Tools

Tools are what give AI Agents the power to interact with their environment. Combined with the planning capabilities of LLMs, AI Agents are able to break down complex tasks that may require multiple steps and use tools to accomplish their goals. In addition to using BondAI's comprehensive list of built in tools you can build you own custom tools and even import tools from LangChain.

# Example Tools

|     |  |
| -------- | ------- |
| **AgentTool**     | This tool allows Agent's to delegate complex tasks to other Agents creating a heirarchical Agent architecture.  |
| **HumanTool**     | This tool uses allows BondAI to communicate with users via the CLI interface.  |
| **LangChainTool**     | This tool wraps tools implemented in LangChain and makes it possible for them to be used by BondAI Agents.  |
| **PythonREPLTool**     | This tool allows BondAI to write and execute Python code. Note that it is highly recommended that this tool be used from within a Docker environment as it may damage the host machine.  |
| **ResponseQueryTool**     | BondAI will automatically detect if a tool returns a large response (>2000 tokens). To prevent this response from overwhelming the Agent's memory the output will be passed to the ResponseQueryTool which the Agent can then query to get information about the response.  |
| **ShellTool**     | This tool allows BondAI to interact with the users Shell and run arbitrary commands. Note that it is highly recommended that this tool be used from within a Docker environment as it may damage the host machine.  |
| **FileQueryTool**     | This tool allows BondAI to query the content of a file. This tool uses integrated Semantic search. If the content of the file is too large for the LLM's context window the content will automatically be converted to embeddings and filtered to fit within the context window.  |
| **FileWriteTool**     | This tool allows BondAI to write content to a specified filename.  |
| **FileReadTool**     | This tool allows BondAI to read the raw content of a specified filename. Note that when dealing with large files it is recommended to use the FileQueryTool as large files may overwhelm the Agent's memory.  |
| **DownloadFileTool**     | This tool allows BondAI to download files from the internet and save them locally to a specified filename.  |
| **ExtractHyperlinksTool**     | This tool allows BondAI retrieve the hyperlinks from the HTML of a specified website.  |
| **WebsiteQueryTool**     | This tool allows BondAI to query the content of a website. This tool uses integrated Semantic search. If the content of the website is too large for the LLM's context window the content will automatically be converted to embeddings and filtered to fit within the context window.  |

# Partner Tools

|     |  |  |
| -------- | ------- |------- |
| <img src={openaiLogo} alt="openai logo" width="50"/> | **OpenAI**     | BondAI supports any combination of OpenAI models and services including GPT-4, GPT-3.5, Dalle-E 3, and Embeddings.  |
| <img src={azureLogo} alt="azure logo" width="50"/> | **Microsoft Azure**     | BondAI fully supports connectivity to GPT-N, Dalle-E and Embedding APIs through [Microsoft's Azure OpenAI services](https://azure.microsoft.com/en-us/products/ai-services/openai-service).  |
| <img src={googleLogo} alt="google logo" width="50"/>  | **Google Search**    | Allows BondAI to search the internet. [Requires a Google Search API Key and CSE ID](https://developers.google.com/custom-search/v1/introduction) |
| <img src={duckduckgoLogo} alt="duckduckgo logo" width="50"/> | **DuckDuckGo**     | Allows BondAI to search the internet. No API keys required. |
| <img src={alpacaMarketsLogo} alt="alpaca markets logo" width="50"/> | **Alpaca Markets**     | Allows BondAI to buy and sell stocks and crypto. [Requires an Alpaca Markets account.](https://alpaca.markets/)  |
| <img src={postgresLogo} alt="postgres logo" width="75"/>    | **PostgreSQL**    | BondAI can automatically extract the schema from a Postgres DB and process natural language queries. |
| <img src={blandaiLogo} alt="bland.ai logo" width="50"/> | **Bland AI**     | Allows BondAI to make phone calls and process/retrieve call transcripts. [Requires a Bland.ai account.](https://www.bland.ai/)  |
| <img src={gmailLogo} alt="gmail logo" width="50"/> | **Gmail**     | Allows BondAI to search and read emails.  |
| <img src={langchainLogo} alt="langchain logo" width="50"/> | **LangChain**     | Use BondAI's LangChainTool class to import any tool from LangChain into BondAI.  |

