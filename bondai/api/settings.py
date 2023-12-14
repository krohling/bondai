import os
from itertools import chain
from flask import request, jsonify
from flask_restful import Resource
from bondai.models.openai.env_vars import *
from bondai.tools.search.google_search import (
    GOOGLE_API_KEY_ENV_VAR,
    GOOGLE_CSE_ID_ENV_VAR,
)
from bondai.tools.alpaca_markets import (
    ALPACA_MARKETS_API_KEY_ENV_VAR,
    ALPACA_MARKETS_SECRET_KEY_ENV_VAR,
)
from bondai.tools.bland_ai import (
    BLAND_AI_API_KEY_ENV_VAR,
    BLAND_AI_VOICE_ID_ENV_VAR,
    BLAND_AI_CALL_TIMEOUT_ENV_VAR,
)
from bondai.tools.database import PG_URI_ENV_VAR

SETTINGS_OPTIONS = {
    "openai": [
        {
            "name": "API Key",
            "key": OPENAI_API_KEY_ENV_VAR,
        }
    ],
    "azure": [
        {
            "name": "Embeddings API Key",
            "key": AZURE_OPENAI_EMBEDDINGS_API_KEY_ENV_VAR,
        },
        {
            "name": "Embeddings API Base",
            "key": AZURE_OPENAI_EMBEDDINGS_API_BASE_ENV_VAR,
        },
        {
            "name": "Embeddings API Version",
            "key": AZURE_OPENAI_EMBEDDINGS_API_VERSION_ENV_VAR,
        },
        {
            "name": "Embeddings Deployment",
            "key": AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_ENV_VAR,
        },
        {
            "name": "GPT-3.5 API Key",
            "key": AZURE_OPENAI_GPT35_API_KEY_ENV_VAR,
        },
        {
            "name": "GPT-3.5 API Base",
            "key": AZURE_OPENAI_GPT35_API_BASE_ENV_VAR,
        },
        {
            "name": "GPT-3.5 API Version",
            "key": AZURE_OPENAI_GPT35_API_VERSION_ENV_VAR,
        },
        {
            "name": "GPT-3.5 Deployment",
            "key": AZURE_OPENAI_GPT35_DEPLOYMENT_ENV_VAR,
        },
        {
            "name": "GPT-4 API Key",
            "key": AZURE_OPENAI_GPT4_API_KEY_ENV_VAR,
        },
        {
            "name": "GPT-4 API Base",
            "key": AZURE_OPENAI_GPT4_API_BASE_ENV_VAR,
        },
        {
            "name": "GPT-4 API Version",
            "key": AZURE_OPENAI_GPT4_API_VERSION_ENV_VAR,
        },
        {
            "name": "GPT-4 Deployment",
            "key": AZURE_OPENAI_GPT4_DEPLOYMENT_ENV_VAR,
        },
        {
            "name": "DALL-E API Key",
            "key": AZURE_OPENAI_DALLE_API_KEY_ENV_VAR,
        },
        {
            "name": "DALL-E API Base",
            "key": AZURE_OPENAI_DALLE_API_BASE_ENV_VAR,
        },
        {
            "name": "DALL-E API Version",
            "key": AZURE_OPENAI_DALLE_API_VERSION_ENV_VAR,
        },
        {
            "name": "DALL-E Deployment",
            "key": AZURE_OPENAI_DALLE_DEPLOYMENT_ENV_VAR,
        },
    ],
    "tools": [
        {
            "name": "Google Search",
            "parameters": [
                {
                    "name": "API Key",
                    "key": GOOGLE_API_KEY_ENV_VAR,
                },
                {
                    "name": "CSE ID",
                    "key": GOOGLE_CSE_ID_ENV_VAR,
                },
            ],
        },
        {
            "name": "Alpaca Markets",
            "parameters": [
                {
                    "name": "API Key",
                    "key": ALPACA_MARKETS_API_KEY_ENV_VAR,
                },
                {
                    "name": "Secret Key",
                    "key": ALPACA_MARKETS_SECRET_KEY_ENV_VAR,
                },
            ],
        },
        {
            "name": "Bland AI",
            "parameters": [
                {
                    "name": "API Key",
                    "key": BLAND_AI_API_KEY_ENV_VAR,
                },
                {
                    "name": "Voice ID",
                    "key": BLAND_AI_VOICE_ID_ENV_VAR,
                },
                {
                    "name": "Call Timeout",
                    "key": BLAND_AI_CALL_TIMEOUT_ENV_VAR,
                },
            ],
        },
        {
            "name": "Postgres Database",
            "parameters": [
                {
                    "name": "Postgres URI",
                    "key": PG_URI_ENV_VAR,
                }
            ],
        },
    ],
}


def get_settings():
    settings = SETTINGS_OPTIONS.copy()

    for parameter in settings["openai"]:
        parameter["value"] = os.getenv(parameter["key"], "")

    for parameter in settings["azure"]:
        parameter["value"] = os.getenv(parameter["key"], "")

    for tool in settings["tools"]:
        for parameter in tool["parameters"]:
            parameter["value"] = os.getenv(parameter["key"], "")

    return settings


def set_settings(settings):
    if "openai" in settings:
        tool_keys = [p["key"] for p in SETTINGS_OPTIONS["openai"]]
        for parameter in settings["openai"]:
            key = parameter["key"]
            if key in tool_keys:
                os.environ[key] = parameter["value"]

    if "azure" in settings:
        tool_keys = [p["key"] for p in SETTINGS_OPTIONS["azure"]]
        for parameter in settings["azure"]:
            key = parameter["key"]
            if key in tool_keys:
                os.environ[key] = parameter["value"]

    if "tools" in settings:
        tool_params = [t["parameters"] for t in SETTINGS_OPTIONS["tools"]]
        tool_params = list(chain(*tool_params))
        tool_keys = [p["key"] for p in tool_params]

        for param in settings["tools"]:
            key = param["key"]
            if key in tool_keys:
                os.environ[key] = param["value"]


class SettingsResource(Resource):
    def get(self):
        return jsonify(get_settings())

    def post(self):
        data = request.get_json()
        set_settings(data)
        return jsonify({"status": "success"})
