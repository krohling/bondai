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
Finally, you should highlight potential risks and tradeoffs from taking the medication.
```

#### Command Line Arguments

The following arguments can be passed on the command line to change how the **BondAI** CLI tool works.

- **--enable-dangerous** - Allows potentially dangerous Tools to be loaded (i.e. ShellTool and PythonREPLTool)
- **--enable-prompt-logging log_dir** - Turns on prompt logging which will write all prompt inputs into the specified directory. If no directory is provided **BondAI** will defaul to *logs* within the current directory.
- **--load-tools my_tools.py** - If this option is specified no tools will be loaded by default. Instead **BondAI** will load the specified Python file and look for a function named **get_tools()**. This function should return a list of Tools.
- **--quiet** - Suppress agent output. Unless specified the agent will print detailed information about each step it's taking.

```bash
bondai --enable-dangerous --enable-prompt-logging logs --load-tools my_tools.py
```



#### Default CLI Tools
By default the **BondAI** CLI command will automatically load the following tools:
- **DuckDuckGoSearchTool** - Allows the model to use DuckDuckGo to search the web.
- **WebsiteQueryTool** - Allows the model to query content of websites. By default this is delegated to gpt-3.5-16k but if the content is too large for the model's context it will automatically use embeddings and semantic search.
- **FileQueryTool** - Allows the model to query the content of files. By default this is delegated to gpt-3.5-16k but if the content is too large for the model's context it will automatically use embeddings and semantic search.
- **DownloadFileTool** - Allows the model to download files locally from the web. This is useful for many research tasks.
- **FileWriteTool** - Allows the model to write content to files. This is useful for saving work or exporting the results of a research or generation task to a file.

#### CLI Environment Variables

An OpenAI API Key is required.
```bash
export OPENAI_API_KEY=XXXXXXX
```

If the GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are provided the **BondAI** CLI will load the *GoogleSearchTool* instead of the *DuckDuckGoSearchTool*.
```bash
export GOOGLE_API_KEY=XXXXXXX
export GOOGLE_CSE_ID=XXXXXXX
```

If the ALPACA_MARKETS_API_KEY and ALPACA_MARKETS_SECRET_KEY environment variables are provided the **BondAI** CLI will load the *CreateOrderTool*, *GetAccountTool*, and *ListPositionsTool*.

```bash
export ALPACA_MARKETS_API_KEY=XXXXXXX
export ALPACA_MARKETS_SECRET_KEY=XXXXXXX
```

#### Gmail Integration

[Check here](https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/) for information on generating a **gmail-token.pickle** file with credentials for accessing your gmail account. If this file is present in the root directory where the **BondAI** CLI is running it will load the *ListEmailsTool* and *QueryEmailsTool* tools automatically.

#### Langchain Tools
When the **BondAI** CLI starts it will check to see if LangChain is installed. If it is it will automatically load the following LangChain tools:

- **ShellTool** - This allows the model to generate and run arbitrary bash commands.
- **PythonREPLTool** - This allows the model to generate and run arbitrary Python commands.

**Warning: Both of these tools are considered dangerous and require that the --enable_dangerous argument is specified when running starting the CLI. Is is strongly recommended that these are run within a containerized environment.**


## Docker

It is highly recommended that you run **BondAI** from within a container if you are going to use tools with file system access. There's two options for running Docker:

> Download Docker Desktop for a UI based experience, which gives you quick access to the log viewer and the terminal for the bondai container.
https://www.docker.com/products/docker-desktop/

### Docker CLI

From the command line follow the steps below to build and run the **BondAI** container. A directory named 'agent-volume' will be created which will be used as the working directory for execution of the CLI tool on the container.

```bash
cd docker
./build-container.sh
./run-container.sh OPENAI_API_KEY=XXXXX ENV1=XXXX ENV2=XXXX --arg1 --arg2
```

### Docker Compose 

The docker-compose.yml file which is located in the `./docker` directory, makes use of a .env file and a pre-configured **volume** which is mapped to an `./agent-volume` directory

There's two options with Docker Compose. From the command line with this command:

```bash
cd ./docker
docker-compose up
```

Or if you use vsCode, install the official Docker Extension, then right click on the `./docker/docker-compose.yml` file and select `Compose Up`

> Don't forget to open sample.env, add your Environment Keys and save as `.env`


## APIs

#### Agent
The Agent module provides a flexible interface for agents to interact with different tools and functions. The Agent makes decisions based on given tasks, uses available tools to provide a response, and handles exceptions smoothly.

**init:** Instantiate a new Agent
- *prompt_builder* (default=DefaultPromptBuilder): Responsible for building the prompts at each step.
- *tools* (default=[]): The list of tools available to the Agent.
- *llm* (default=MODEL_GPT4_0613): The primary model used by the Agent.
- *fallback_llm* (default=MODEL_GPT35_TURBO_0613): Secondary model the Agent falls back on when an appropriate response was not received by the primary model.
- *final_answer_tool* (default=DEFAULT_FINAL_ANSWER_TOOL): Tool that provides the final answer/response back to the user.
- *quiet* (default=False): If true, the Agent will suppress most print messages.

**run(task='', task_budget=None):** Continuously runs the agent until the task is completed or the budget is exceeded. The Agent will keep track of the cost for all API calls made to OpenAI. If this budget is exceeded the Agent will raise a BudgetExceededException.
**run_once(task=''):** Executes a single step of the agent's process. Returns an instance of AgentStep.
**reset_memory():** Clears the agent's memory of previous steps.



#### Custom Tools

```python
# Required imports
from pydantic import BaseModel
from bondai.tools import Tool

# Define Tool metadata
TOOL_NAME = 'my_unique_tool_name'
TOOL_DESCRIPTION = "A thorough description of what my Tool implementation does. Better explanations lead to better tool usage."

# Describe the parameters your tool accepts. It is recommended but not required to have a 'thought' parameter.
class Parameters(BaseModel):
    param1: str
    param2: int
    thought: str

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