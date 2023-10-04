---
sidebar_position: 2
---

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

Once you've installed BondAI using `pip install bondai` the CLI will be available as an executable accessible simply by running `bondai` in your shell. [Learn more about all of the tools and options available through the CLI](./cli).

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

BondAI has a straightforward API for creating powerful AI Agents. Check out our [examples](./category/examples/) for ideas on how to get started.  Remember to set your *OPENAI_API_KEY* environment variable before running your BondAI Agent.

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