---
sidebar_position: 9
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

```bash wordWrap=true
% bondai

Loading BondAI...
******************ENTERING CHAT******************
You are entering a chat with BondAI...
You can exit any time by typing 'exit'.

Hello! I'm BondAI, your friendly and helpful assistant. I'm here to assist you with any tasks or questions you might have. How can I assist you today?

I want you to write a story about unicorns and save it to a file named unicorns.md.
Using tool file_write: Writing a story about unicorns and saving it to a file named unicorns.md
Using tool final_answer...

A story about unicorns has been successfully written and saved to a file named unicorns.md. The story is set in an enchanted forest and describes the magical and majestic nature of unicorns, their daily routines, and their harmonious relationship with other creatures in the forest.
```

## CLI Default Tools

When starting the CLI, BondAI will load the following tools by default.

- **DalleTool** - Allows BondAI to generate images using the Dalle-E text to image model.
- **ImageAnalysisTool** - Allows the Agent to use GPT4 Vision to analyze images.
- **DuckDuckGoSearchTool** - This is the default search tool loaded by BondAI as it requires no API keys or additional configuration.
- **WebsiteQueryTool** - Allows the Agent to query information about websites. Note that this tool has integrated semantic search. If the content of the website exceeds the LLM's context window size BondAI will automatically convert the content to Embeddings and semantically filter it to fit inside the context window.
- **FileQueryTool** - Allows BondAI to query file contents. Note that this tool has integrated semantic search. If the content of the file exceeds the LLM's context window size BondAI will automatically convert the content to Embeddings and semantically filter it to fit inside the context window.
- **DownloadFileTool** - Allows BondAI to download files from the internet and save them to local files.
- **FileWriteTool** - Allows BondAI to save text to a local file.
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
bondai --enable-prompt-logging --quiet
```

- **--server [PORT]** - Starts the BondAI API server. Learn more about the [BondAI API here](./category/api-specification).
- **--enable-prompt-logging [LOG_DIR]** - Turns on prompt logging which will write all prompt inputs into the specified directory. If no directory is provided BondAI will default to saving logs within the current directory.
- **--quiet** - Suppress agent output. Unless specified the agent will print detailed information about each step it's taking and the tools it's using.

