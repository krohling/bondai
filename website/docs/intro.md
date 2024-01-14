---
sidebar_position: 1
---

import bondaiLogo from './img/bondai-logo.png'
import googleLogo from './img/google-logo.png'
import alpacaMarketsLogo from './img/alpaca-markets-logo.jpeg'
import postgresLogo from './img/postgres-logo.jpeg'
import blandaiLogo from './img/blandai-logo.jpeg'
import duckduckgoLogo from './img/duckduckgo-logo.png'
import gmailLogo from './img/gmail-logo.png'
import openaiLogo from './img/openai-logo.png'
import azureLogo from './img/azure-logo.png'
import langchainLogo from './img/langchain-logo.jpeg'

# Meet BondAI

<p align="center">
<img src={bondaiLogo} alt="Description or Alt text" style={{borderRadius: "10px", width: "50%"}}  alt="logo" />
</p>

<p align="center">
    <a href="https://opensource.org/licenses/MIT" style={{marginLeft: '10px'}}>
        <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/>
    </a>
    <a href="https://pypi.org/project/bondai/" style={{marginLeft: '10px'}}>
        <img src="https://img.shields.io/pypi/v/bondai" style={{marginLeft: '10px'}} alt="PyPI"/>
    </a>
    <a href="https://colab.research.google.com/drive/1Rmzosq6LD_ZR3MkqQO1M1Af27VAaYNRE?usp=sharing" style={{marginLeft: '10px'}}>
        <img src="https://colab.research.google.com/assets/colab-badge.svg" style={{marginLeft: '10px'}} alt="PyPI"/>
    </a>
</p>
<p align="center"><em>Build highly capable Single and Multi-Agent Systems.</em></p>

## What is BondAI?

BondAI is an open-source tool for developing AI Agent Systems. BondAI handles the implementation complexities including memory/context management, error handling, vector/semantic search and includes a powerful set of out of the box tools and integrations. BondAI's implementation is based on the latest research including support for **[ReAct](https://arxiv.org/abs/2210.03629)**, Multi-Agent and Conversable Agent systems based on the **[AutoGen paper](https://arxiv.org/abs/2308.08155)**, and a Tiered Memory System based on the **[MemGPT paper](https://arxiv.org/abs/2310.08560)**. Additionally, BondAI comes with a CLI interface and a REST/WebSocket Agent Server.


## BondAI Integrations

BondAI comes out of the box with a powerful set of integrations.

|     |  |  |
| -------- | ------- |------- |
| <img src={openaiLogo} alt="openai logo" width="50"/> | **OpenAI**     | BondAI supports any combination of OpenAI models and services including all GPT-N, GPT-4 Vision, Dalle-E 3, and Embeddings.  |
| <img src={azureLogo} alt="azure logo" width="50"/> | **Microsoft Azure**     | BondAI fully supports connectivity to GPT-N, Dalle-E and Embedding APIs through [Microsoft's Azure OpenAI services](https://azure.microsoft.com/en-us/products/ai-services/openai-service).  |
| <img src={googleLogo} alt="google logo" width="50"/>  | **Google Search**    | Allows BondAI to search the internet. [Requires a Google Search API Key and CSE ID](https://developers.google.com/custom-search/v1/introduction) |
| <img src={duckduckgoLogo} alt="duckduckgo logo" width="50"/> | **DuckDuckGo**     | Allows BondAI to search the internet. No API keys required. |
| <img src={alpacaMarketsLogo} alt="alpaca markets logo" width="50"/> | **Alpaca Markets**     | Allows BondAI to buy and sell stocks and crypto. [Requires an Alpaca Markets account.](https://alpaca.markets/)  |
| <img src={postgresLogo} alt="postgres logo" width="75"/>    | **PostgreSQL**    | BondAI can automatically extract the schema from a Postgres DB and process natural language queries. |
| <img src={blandaiLogo} alt="bland.ai logo" width="50"/> | **Bland AI**     | Allows BondAI to make phone calls and process/retrieve call transcripts. [Requires a Bland.ai account.](https://www.bland.ai/)  |
| <img src={gmailLogo} alt="gmail logo" width="50"/> | **Gmail**     | Allows BondAI to search and read emails.  |
| <img src={langchainLogo} alt="langchain logo" width="50"/> | **LangChain**     | Use BondAI's LangChainTool class to import any tool from LangChain into BondAI.  |

