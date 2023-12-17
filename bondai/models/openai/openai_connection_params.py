from .openai_models import OpenAIConnectionType


class OpenAIConnectionParams:
    def __init__(
        self,
        connection_type: OpenAIConnectionType,
        api_key: str,
        api_version: str | None = None,
        azure_endpoint: str | None = None,
        azure_deployment: str | None = None,
    ):
        if connection_type not in OpenAIConnectionType:
            raise ValueError(f"Invalid api_type: {connection_type}")
        if not api_key:
            raise ValueError(
                f"api_key is required for '{connection_type.value}' connection type."
            )
        if connection_type == OpenAIConnectionType.AZURE:
            if not api_version:
                raise ValueError("api_version is required for 'azure' connection type.")
            if not azure_endpoint:
                raise ValueError(
                    "azure_endpoint is required for 'azure' connection type."
                )
            if not azure_deployment:
                raise ValueError(
                    "azure_deployment is required for 'azure' connection type."
                )

        self._connection_type = connection_type
        self._api_key = api_key
        self._api_version = api_version
        self._azure_endpoint = azure_endpoint
        self._azure_deployment = azure_deployment

    @property
    def connection_type(self):
        return self._connection_type

    @property
    def api_key(self):
        return self._api_key

    @property
    def api_version(self):
        return self._api_version

    @property
    def azure_endpoint(self):
        return self._azure_endpoint

    @property
    def azure_deployment(self):
        return self._azure_deployment

    def configure_openai_connection(self, api_key: str):
        if not api_key:
            raise ValueError("api_key is required for 'openai' connection type.")
        self._connection_type = OpenAIConnectionType.OPENAI
        self._api_key = api_key
        self._api_version = None
        self._azure_endpoint = None
        self._azure_deployment = None

    def configure_azure_connection(
        self, api_key: str, api_version: str, azure_endpoint: str, azure_deployment: str
    ):
        if not api_key:
            raise ValueError("api_key is required for 'azure' connection type.")
        if not api_version:
            raise ValueError("api_version is required for 'azure' connection type.")
        if not azure_endpoint:
            raise ValueError("azure_endpoint is required for 'azure' connection type.")
        if not azure_deployment:
            raise ValueError(
                "azure_deployment is required for 'azure' connection type."
            )

        self._connection_type = OpenAIConnectionType.AZURE
        self._api_key = api_key
        self._api_version = api_version
        self._azure_endpoint = azure_endpoint
        self._azure_deployment = azure_deployment

    def to_dict(self):
        return {
            "api_key": self._api_key,
            "api_version": self._api_version,
            "azure_endpoint": self._azure_endpoint,
            "azure_deployment": self._azure_deployment,
        }
