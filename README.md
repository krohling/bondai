<a href="https://bondai.dev">
<p align="center">
<img src="assets/bondai-logo.png" alt="Description or Alt text" style="border-radius: 10px; width: 50%;"  alt="logo">
</p>
</a>

<p align="center">
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://pypi.org/project/bondai/"><img src="https://img.shields.io/pypi/v/bondai" alt="PyPI"></a>
    <a href="https://hub.docker.com/r/krohling/bondai"><img src="https://img.shields.io/docker/v/krohling/bondai?logo=docker" alt="Docker"></a>
</p>
<p align="center"><em>Meet BondAI, an open source, AI-powered assistant with a lightweight, versatile API for seamless integration into your own applications.</em></p>

# <a href="https://bondai.dev">BondAI Homepage</a>

Checkout the BondAI Homepage ([https://bondai.dev](https://bondai.dev)) for in depth documentation, examples and API specification.

# Getting Started

There are 3 ways to use BondAI:

1) 🛠️ **Command Line Interface (CLI)** - This is the easiest way to get up and running fast. Run BondAI on your command line with a pre-configured set of tools.

2) 🐋 **Docker** - Running BondAI in a Docker container is recommended if you plan on using tools that run code or directly access your shell.

3) 🏗️ **Start Coding with BondAI** - Integrate BondAI into your own codebase and start building your own agents.

## 🚀 Installation

Installing BondAI is easy:

```bash
pip install bondai
```

## 🛠️ Command Line Interface (CLI)

Once you've installed BondAI using `pip install bondai` the CLI will be available as an executable accessible simply by running `bondai` in your shell. [Learn more about all of the tools and options available through the CLI](https://bondai.dev/docs/cli).

Before running `bondai` you will need to set the OPENAI_API_KEY environment variable.
```bash
export OPENAI_API_KEY=sk-XXXXXXXXXX
```

Once the environment variable has been set you can run `bondai` to start the CLI.

```bash
% bondai                   
Loading BondAI...
Skipping Gmail tools because gmail-token.pickle file is not present.

Hello! How can I assist you today?
```


## 🐋 Docker

BondAI Docker images are available on [DockerHub here](https://hub.docker.com/r/krohling/bondai). If you intend to use tools that run arbitrary code (*PythonREPLTool*) or access your shell (*ShellTool*) it is highly recommended that you run BondAI in a Docker container as these tools can damage your machine.

Before running the BondAI Docker container it is recommended that you create a directory named 'agent-volume' and mount it as a volume on the container. This will be used as the Agent's working directory and allows you to easily share files with the Agent.

```bash
mkdir agent-volume
docker pull krohling/bondai:latest
docker run -it --rm \
           -v ./agent-volume:/agent-volume \
           -w /agent-volume \
           OPENAI_API_KEY=sk-XXXXXXXXXX \
           bondai:latest bondai
```

## 🔥 Start Coding with BondAI

BondAI has a straightforward API for creating powerful AI Agents. Check out our [examples](https://bondai.dev/docs/category/examples) for ideas on how to get started.  Remember to set your *OPENAI_API_KEY* environment variable before running your BondAI Agent.

```python
from bondai import Agent
from bondai.tools.search import DuckDuckGoSearchTool
from bondai.tools.website import WebsiteQueryTool
from bondai.tools.file import FileWriteTool

task = """I want you to research the usage of Metformin as a drug to treat aging and aging related illness. 
You should only use reputable information sources, ideally peer reviewed scientific studies. 
I want you to summarize your findings in a document named metformin.md and includes links to reference and resources you used to find the information. 
Additionally, the last section of your document you should provide a recommendation for a 43 year old male, in good health and who regularly exercises as to whether he would benefit from taking Metformin. 
You should explain your recommendation and justify it with sources. 
Finally, you should highlight potential risks and tradeoffs from taking the medication."""

Agent(tools=[
  DuckDuckGoSearchTool(),
  WebsiteQueryTool(),
  FileWriteTool()
]).run(task)
```

## BondAI Integrations

BondAI comes out of the box with a powerful set of integrations.

|     |  |  |
| -------- | ------- |------- |
| <img src="assets/logos/openai-logo.png" alt="openai logo" width="50"/> | **OpenAI**     | BondAI supports any combination of OpenAI models and services including GPT-4, GPT-3.5, Dalle-E 3, and Embeddings.  |
| <img src="assets/logos/azure-logo.png" alt="azure logo" width="50"/> | **Microsoft Azure**     | BondAI fully supports connectivity to GPT-N, Dalle-E and Embedding APIs through [Microsoft's Azure OpenAI services](https://azure.microsoft.com/en-us/products/ai-services/openai-service).  |
| <img src="assets/logos/google-logo.png" alt="google logo" width="50"/>  | **Google Search**    | Allows BondAI to search the internet. [Requires a Google Search API Key and CSE ID](https://developers.google.com/custom-search/v1/introduction) |
| <img src="assets/logos/duckduckgo-logo.png" alt="duckduckgo logo" width="50"/> | **DuckDuckGo**     | Allows BondAI to search the internet. No API keys required. |
| <img src="assets/logos/alpaca-markets-logo.jpeg" alt="alpaca markets logo" width="50"/> | **Alpaca Markets**     | Allows BondAI to buy and sell stocks and crypto. [Requires an Alpaca Markets account.](https://alpaca.markets/)  |
| <img src="assets/logos/postgres-logo.jpeg" alt="postgres logo" width="75"/>    | **PostgreSQL**    | BondAI can automatically extract the schema from a Postgres DB and process natural language queries. |
| <img src="assets/logos/blandai-logo.jpeg" alt="bland.ai logo" width="50"/> | **Bland AI**     | Allows BondAI to make phone calls and process/retrieve call transcripts. [Requires a Bland.ai account.](https://www.bland.ai/)  |
| <img src="assets/logos/gmail-logo.png" alt="gmail logo" width="50"/> | **Gmail**     | Allows BondAI to search and read emails.  |
| <img src="assets/logos/langchain-logo.jpeg" alt="langchain logo" width="50"/> | **LangChain**     | Use BondAI's LangChainTool class to import any tool from LangChain into BondAI.  |