---
sidebar_position: 3
---

# Using Custom Tools with the CLI

Once you've build your own custom tool you may want to use it with the BondAI CLI. Fortunately, BondAI makes this super easy! In this example, we will use the QueryCountriesTool we built in the [Building Custom Tools](./custom-tool) section.

To use a custom tool with the BondAI CLI all that is needed is to create a `my_tools.py` file with a single function named `get_tools`. Note that you can name this file anything you like.

```python
from query_countries_tool import QueryCountriesTool

def get_tools():
    return [
        QueryCountriesTool()
    ]
```

With this file created now we can pass it to the BondAI CLI using the `--load-tools` command line argument.

```bash
bondai --load-tools ./my_tools.py
```

Now let's give this a try...

```bash
bondai --load-tools ./my_tools.py
Loading BondAI...
Loaded tools from ./my_tools.py

Hello! How can I assist you today?

What is Germany's population?


Using the query_countries_tool tool
Thought: Using the query_countries_tool to find the population of Germany.
Arguments
country_name: Germany
Output: **Germany** Population: 83240525 Language: German Area: 357114.0 Currency: EUR Region: Europe Sub...
Total Cost: $0.09


Using the final_answer tool
Arguments
input: The population of Germany is 83240525.
Output: The population of Germany is 83240525.
Total Cost: $0.11

The population of Germany is 83,240,525. Is there anything else you need assistance with?
```