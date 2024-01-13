---
sidebar_position: 11
---

# Azure OpenAI Services

BondAI has support for Azure OpenAI Services for all GPT-N models, GPT-4 Vision, the Dalle-E text-to-image model as well as the Embeddings API.

## Using Environment Variables

To enable connectivity to Azure OpenAI Services simply specify the following environment variables:

```bash
export OPENAI_CONNECTION_TYPE=azure

export AZURE_OPENAI_GPT35_API_KEY=XXXXXXXXXX
export AZURE_OPENAI_GPT35_API_BASE=XXXXXXXXXX
export AZURE_OPENAI_GPT35_API_VERSION=2023-07-01-preview
export AZURE_OPENAI_GPT35_DEPLOYMENT=XXXXXXXXXX

export AZURE_OPENAI_GPT4_API_KEY=XXXXXXXXXX
export AZURE_OPENAI_GPT4_API_BASE=XXXXXXXXXX
export AZURE_OPENAI_GPT4_API_VERSION=2023-07-01-preview
export AZURE_OPENAI_GPT4_DEPLOYMENT=XXXXXXXXXX

export AZURE_OPENAI_EMBEDDINGS_API_KEY=XXXXXXXXXX
export AZURE_OPENAI_EMBEDDINGS_API_BASE=XXXXXXXXXX
export AZURE_OPENAI_EMBEDDINGS_API_VERSION=2023-07-01-preview
export AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=XXXXXXXXXX

# If you intend to use the DalleTool for text to image generation.
export AZURE_OPENAI_DALLE_API_KEY=XXXXXXXXXX
export AZURE_OPENAI_DALLE_API_BASE=XXXXXXXXXX
export AZURE_OPENAI_DALLE_API_VERSION=2023-06-01-preview
export AZURE_OPENAI_DALLE_DEPLOYMENT=XXXXXXXXXX
```

## In Code

Configure application wide default connection parameters.

```python
from bondai.models.openai import DefaultOpenAIConnectionParams

DefaultOpenAIConnectionParams.configure_azure_connection(
    gpt_4_api_key: '',
    gpt_4_api_version: '',
    gpt_4_azure_endpoint: '',
    gpt_4_azure_deployment: '',
)
```

Configure connection settings for a single Agent.

```python
from bondai.agents import Agent
from bondai.models.openai import (
  OpenAILLM,
  OpenAIConnectionParams, 
  OpenAIConnectionType,
  OpenAIModelNames
)


connection_params = OpenAIConnectionParams(
    connection_type=OpenAIConnectionType.AZURE,
    api_key = '',
    api_version = '',
    azure_endpoint = '',
    azure_deployment = '',
)

llm = OpenAILLM(
  model=OpenAIModelNames.GPT4_32K,
  connection_params=connection_params
)

agent = Agent(llm=llm)
```