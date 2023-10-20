# Bondai UI 

## Prereqisites

**Docker**

It is highly recommended that you run **BondAI** from within a Docker container if you are going to use tools with file system access.

https://www.docker.com/products/docker-desktop/


**OpenAi Account**

At this time, Bondai is configured with OpenAI LLM (GPT-3.5-Turbo, GPT-4). If you don't have an API Key, you can sign up here: https://platform.openai.com/

> Costs may vary depending on usage: https://openai.com/pricing

## Production Version

If you don't plan on making any changes to the source code, run the production version for speed.

From the UI root run:

`docker-compose -f docker-compose.yml up`

## Development Version

From the UI root run:

`docker-compose -f docker-compose-dev.yml up`

## Credit

Bondai UI is based on the Next.js AI chatbot built by Vercel Labs

https://github.com/vercel-labs/ai-chatbot

https://chat.vercel.ai