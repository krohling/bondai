import os
from .env_vars import *
from .openai_models import OpenAIConnectionType

OPENAI_CONNECTION_TYPE = (
    OpenAIConnectionType.AZURE
    if os.environ.get(OPENAI_CONNECTION_TYPE_ENV_VAR) == "azure"
    else OpenAIConnectionType.OPENAI
)

# Standard OpenAI Configuration
OPENAI_API_KEY = os.environ.get(OPENAI_API_KEY_ENV_VAR)
EMBEDDINGS_CONNECTION_PARAMS = {"api_key": OPENAI_API_KEY}
GPT_35_CONNECTION_PARAMS = {"api_key": OPENAI_API_KEY}
GPT_4_CONNECTION_PARAMS = {"api_key": OPENAI_API_KEY}
DALLE_CONNECTION_PARAMS = {"api_key": OPENAI_API_KEY}

# Azure Embeddings Configuration
AZURE_OPENAI_EMBEDDINGS_API_KEY = os.environ.get(
    AZURE_OPENAI_EMBEDDINGS_API_KEY_ENV_VAR
)
AZURE_OPENAI_EMBEDDINGS_API_BASE = os.environ.get(
    AZURE_OPENAI_EMBEDDINGS_API_BASE_ENV_VAR
)
AZURE_OPENAI_EMBEDDINGS_API_VERSION = os.environ.get(
    AZURE_OPENAI_EMBEDDINGS_API_VERSION_ENV_VAR
)
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT = os.environ.get(
    AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_ENV_VAR
)

# GPT-3.5 Azure Configuration
AZURE_OPENAI_GPT35_API_KEY = os.environ.get(AZURE_OPENAI_GPT35_API_KEY_ENV_VAR)
AZURE_OPENAI_GPT35_API_BASE = os.environ.get(AZURE_OPENAI_GPT35_API_BASE_ENV_VAR)
AZURE_OPENAI_GPT35_API_VERSION = os.environ.get(
    AZURE_OPENAI_GPT35_API_VERSION_ENV_VAR, "2023-07-01-preview"
)
AZURE_OPENAI_GPT35_DEPLOYMENT = os.environ.get(AZURE_OPENAI_GPT35_DEPLOYMENT_ENV_VAR)

# GPT-4 Azure Configuration
AZURE_OPENAI_GPT4_API_KEY = os.environ.get(AZURE_OPENAI_GPT4_API_KEY_ENV_VAR)
AZURE_OPENAI_GPT4_API_BASE = os.environ.get(AZURE_OPENAI_GPT4_API_BASE_ENV_VAR)
AZURE_OPENAI_GPT4_API_VERSION = os.environ.get(
    AZURE_OPENAI_GPT4_API_VERSION_ENV_VAR, "2023-07-01-preview"
)
AZURE_OPENAI_GPT4_DEPLOYMENT = os.environ.get(AZURE_OPENAI_GPT4_DEPLOYMENT_ENV_VAR)

AZURE_OPENAI_DALLE_API_KEY = os.environ.get(AZURE_OPENAI_DALLE_API_KEY_ENV_VAR)
AZURE_OPENAI_DALLE_API_BASE = os.environ.get(AZURE_OPENAI_DALLE_API_BASE_ENV_VAR)
AZURE_OPENAI_DALLE_API_VERSION = os.environ.get(AZURE_OPENAI_DALLE_API_VERSION_ENV_VAR)
AZURE_OPENAI_DALLE_DEPLOYMENT = os.environ.get(AZURE_OPENAI_DALLE_DEPLOYMENT_ENV_VAR)

if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.AZURE:
    if not AZURE_OPENAI_GPT35_API_KEY:
        raise Exception(
            "AZURE_OPENAI_GPT35_API_KEY is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT35_API_BASE:
        raise Exception(
            "AZURE_OPENAI_GPT35_API_BASE is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT35_API_VERSION:
        raise Exception(
            "AZURE_OPENAI_GPT35_API_VERSION is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT35_DEPLOYMENT:
        raise Exception(
            "AZURE_OPENAI_GPT35_DEPLOYMENT is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT4_API_KEY:
        raise Exception(
            "AZURE_OPENAI_GPT4_API_KEY is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT4_API_BASE:
        raise Exception(
            "AZURE_OPENAI_GPT4_API_BASE is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT4_API_VERSION:
        raise Exception(
            "AZURE_OPENAI_GPT4_API_VERSION is required for 'azure' connection type."
        )
    if not AZURE_OPENAI_GPT4_DEPLOYMENT:
        raise Exception(
            "AZURE_OPENAI_GPT4_DEPLOYMENT is required for 'azure' connection type."
        )

    EMBEDDINGS_CONNECTION_PARAMS = {
        "api_type": "azure",
        "api_key": AZURE_OPENAI_EMBEDDINGS_API_KEY,
        "api_version": AZURE_OPENAI_EMBEDDINGS_API_VERSION,
        "azure_endpoint": AZURE_OPENAI_EMBEDDINGS_API_BASE,
        "azure_deployment": AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT,
    }

    GPT_35_CONNECTION_PARAMS = {
        "api_type": "azure",
        "api_key": AZURE_OPENAI_GPT35_API_KEY,
        "api_version": AZURE_OPENAI_GPT35_API_VERSION,
        "azure_endpoint": AZURE_OPENAI_GPT35_API_BASE,
        "azure_deployment": AZURE_OPENAI_GPT35_DEPLOYMENT,
    }

    GPT_4_CONNECTION_PARAMS = {
        "api_type": "azure",
        "api_key": AZURE_OPENAI_GPT4_API_KEY,
        "api_version": AZURE_OPENAI_GPT4_API_VERSION,
        "azure_endpoint": AZURE_OPENAI_GPT4_API_BASE,
        "azure_deployment": AZURE_OPENAI_GPT4_DEPLOYMENT,
    }

    DALLE_CONNECTION_PARAMS = {
        "api_type": "azure",
        "api_key": AZURE_OPENAI_DALLE_API_KEY,
        "api_version": AZURE_OPENAI_DALLE_API_VERSION,
        "azure_endpoint": AZURE_OPENAI_DALLE_API_BASE,
        "azure_deployment": AZURE_OPENAI_DALLE_DEPLOYMENT,
    }
