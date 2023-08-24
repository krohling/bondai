<p align="center">
<img src="assets/bondai-logo.png" alt="Description or Alt text" style="border-radius: 10px; width: 50%;"  alt="logo">
</p>

<p align="center">
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/pypi/v/bondai" alt="PyPI">
</p>
<p align="center"><em>Meet BondAI, a truly open source, AI-powered assistant with a lightweight, versatile API for seamless integration into applications.</em></p>

## What is BondAI?

**BondAI** is a truly open-source framework tailored for integrating and customizing Conversational AI Agents. Built on OpenAI's [function calling support](https://openai.com/blog/function-calling-and-other-api-updates), **BondAI** handles many of the implementation complexities including memory management, error handling, integrated semantic search, a powerful set of out of the box tools, as well as the ability to easily import tools from LangChain.

Additionally, **BondAI** includes a **CLI tool**, enabling anyone with an OpenAI API Key to run a powerful command line agent with a pre-configured set of tools. **BondAI** 

## Why build BondAI?

I truly believe that AI agents are the future! After a bit of experimentation I was blown away by their ability to problem solve and execute on complex tasks with very little guidance. However, I was also frustrated by much of the existing tooling. I found existing agents unable to complete useful tasks and framework APIs felt unnecessarily complex, making it difficult to optimize the important parts of my agent implementation.


I hope you like it and [I'd love feedback](mailto:kevin@kevinrohling.com) on whether you think I've managed to solve some of these problems :)


## Installation

```bash
pip install bondai
```

## Usage

### Agent APIs

### Custom Tools

### Customizing Prompts


## Using the CLI Tool

### Default Tools
By default the **bondai** CLI command will automatically load the following tools:
- **DuckDuckGoSearchTool** - Allows the model to use DuckDuckGo to search the web.
- **WebsiteQueryTool** - Allows the model to query content of websites. By default this is delegated to gpt-3.5-16k but if the content is too large for the model's context it will automatically use embeddings and semantic search.
- **FileQueryTool** - Allows the model to query the content of files. By default this is delegated to gpt-3.5-16k but if the content is too large for the model's context it will automatically use embeddings and semantic search.
- **DownloadFileTool** - Allows the model to download files locally from the web. This is useful for many research tasks.
- **FileWriteTool** - Allows the model to write content to files. Thsi is useful for saving work or exporting the results of a research or generation task to a file.

### Environment Variables

An OpenAI API Key is required.
```bash
export OPENAI_API_KEY=XXXXXXX
```

If the GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables are provided the **bondai** CLI will load the *GoogleSearchTool* instead of the *DuckDuckGoSearchTool*.
```bash
export GOOGLE_API_KEY=XXXXXXX
export GOOGLE_CSE_ID=XXXXXXX
```

If the ALPACA_MARKETS_API_KEY and ALPACA_MARKETS_SECRET_KEY environment variables are provided the **bondai** CLI will load the *CreateOrderTool*, *GetAccountTool*, and *ListPositionsTool*.

```bash
export ALPACA_MARKETS_API_KEY=XXXXXXX
export ALPACA_MARKETS_SECRET_KEY=XXXXXXX
```

### Gmail Integration

[Check here](https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/) for information on generating a **gmail-token.pickle** file with credentials for accessing your gmail account. If this file is present in the root directory where the **bondai** CLI is running it will load the *ListEmailsTool* and *QueryEmailsTool* tools.

### Langchain Tools
When the **bondai** CLI starts it will check to see if LangChain is installed. If it is it will automatically load the following LangChain tools:

- **ShellTool** - This allows the model to generate and run arbitrary bash commands.
- **PythonREPLTool** - This allows the model to generate and run arbitrary Python commands.

**Warning: Both of these tools are considered dangerous and require that the --enable_dangerous argument is specified when running starting the CLI. Is is strongly recommended that these are run within a containerized environment.**
```bash
bondai --enable_dangerous
```

### Usage

```bash
>>bondai
Welcome to BondAI!
I have been trained to help you with a variety of tasks.
To get started, just tell me what task you would like me to help you with.
If you would like to exit, just type 'exit'.

What can I help you with today?

I want you to research the usage of Metformin as a drug to treat aging and aging related illness.
You should only use reputable information sources, ideally peer reviewed scientific studies. 
I want you to summarize your findings in a document named metformin.md and includes links to reference and resources you used to find the information. 
Additionally, the last section of your document you should provide a recommendation for a 43 year old male, in good health and who regularly exercises as to whether he would benefit from taking Metformin. 
You should explain your recommendation and justify it with sources. 
Finally, you should highlight potential risks and tradeoffs from taking the medication.
```

## Examples

### Online Research

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


### Buy/Sell Stocks

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

### Integrating LangChain Tools

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


## Plans For Finetuning Llama 2


## Plans For Future Development


## :wrench: Development

Want to contribute to **BondAI**?
Check out the contribution [instruction & guidelines](/CONTRIBUTING.md).