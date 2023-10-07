---
sidebar_position: 8
---

# Azure OpenAI Services

BondAI has support for using Azure OpenAI Services for all GPT-N models, the Dalle-E text-to-image model as well as the Embeddings API. To enable connectivity to Azure OpenAI Services simplify specify the following environment variables:

```
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

# These are only necessary if you intend to use the DalleTool for text to image generation.
export AZURE_OPENAI_DALLE_API_KEY=XXXXXXXXXX
export AZURE_OPENAI_DALLE_API_BASE=XXXXXXXXXX
export AZURE_OPENAI_DALLE_API_VERSION=2023-06-01-preview
export AZURE_OPENAI_DALLE_DEPLOYMENT=XXXXXXXXXX
```
