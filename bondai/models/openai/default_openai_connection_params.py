import os
from .env_vars import *
from .openai_connection_params import OpenAIConnectionParams, OpenAIConnectionType

gpt_4_connection_params = None
gpt_35_connection_params = None
dalle_connection_params = None
embeddings_connection_params = None

if os.environ.get(OPENAI_CONNECTION_TYPE_ENV_VAR) == "azure":
    try:
        gpt_4_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=os.environ.get(AZURE_OPENAI_GPT4_API_KEY_ENV_VAR),
            api_version=os.environ.get(
                AZURE_OPENAI_GPT4_API_VERSION_ENV_VAR, "2023-07-01-preview"
            ),
            azure_endpoint=os.environ.get(AZURE_OPENAI_GPT4_API_BASE_ENV_VAR),
            azure_deployment=os.environ.get(AZURE_OPENAI_GPT4_DEPLOYMENT_ENV_VAR),
        )
    except ValueError:
        pass

    try:
        gpt_35_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=os.environ.get(AZURE_OPENAI_GPT35_API_KEY_ENV_VAR),
            api_version=os.environ.get(
                AZURE_OPENAI_GPT35_API_VERSION_ENV_VAR, "2023-07-01-preview"
            ),
            azure_endpoint=os.environ.get(AZURE_OPENAI_GPT35_API_BASE_ENV_VAR),
            azure_deployment=os.environ.get(AZURE_OPENAI_GPT35_DEPLOYMENT_ENV_VAR),
        )
    except ValueError:
        pass

    try:
        dalle_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=os.environ.get(AZURE_OPENAI_DALLE_API_KEY_ENV_VAR),
            api_version=os.environ.get(AZURE_OPENAI_DALLE_API_VERSION_ENV_VAR),
            azure_endpoint=os.environ.get(AZURE_OPENAI_DALLE_API_BASE_ENV_VAR),
            azure_deployment=os.environ.get(AZURE_OPENAI_DALLE_DEPLOYMENT_ENV_VAR),
        )
    except ValueError:
        pass

    try:
        embeddings_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=os.environ.get(AZURE_OPENAI_EMBEDDINGS_API_KEY_ENV_VAR),
            api_version=os.environ.get(AZURE_OPENAI_EMBEDDINGS_API_VERSION_ENV_VAR),
            azure_endpoint=os.environ.get(AZURE_OPENAI_EMBEDDINGS_API_BASE_ENV_VAR),
            azure_deployment=os.environ.get(AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_ENV_VAR),
        )
    except ValueError:
        pass
else:
    try:
        gpt_4_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=os.environ.get(OPENAI_API_KEY_ENV_VAR),
        )
    except ValueError:
        pass

    try:
        gpt_35_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=os.environ.get(OPENAI_API_KEY_ENV_VAR),
        )
    except ValueError:
        pass

    try:
        dalle_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=os.environ.get(OPENAI_API_KEY_ENV_VAR),
        )
    except ValueError:
        pass

    try:
        embeddings_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=os.environ.get(OPENAI_API_KEY_ENV_VAR),
        )
    except ValueError:
        pass


def configure_openai_connection(api_key: str):
    global gpt_4_connection_params
    global gpt_35_connection_params
    global dalle_connection_params
    global embeddings_connection_params

    if gpt_4_connection_params:
        gpt_4_connection_params.configure_openai_connection(api_key)
    else:
        gpt_4_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=api_key,
        )

    if gpt_35_connection_params:
        gpt_35_connection_params.configure_openai_connection(api_key)
    else:
        gpt_35_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=api_key,
        )

    if dalle_connection_params:
        dalle_connection_params.configure_openai_connection(api_key)
    else:
        dalle_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=api_key,
        )

    if embeddings_connection_params:
        embeddings_connection_params.configure_openai_connection(api_key)
    else:
        embeddings_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.OPENAI,
            api_key=api_key,
        )
