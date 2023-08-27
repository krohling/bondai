<p align="center">
<img src="assets/bondai-logo.png" alt="Description or Alt text" style="border-radius: 10px; width: 50%;"  alt="logo">
</p>

<p align="center">
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/pypi/v/bondai" alt="PyPI">
</p>
<p align="center"><em>Meet BondAI, a truly open source, AI-powered assistant with a lightweight, versatile API for seamless integration into applications.</em></p>

## What is BondAI?

**BondAI** is a truly open-source framework tailored for integrating and customizing Conversational AI Agents. Built on *OpenAI's [function calling support](https://openai.com/blog/function-calling-and-other-api-updates), **BondAI** handles many of the implementation complexities involved in creating a Conversational Agent, including memory management, error handling, integrated semantic search, a powerful set of out of the box tools, as well as the ability to easily create new, custom tools. Additionally, **BondAI** includes a **CLI** interface, enabling anyone with an OpenAI API Key to run a powerful command line agent with a pre-configured set of tools.

*Interested in an agent running on an OSS model (i.e. Llama 2)? Check out **Plans For Finetuning Llama 2** below!

## Why build BondAI?

I truly believe that AI agents are the future! After a bit of experimentation I was blown away by their ability to problem solve and execute on complex tasks with very little guidance. However, I was also frustrated by much of the existing tooling. I found existing agents unable to complete simple tasks and framework APIs felt unnecessarily complex, making it difficult to optimize the important parts of my agent implementations.

I hope you like **BondAI** and [I'd love feedback](mailto:kevin@kevinrohling.com) on whether you think I've managed to solve some of these problems and how it could be better :)

## Installation

```bash
pip install bondai
```

## Examples

#### Online Research

Requires a [Google Search API Key and CSE ID](https://developers.google.com/custom-search/v1/overview).

```bash
export OPENAI_API_KEY=XXXXXXX
export GOOGLE_API_KEY=XXXXXXX
export GOOGLE_CSE_ID=XXXXXXX
```

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


#### Buy/Sell Stocks

Requires an [Alpaca Markets](https://alpaca.markets/) account. Using [Paper Trading](https://alpaca.markets/docs/trading/paper-trading/) is strongly recommended!

```bash
export OPENAI_API_KEY=XXXXXXX
export ALPACA_MARKETS_API_KEY=XXXXXXX
export ALPACA_MARKETS_SECRET_KEY=XXXXXXX
```

```python
from bondai import Agent
from bondai.tools.alpaca_markets import CreateOrderTool, GetAccountTool, ListPositionsTool

task = """I want you to sell off all of my existing positions.
Then I want you to buy 10 shares of NVIDIA with a limit price of $456."""

Agent(tools=[
  CreateOrderTool(),
  GetAccountTool(),
  ListPositionsTool()
]).run(task)
```

#### Integrating LangChain Tools

```bash
export OPENAI_API_KEY=XXXXXXX
```

```python
from pydantic import BaseModel
from bondai.tools import LangChainTool
from langchain.tools import ShellTool

class ShellToolParameters(BaseModel):
    commands: str
    thought: str

task = """I have a database running on RDS in the us-west-2 region. Is this database configured to force SSL connections? 
I already have the AWS CLI installed btw."""

Agent(tools=[
  LangChainTool(ShellTool(), ShellToolParameters), 
]).run(task)
```

## Using the CLI Tool

**BondAI** comes with a CLI Tool for an "out of the box" agent experience that includes a number of default tools.

#### CLI Usage

```bash
>>bondai
Welcome to BondAI!
I have been trained to help you with a variety of tasks.
To get started, just tell me what task you would like me to help you with. The more descriptive you are, the better I can help you.
If you would like to exit, just type 'exit'.

What can I help you with today?

I want you to research the usage of Metformin as a drug to treat aging and aging related illness.
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


## Docker Container

It is highly recommended that you run **BondAI** from within a container if you are going to use tools with file system access. Use the following steps below to build and run the **BondAI** container. A directory named 'agent-volume' will be created which will be used as the working directory for execution of the CLI tool on the container.

```bash
cd docker
./build-container.sh
./run-container.sh OPENAI_API_KEY=XXXXX ENV1=XXXX ENV2=XXXX --arg1 --arg2
```


## APIs

#### Agent
The Agent module provides a flexible interface for agents to interact with different tools and functions. The Agent makes decisions based on given tasks, uses available tools to provide a response, and handles exceptions smoothly.

**init:** Instantiate a new Agent
- *prompt_builder* (default=DefaultPromptBuilder): Responsible for building the prompts at each step.
- *tools* (default=[]): The list of tools available to the Agent.
- *llm* (default=MODEL_GPT4_0613): The primary model used by the Agent.
- *fallback_llm* (default=MODEL_GPT35_TURBO_0613): Secondary model the Agent falls back on when an appropriate response was not received by the primary model.
- *final_answer_tool* (default=DEFAULT_FINAL_ANSWER_TOOL): Tool that provides the final answer/response back to the user.
- *budget* (default=None): The Agent will keep track of the cost for all API calls made to OpenAI. If this budget is exceeded the Agent will raise a BudgetExceededException.
- *quiet* (default=False): If true, the Agent will suppress most print messages.

**run(task=''):** Continuously runs the agent until a final answer is received or the budget is exceeded.
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

class MyCustomTool(Tool):
    def __init__(self):
        super(MyCustomTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
    
    def run(self, arguments):
        # Tool's main functionality here.
        param1 = arguments.get("param1")
        param2 = arguments.get("param2")
```


## Plans For Finetuning Llama 2

The holy grail (IMHO) is to have a capable Agent that can run fully independent of OpenAI and all other 3rd party hosted models. Unfortunately, current open source models make poor Agents. However, I believe that if a robust enough dataset of Agent interactions can be captured, an open source model can be fine tuned, greatly improving it's Agent capabilities.

If you would like to participate and help this cause, **simply enable prompt logging** while running **BondAI** which will store all the LLM prompts and responses. [Either email them to me](mailto:kevin@kevinrohling.com) or make a PR to this repository adding your prompt logs to the prompt-dataset directory. Note that I will make both the dataset and the resulting models available for free on Github and HuggingFace.

My goal is to get to a dataset of **50K prompts**. Let's see what we can do!

**Note: PLEASE make sure that any logs you share are free of personally identifying or sensitive data as they will be shared publically and used to train future models.**

## Contribution

Want to contribute to **BondAI**? Please do!
Check out the contribution [instruction & guidelines](./CONTRIBUTING.md).
