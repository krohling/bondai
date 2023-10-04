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
    <a href="https://discord.gg/WZEdaZUn" target="_blank">
			<img src="https://img.shields.io/static/v1?label=Join&message=%20discord!&color=mediumslateblue"/>
		</a>
    <a href="https://opensource.org/licenses/MIT" style={{marginLeft: '10px'}}><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/>
    <img src="https://img.shields.io/pypi/v/bondai" style={{marginLeft: '10px'}} alt="PyPI"/>
    </a>
</p>
<p align="center"><em>Meet BondAI, an open source, AI-powered assistant with a lightweight, versatile API for seamless integration into your own applications.</em></p>

## What is BondAI?

BondAI is an open-source framework tailored for integrating and customizing Conversational AI Agents. Built on *OpenAI's function calling support, BondAI handles the implementation complexities involved in creating Autonomous AI Agents, including memory management, error handling, integrated vector/semantic search, a powerful set of out of the box tools, as well as the ability to easily create new, custom tools. Additionally, BondAI includes a CLI interface, enabling anyone with an OpenAI API Key to run a powerful command line agent with a pre-configured set of tools.

## BondAI Integrations

BondAI comes out of the box with a powerful set of integrations.

|     |  |  |
| -------- | ------- |------- |
| <img src={openaiLogo} alt="openai logo" width="50"/> | **OpenAI**     | BondAI supports any combination of OpenAI models and services including GPT-4, GPT-3.5, Dalle-E 3, and Embeddings.  |
| <img src={azureLogo} alt="azure logo" width="50"/> | **Microsoft Azure**     | BondAI fully supports connectivity to GPT-N, Dalle-E and Embedding APIs through [Microsoft's Azure OpenAI services](https://azure.microsoft.com/en-us/products/ai-services/openai-service).  |
| <img src={googleLogo} alt="google logo" width="50"/>  | **Google Search**    | Allows BondAI to search the internet. [Requires a Google Search API Key and CSE ID](https://developers.google.com/custom-search/v1/introduction) |
| <img src={duckduckgoLogo} alt="duckduckgo logo" width="50"/> | **DuckDuckGo**     | Allows BondAI to search the internet. No API keys required. |
| <img src={alpacaMarketsLogo} alt="alpaca markets logo" width="50"/> | **Alpaca Markets**     | Allows BondAI to buy and sell stocks and crypto. [Requires an Alpaca Markets account.](https://alpaca.markets/)  |
| <img src={postgresLogo} alt="postgres logo" width="75"/>    | **PostgreSQL**    | BondAI can automatically extract the schema from a Postgres DB and process natural language queries. |
| <img src={blandaiLogo} alt="bland.ai logo" width="50"/> | **Bland AI**     | Allows BondAI to make phone calls and process/retrieve call transcripts. [Requires a Bland.ai account.](https://www.bland.ai/)  |
| <img src={gmailLogo} alt="gmail logo" width="50"/> | **Gmail**     | Allows BondAI to search and read emails.  |
| <img src={langchainLogo} alt="langchain logo" width="50"/> | **LangChain**     | Use BondAI's LangChainTool class to import any tool from LangChain into BondAI.  |

