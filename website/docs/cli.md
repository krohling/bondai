---
sidebar_position: 3
---

import googleLogo from './img/google-logo.png'
import alpacaMarketsLogo from './img/alpaca-markets-logo.jpeg'
import postgresLogo from './img/postgres-logo.jpeg'
import blandaiLogo from './img/blandai-logo.jpeg'
import duckduckgoLogo from './img/duckduckgo-logo.png'
import gmailLogo from './img/gmail-logo.png'

# Command Line Interface

BondAI comes with an easy to use Command Line Interface for an "out of the box" Agent experience that includes a number of default tools.

## 🚀 Getting Started

Installing BondAI is easy:

```bash
pip install bondai
```

Once you've installed BondAI the CLI will be available as an executable in your shell. Before running the CLI you will need to set the OPENAI_API_KEY environment variable.

```bash
export OPENAI_API_KEY=sk-XXXXXXXXXX
```

When you start BondAI the Task Assistant Agent will ask you about the task you want to run and gather any necessary details. To start the CLI just run `bondai` in your shell.

```
% bondai

Loading BondAI...
Skipping Gmail tools because gmail-token.pickle file is not present.

Hello! How can I assist you today?

I want you to write a story about unicorns and save it to a file named unicorns.md.

Just to confirm, you would like me to write a story about unicorns and save it to a file named unicorns.md. Is that correct? Also, do you have a budget for this task?

That is correct. I don't have a budget for this task.
```

The Task Assistant Agent may ask you if you have a budget. This allows you to specify a maximum amount that you're willing to spend on OpenAI API credits to accomplish this task. If you don't want to set a budget just say you have no budget. Once you've confirmed the details of the task BondAI will get started using it's tools.

```
Using the file_write tool
Thought: Saving the unicorn story to a file.
Arguments
filename: unicorns.md
text: Once upon a time, in a land filled with vibrant colors and shimmering waters, there lived a herd ...
Output: File unicorns.md written successfully
Total Cost: $0.21


Using the final_answer tool
Arguments
input: The short story about unicorns has been written and saved to a file named unicorns.md successfully.
Output: The short story about unicorns has been written and saved to a file named unicorns.md successfully.
Total Cost: $0.24

Your short story about unicorns has been written and saved successfully to a file named unicorns.md. Is there anything else you would like assistance with?
```

## CLI Default Tools

When starting the CLI, BondAI will load the following tools by default.

- **DuckDuckGoSearchTool** - This is the default search tool loaded by BondAI as it requires no API keys or additional configuration.
- **WebsiteQueryTool** - Allows the Agent to query information about websites. Note that this tool has integrated semantic search. If the content of the website exceeds the LLM's context window size BondAI will automatically convert the content to Embeddings and semantically filter it to fit inside the context window.
- **FileQueryTool** - Allows BondAI to query file contents. Note that this tool has integrated semantic search. If the content of the file exceeds the LLM's context window size BondAI will automatically convert the content to Embeddings and semantically filter it to fit inside the context window.
- **DownloadFileTool** - Allows BondAI to download files from the internet and save them to local files.
- **FileWriteTool** - Allows BondAI to save text to a local file.
- **DalleTool** - Allows BondAI to generate images using the Dalle-E text to image model.

**Dangerous Tools** are only loaded if the `--enable-dangerous` command line argument is specified.

- **PythonREPLTool** - Allows the Agent run Python scripts.
- **ShellTool** - Allows the Agent access to the shell.


## Additional Supported Tools

<img src={googleLogo} alt="google logo" width="20"/> <h3 style={{display: 'inline', marginLeft: '10px'}}>Google Search</h3>

Allows BondAI to use the Google Search API to search the internet. If this tool is loaded BondAI will **not load the DuckDuckGoSearchTool** tool since doing so would be redundant. This tool equires the following environment variables:
```
export GOOGLE_API_KEY=XXXXXXXXXX
export GOOGLE_CSE_ID=XXXXXXXXXX
```


<img src={blandaiLogo} alt="blandai logo" width="25"/> <h3 style={{display: 'inline', marginLeft: '10px'}}>BlandAI</h3>

Allows BondAI to use the BlandAI API to make phone calls and process call transcripts. This tool requires the following environment variable:
```
export BLAND_AI_API_KEY=XXXXXXXXXX
```


<img src={alpacaMarketsLogo} alt="alpaca markets logo" width="25"/> <h3 style={{display: 'inline', marginLeft: '10px'}}>Alpaca Markets</h3>

Allows BondAI to use the Alpaca Markets API to buy and sell stocks and crypto. This tool requires the following environment variables:
```
export ALPACA_MARKETS_API_KEY=XXXXXXXXXX
export ALPACA_MARKETS_SECRET_KEY=XXXXXXXXXX
```


<img src={postgresLogo} alt="postgresql logo" width="30"/> <h3 style={{display: 'inline', marginLeft: '10px'}}>PostgreSQL</h3>

Allows BondAI to automatically query a Postgres database. Note that the specified user must have the ability to query the database schema. This tool requires the following environment variable:
```
export PG_URI=postgresql://user:password@host:port/database
```

Alternative you can use the following environment variables:
```
export PG_HOST=host
export PG_PORT=5432
export PG_USERNAME=user
export PG_PASSWORD=password
export PG_DBNAME=database
```

<img src={gmailLogo} alt="gmail logo" width="30"/> <h3 style={{display: 'inline', marginLeft: '10px'}}>Gmail</h3>

Allows BondAI to search and read emails. BondAI will search the local directory for a file named `gmail-token.pickle`. If this file is found and contains valid gmail credentials the Gmail tools will be automatically loaded.



## CLI Command Line Arguments

The following command line arguments can be specified to change the CLI behavior. For example:
```bash
bondai --enable-dangerous --enable-prompt-logging --quiet
```

- **--enable-dangerous** - Allows potentially dangerous Tools to be loaded (i.e. ShellTool and PythonREPLTool)
- **--server [PORT]** - Starts the BondAI API server. Learn more about the [BondAI API here](./category/api-specification).
- **--enable-prompt-logging [LOG_DIR]** - Turns on prompt logging which will write all prompt inputs into the specified directory. If no directory is provided BondAI will default to saving logs within the current directory.
- **--load-tools my_tools.py** - If this option is specified no tools will be loaded by default. Instead BondAI will load the specified Python file and look for a function named get_tools(). This function should return a list of Tools.
- **--quiet** - Suppress agent output. Unless specified the agent will print detailed information about each step it's taking and the tools it's using.

