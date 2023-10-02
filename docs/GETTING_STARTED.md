# GETTING STARTED

There are multiple ways to get started with Bondai:

**Example Setups**

1. Linux, PyCharm, CLI
2. Mac, vsCode, Docker, CLI
3. Mac, vsCode, Docker, Docker Desktop
4. Windows, vsCode, Docker, CLI
5. Windows, vsCode, Docker, Docker Desktop

For this basic example, we're going to demonstrate number 5.

## SOFTWARE PREREQUISITES

- Windows 11
- WSL (Windows Subsystem for Linux)
- Ubuntu 22.04
- Visual Studio Code (vsCode)
- Docker Extension for vsCode
- Docker Desktop

### FRESH INSTALLATION

Make sure you have all of the software programs installed and open vsCode and Docker Desktop.

1. From inside vsCode, press `CTRL+SHIFT+P` to open the command palette and search for **WSL**

2. Click on **WSL: Connect to WSL using Distro..** and select Ubuntu 22.04

> Next up we need to clone the Bondai Github Repo to your localhost and because we're connected to WSL, save it to a folder in your home directory, rather than a regular windows folder such as My Documents. It will load correctly and be faster keeping it all inside of the Linux environment.

3. `` CTRL + SHIFT + ` `` to open a Terminal window and create a new directory in your home; something like `apps` or `websites` or `repos`.

```bash
cd ~
mkdir apps
```

4. Assuming you dont have an existing project open in vsCode; When you open the left menu (Explorer Panel) you should see some blue buttons, select **Clone Repository**. 

5. From the drop down menu that appears, copy/paste the Bondai Github Repo URL: https://github.com/krohling/bondai and hit enter.

6. After its finished cloning you should see all the files in the left menu under "explorer".

7. Open the Docker folder and right click `docker-compose.yml` and select `Compose Up`

8. In the terminal that opens, you should see Docker building the Image and Container, when it has finished, go to Docker Desktop (and all being well), you will see the Bondai Docker Container running on port 8000 - the green icon symbolizes that is has started up successfully. Orange means something has gone wrong.

9. Click on the docker-bondai container and you will see the a sub menu with:

Logs, Inspect, Bind Mounts, Terminal, Files, Stats

10. Click on Terminal and in the command line type **bondai**, this will start **Bondai** ... you should see something like:

```bash
Loading BondAI...
Skipping Alpaca Markets tools because ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables are not set.
Skipping Gmail tools because gmail-token.pickle file is not present.
Loading LangChain tools...
Done loading LangChain tools
Dangerous Tools are enabled.

Welcome to BondAI!
I have been trained to help you with a variety of tasks.
To get started, just tell me what task you would like me to help you with. The more descriptive you are, the better I can help you.
If you would like to exit, just type 'exit'.

What can I help you with today?
```

## RUNNING BONDAI

There are two ways to use bondai: 

1. Out of the box; using default tools
2. Custom tools

### OUT OF THE BOX - DEFAULT

**GoogleSearchTool** loaded instead of **DuckDuckGoSearchTool**, assuming Google API env vars are provided.

```bash
bondai --enable-dangerous --enable-prompt-logging logs
```

Example of default setup

```python
from bondai import Agent
from bondai.tools.search import GoogleSearchTool # default tool
from bondai.tools.website import WebsiteQueryTool # default tool
from bondai.tools.website import DownloadFileTool # default tool
from bondai.tools.file import FileQueryTool # default tool
from bondai.tools.file import FileWriteTool # default tool

task = """I want you to research the usage of Metformin as a drug to treat aging and aging related illness. 
You should only use reputable information sources, ideally peer reviewed scientific studies. 
I want you to summarize your findings in a document named metformin.md and includes links to reference and resources you used to find the information. 
Additionally, the last section of your document you should provide a recommendation for a 43 year old male, in good health and who regularly exercises as to whether he would benefit from taking Metformin. 
You should explain your recommendation and justify it with sources. 
Finally, you should highlight potential risks and tradeoffs from taking the medication."""

Agent(tools=[
  GoogleSearchTool(),
  WebsiteQueryTool(),
  DownloadFileTool(),
  FileQueryTool(),
  FileWriteTool()
]).run(task)
```

### CUSTOM TOOLS

Create your own bondai python script and customize it to your task needs.

Home Automation example:

```bash
bondai --enable-dangerous --enable-prompt-logging logs --load-tools home_automation.py
```

Example of Home Automation setup

```python
from pydantic import BaseModel
from bondai import Agent
from bondai.tools import LangChainTool
from langchain.tools import ShellTool
from langchain.tools.python.tool import PythonREPLTool

task = "I want you to turn off my Bedroom Lamp. It's a Kasa smart plug btw on the same network."

class ShellToolParameters(BaseModel):
    commands: str
    thought: str

class PythonREPLParameters(BaseModel):
    query: str

shell_tool = ShellTool()
shell_tool.description = "This is a very powerful tool that allows you to run any shell command on this Ubuntu machine. Note that this tool only accepts a single string argument at a time and does not accept a list of commands." + f" args {shell_tool.args}".replace(
    "{", "{{"
).replace("}", "}}")

result = Agent(tools=[
  LangChainTool(shell_tool, ShellToolParameters), 
  LangChainTool(PythonREPLTool(), PythonREPLParameters)
]).run(task)
print(result.output)
```
