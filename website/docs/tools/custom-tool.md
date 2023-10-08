---
sidebar_position: 2
---

# Building Custom Tools

By building your own custom tools you can give BondAI the power to interact with new products, external APIs, really just about anything! Fortunately, tools are super easy to build. In this example we'll build a tool that allows BondAI to ask questions about any country and get information back from the [RestCountries API](https://restcountries.com/).


### Step 1: Define your Tool's Name, Description and Parameters

For BondAI to use your tool it needs 3 pieces of information to tell the LLM about your tool. For the LLM to effectively use your tool your description should be highly detailed and informative.

- **Tool Name** - This should be an informative name for what your tool does. It's also important that it is unique to just your tool.
- **Tool Description** - This is a detailed description of what your tool does, what the parameters are used for, what information it returns and when to use it.
- **Tool Parameters** - The Parameters structure is used to encode the parameters shown to the LLM. You must include all possible parameters in this structure. It is common to include a 'thought' parameter which encourages the LLM to include it's reasoning for using the tool which has been shown to improve performance.

```python
from pydantic import BaseModel

TOOL_NAME = "query_countries_tool"
TOOL_DESCRIPTION = (
    "This tool allows you to search countries by name and get a list back with information about each country. "
    "The response includes incormation like the country's population size, currencies, languages and more. "
    "\nParameters:\n"
    "- country_name (required): The name of the country you are looking for."
)

class Parameters(BaseModel):
    country_name: str
    thought: str
```

### Step 2: Implement your Tool class

All custom BondAI tools must extend from the Tool class and implement the `run` method. In our example tool we will call the RestCountries API to search for countries by name. **Note:** It is very important to validate that any required parameters have been provided. Note the check for `country_name` where an exception is thrown if it has not been provided. This exception message will automatically be provided to the BondAI agent so that it can correct it's mistake.

```python
from bondai.tools import Tool

class QueryCountriesTool(Tool):

    def __init__(self):
        super().__init__(TOOL_NAME, TOOL_DESCRIPTION, parameters=Parameters)

    def run(self, arguments):
        country_name = arguments.get('country_name')

        if country_name is None:
            raise Exception("country_name is required.")
        
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        return parse_countries_info(response.json())
```

### Step 3: Format your response

We will define a function named `parse_countries_info` that takes the JSON object returned from the RestCountries API and turns it into a well formatted string that can be easily understood by the LLM. Note that while the LLM could likely undestand the JSON formatted response, this approach has the advantage of removing unnecessary information which reduces token usage and cost. This also reduces the amount of Agent memory required to store the result which is limited by the LLM's context window. It is highly recommended that tool responses are well formatted (ie markdown) to improve understanding and return only information that is required.


```python
def parse_countries_info(data):
    responses = []

    for country in data:
        country_name = country['name']['common']
        population = country['population']
        language = list(country['languages'].values())[0]
        area = country['area']
        currency = list(country['currencies'].keys())[0]
        region = country['region']
        subregion = country['subregion']
        
        country_info = f"""**{country_name}**
Population: {population}
Language: {language}
Area: {area}
Currency: {currency}
Region: {region}
Subregion: {subregion}\n---\n"""  # Added a separator for readability

        responses.append(country_info)

    return "\n".join(responses)
```


### Putting it all together

Finally, let's put it all together into a single file!

```python
import requests
from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = "query_countries_tool"
TOOL_DESCRIPTION = (
    "This tool allows you to search countries by name and get a list back with information about each country. "
    "The response includes incormation like the country's population size, currencies, languages and more. "
    "\nParameters:\n"
    "- country_name (required): The name of the country you are looking for."
)

class Parameters(BaseModel):
    country_name: str
    thought: str

def parse_countries_info(data):
    responses = []

    for country in data:
        country_name = country['name']['common']
        population = country['population']
        language = list(country['languages'].values())[0]
        area = country['area']
        currency = list(country['currencies'].keys())[0]
        region = country['region']
        subregion = country['subregion']
        
        country_info = f"""**{country_name}**
Population: {population}
Language: {language}
Area: {area}
Currency: {currency}
Region: {region}
Subregion: {subregion}\n---\n"""  # Added a separator for readability

        responses.append(country_info)

    return "\n".join(responses)

class QueryCountriesTool(Tool):

    def __init__(self):
        super().__init__(TOOL_NAME, TOOL_DESCRIPTION, parameters=Parameters)

    def run(self, arguments):
        country_name = arguments.get('country_name')

        if country_name is None:
            raise Exception("country_name is required.")
        
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        return parse_countries_info(response.json())
```