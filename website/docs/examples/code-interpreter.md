---
sidebar_position: 3
---

import gdpChart from './img/us_gdp_2000_2010.png'

# Code Interpreter

In this example we demonstrate BondAI's ability to combine online research and data visualization tasks. We ask BondAI to plot a line chart of U.S. GDP between 2000 and 2010, which requires using a combination of web search, data extraction and data visualization tools (ie matplotlib).

First we will configure the environment variables for OpenAI and Google Search.

```bash
export OPENAI_API_KEY=sk-XXXXXXXXXX
export GOOGLE_API_KEY=XXXXXXXXXX
export GOOGLE_CSE_ID=XXXXXXXXXX
```

Next we will create an Agent with 3 tools:
- **GoogleSearchTool** allows the Agent to search the internet.
- **WebsiteQueryTool** allows the Agent to query information about websites. Note that this tool has integrated semantic search. If the content of the website exceeds the LLM's context window size BondAI will automatically convert the content to Embeddings and semantically filter it to fit inside the context window.
- **PythonREPLTool** allows the Agent run Python scripts.

```python
from bondai import Agent
from bondai.tools import PythonREPLTool
from bondai.tools.search import GoogleSearchTool
from bondai.tools.website import WebsiteQueryTool

task = "I want you to generate a line chart of the U.S. GDP from 2000 to 2010."

Agent(tools=[
  GoogleSearchTool(),
  WebsiteQueryTool(),
  PythonREPLTool()
]).run(task)
```

## Example Output

<img src={gdpChart} alt="gdp chart" width="500"/>

```
Using the google_search tool
Thought: I'm using the google_search tool to find a reliable source for U.S. GDP data from 2000 to 2010.
Arguments
query: U.S. GDP data from 2000 to 2010
count: 5
page: 1
Output: [GDP by State | U.S. Bureau of Economic Analysis (BEA)](https://www.bea.gov/data/gdp/gdp-state) [...


Using the website_query tool
Thought: I'm using the website_query tool to extract the U.S. GDP data from 2000 to 2010 from the Statista website.
Arguments
url: https://www.statista.com/statistics/188105/annual-gdp-of-the-united-states-since-1990/
question: What is the annual GDP of the United States from 2000 to 2010?
Output: The annual GDP of the United States from 2000 to 2010 is as follows:  2000: $10,251.9 billion 200...


Using the Python_REPL tool
Arguments
query: import matplotlib.pyplot as plt  years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2...
Output: This command ran successfully with no output.


Using the Python_REPL tool
Arguments
query: plt.plot(years, gdp) plt.xlabel('Years') plt.ylabel('GDP in billions') plt.title('U.S. GDP from 2...
Output: This command ran successfully with no output.


Using the final_answer tool
Arguments
input: The line chart of the U.S. GDP from 2000 to 2010 has been successfully generated and saved as 'us...
Output: The line chart of the U.S. GDP from 2000 to 2010 has been successfully generated and saved as 'us...
```