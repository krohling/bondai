---
sidebar_position: 8
---

# Get Settings

`GET /settings`

This API returns a list of all OpenAI, Azure, and Tool settings.

**Response Body:**

```json
{
    "openai":[
      {
         "key":"OPENAI_API_KEY",
         "name":"API Key",
         "value":""
      }
   ],
   "azure":[
      {
         "key":"AZURE_OPENAI_EMBEDDINGS_API_KEY",
         "name":"Embeddings API Key",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_EMBEDDINGS_API_BASE",
         "name":"Embeddings API Base",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_EMBEDDINGS_API_VERSION",
         "name":"Embeddings API Version",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT",
         "name":"Embeddings Deployment",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT35_API_KEY",
         "name":"GPT-3.5 API Key",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT35_API_BASE",
         "name":"GPT-3.5 API Base",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT35_API_VERSION",
         "name":"GPT-3.5 API Version",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT35_DEPLOYMENT",
         "name":"GPT-3.5 Deployment",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT4_API_KEY",
         "name":"GPT-4 API Key",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT4_API_BASE",
         "name":"GPT-4 API Base",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT4_API_VERSION",
         "name":"GPT-4 API Version",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_GPT4_DEPLOYMENT",
         "name":"GPT-4 Deployment",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_DALLE_API_KEY",
         "name":"DALL-E API Key",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_DALLE_API_BASE",
         "name":"DALL-E API Base",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_DALLE_API_VERSION",
         "name":"DALL-E API Version",
         "value":""
      },
      {
         "key":"AZURE_OPENAI_DALLE_DEPLOYMENT",
         "name":"DALL-E Deployment",
         "value":""
      }
   ],
   "tools":[
      {
         "name":"Google Search",
         "parameters":[
            {
               "key":"GOOGLE_API_KEY",
               "name":"API Key",
               "value":""
            },
            {
               "key":"GOOGLE_CSE_ID",
               "name":"CSE ID",
               "value":""
            }
         ]
      },
      {
         "name":"Alpaca Markets",
         "parameters":[
            {
               "key":"ALPACA_MARKETS_API_KEY",
               "name":"API Key",
               "value":""
            },
            {
               "key":"ALPACA_MARKETS_SECRET_KEY",
               "name":"Secret Key",
               "value":""
            }
         ]
      },
      {
         "name":"Bland AI",
         "parameters":[
            {
               "key":"BLAND_AI_API_KEY",
               "name":"API Key",
               "value":""
            },
            {
               "key":"BLAND_AI_VOICE_ID",
               "name":"Voice ID",
               "value":""
            },
            {
               "key":"BLAND_AI_CALL_TIMEOUT",
               "name":"Call Timeout",
               "value":""
            }
         ]
      },
      {
         "name":"Postgres Database",
         "parameters":[
            {
               "key":"PG_URI",
               "name":"Postgres URI",
               "value":""
            }
         ]
      }
   ]
}
```