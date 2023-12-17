import os
from .env_vars import *
from .openai_connection_params import OpenAIConnectionParams, OpenAIConnectionType

gpt_4_connection_params = None
gpt_35_connection_params = None
dalle_connection_params = None
embeddings_connection_params = None


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


def configure_azure_connection(
    gpt_4_api_key: str | None = None,
    gpt_4_api_version: str | None = None,
    gpt_4_azure_endpoint: str | None = None,
    gpt_4_azure_deployment: str | None = None,
    gpt_35_api_key: str | None = None,
    gpt_35_api_version: str | None = None,
    gpt_35_azure_endpoint: str | None = None,
    gpt_35_azure_deployment: str | None = None,
    dalle_api_key: str | None = None,
    dalle_api_version: str | None = None,
    dalle_azure_endpoint: str | None = None,
    dalle_azure_deployment: str | None = None,
    embeddings_api_key: str | None = None,
    embeddings_api_version: str | None = None,
    embeddings_azure_endpoint: str | None = None,
    embeddings_azure_deployment: str | None = None,
):
    global gpt_4_connection_params
    global gpt_35_connection_params
    global dalle_connection_params
    global embeddings_connection_params

    if (
        gpt_4_api_key
        and gpt_4_api_version
        and gpt_4_azure_endpoint
        and gpt_4_azure_deployment
    ):
        gpt_4_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=gpt_4_api_key,
            api_version=gpt_4_api_version,
            azure_endpoint=gpt_4_azure_endpoint,
            azure_deployment=gpt_4_azure_deployment,
        )

    if (
        gpt_35_api_key
        and gpt_35_api_version
        and gpt_35_azure_endpoint
        and gpt_35_azure_deployment
    ):
        gpt_35_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=gpt_35_api_key,
            api_version=gpt_35_api_version,
            azure_endpoint=gpt_35_azure_endpoint,
            azure_deployment=gpt_35_azure_deployment,
        )

    if (
        dalle_api_key
        and dalle_api_version
        and dalle_azure_endpoint
        and dalle_azure_deployment
    ):
        dalle_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=dalle_api_key,
            api_version=dalle_api_version,
            azure_endpoint=dalle_azure_endpoint,
            azure_deployment=dalle_azure_deployment,
        )

    if (
        embeddings_api_key
        and embeddings_api_version
        and embeddings_azure_endpoint
        and embeddings_azure_deployment
    ):
        embeddings_connection_params = OpenAIConnectionParams(
            connection_type=OpenAIConnectionType.AZURE,
            api_key=embeddings_api_key,
            api_version=embeddings_api_version,
            azure_endpoint=embeddings_azure_endpoint,
            azure_deployment=embeddings_azure_deployment,
        )


if os.environ.get(OPENAI_CONNECTION_TYPE_ENV_VAR) == "azure":
    try:
        configure_azure_connection(
            gpt_4_api_key=os.environ.get(AZURE_OPENAI_GPT4_API_KEY_ENV_VAR),
            gpt_4_api_version=os.environ.get(AZURE_OPENAI_GPT4_API_VERSION_ENV_VAR),
            gpt_4_azure_endpoint=os.environ.get(AZURE_OPENAI_GPT4_API_BASE_ENV_VAR),
            gpt_4_azure_deployment=os.environ.get(AZURE_OPENAI_GPT4_DEPLOYMENT_ENV_VAR),
            gpt_35_api_key=os.environ.get(AZURE_OPENAI_GPT35_API_KEY_ENV_VAR),
            gpt_35_api_version=os.environ.get(AZURE_OPENAI_GPT35_API_VERSION_ENV_VAR),
            gpt_35_azure_endpoint=os.environ.get(AZURE_OPENAI_GPT35_API_BASE_ENV_VAR),
            gpt_35_azure_deployment=os.environ.get(
                AZURE_OPENAI_GPT35_DEPLOYMENT_ENV_VAR
            ),
            dalle_api_key=os.environ.get(AZURE_OPENAI_DALLE_API_KEY_ENV_VAR),
            dalle_api_version=os.environ.get(AZURE_OPENAI_DALLE_API_VERSION_ENV_VAR),
            dalle_azure_endpoint=os.environ.get(AZURE_OPENAI_DALLE_API_BASE_ENV_VAR),
            dalle_azure_deployment=os.environ.get(
                AZURE_OPENAI_DALLE_DEPLOYMENT_ENV_VAR
            ),
            embeddings_api_key=os.environ.get(AZURE_OPENAI_EMBEDDINGS_API_KEY_ENV_VAR),
            embeddings_api_version=os.environ.get(
                AZURE_OPENAI_EMBEDDINGS_API_VERSION_ENV_VAR
            ),
            embeddings_azure_endpoint=os.environ.get(
                AZURE_OPENAI_EMBEDDINGS_API_BASE_ENV_VAR
            ),
            embeddings_azure_deployment=os.environ.get(
                AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_ENV_VAR
            ),
        )
    except ValueError:
        pass
else:
    try:
        configure_openai_connection(os.environ.get(OPENAI_API_KEY_ENV_VAR))
    except ValueError:
        pass
