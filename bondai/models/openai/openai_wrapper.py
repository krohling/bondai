import json
import tiktoken
from typing import Dict, List, Callable
from openai import OpenAI, AzureOpenAI
from .openai_models import ModelConfig, OpenAIModelType, OpenAIConnectionType
from bondai.util import ModelLogger

DEFAULT_TEMPERATURE = 0.1

embedding_tokens = 0
embedding_costs = 0.0
gpt_tokens = 0
gpt_costs = 0.0

logger = None


def enable_logging(model_logger: ModelLogger):
    global logger
    logger = model_logger


def disable_logging():
    global logger
    logger = None


def get_gpt_tokens() -> int:
    return gpt_tokens


def get_embedding_tokens() -> int:
    return embedding_tokens


def get_gpt_costs() -> float:
    return gpt_costs


def get_embedding_costs() -> float:
    return embedding_costs


def get_total_cost() -> float:
    return embedding_costs + gpt_costs


def reset_total_cost():
    global embedding_costs, embedding_tokens, gpt_costs, gpt_tokens
    embedding_costs = 0.0
    embedding_tokens = 0
    gpt_costs = 0.0
    gpt_tokens = 0


def calculate_cost(model_name: str, usage: Dict):
    global embedding_costs, embedding_tokens, gpt_costs, gpt_tokens

    if model_name in ModelConfig:
        model = ModelConfig[model_name]
        token_count = usage["total_tokens"]

        if model["model_type"] == OpenAIModelType.LLM:
            gpt_tokens += token_count
            gpt_costs += (usage["prompt_tokens"] * model["input_price_per_token"]) + (
                usage["completion_tokens"] * model["output_price_per_token"]
            )
        else:
            embedding_tokens += token_count
            embedding_costs += token_count * model["price_per_token"]
    else:
        print(f"Unknown model: {model_name}")


def get_max_tokens(model: str) -> int:
    return ModelConfig[model]["max_tokens"]


def count_tokens(prompt: str, model: Dict) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt))


def create_embedding(
    text: str,
    model: str = "text-embedding-ada-002",
    connection_params: Dict = {},
    **kwargs,
) -> [float]:
    params = {
        "input": text if isinstance(text, list) else [text],
    }

    if connection_params.get("api_type", "") == OpenAIConnectionType.AZURE.value:
        client = AzureOpenAI(
            api_key=connection_params["api_key"],
            api_version=connection_params["api_version"],
            azure_endpoint=connection_params["azure_endpoint"],
        )
        params["model"] = connection_params["azure_deployment"]
    else:
        client = OpenAI(**connection_params)
        params["model"] = model

    response = client.embeddings.create(**params, **kwargs)

    calculate_cost(
        model,
        {
            "total_tokens": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.total_tokens
            - response.usage.prompt_tokens,
        },
    )

    embeddings = [d.embedding for d in response.data]

    if len(embeddings) > 0:
        return embeddings
    else:
        return embeddings[0]


def get_completion(
    messages: List[Dict] | None = None,
    functions: List[Dict] | None = None,
    model: str = "gpt-4",
    connection_params: Dict | None = None,
    **kwargs,
) -> (str, Dict | None):
    if messages is None:
        messages = []
    if functions is None:
        functions = []
    if connection_params is None:
        connection_params = {}

    response = _get_completion(
        messages=messages,
        functions=functions,
        model=model,
        connection_params=connection_params,
        **kwargs,
    )

    function = None
    message = response.choices[0].message
    if message.function_call:
        function = {"name": message.function_call.name}
        if message.function_call.arguments:
            try:
                function["arguments"] = json.loads(message.function_call.arguments)
            except json.decoder.JSONDecodeError:
                pass

    calculate_cost(
        model,
        {
            "total_tokens": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.total_tokens
            - response.usage.prompt_tokens,
        },
    )
    _log_completion(
        messages,
        functions=functions,
        response_content=message.content,
        response_function=function,
    )

    return message.content, function


def get_streaming_completion(
    messages: List[Dict] | None = None,
    functions: List[Dict] | None = None,
    model: str = "gpt-4",
    connection_params: Dict | None = None,
    content_stream_callback: Callable[[str], None] | None = None,
    function_stream_callback: Callable[[str], None] | None = None,
    **kwargs,
) -> (str, Dict | None):
    if messages is None:
        messages = []
    if functions is None:
        functions = []
    if connection_params is None:
        connection_params = {}

    response = _get_completion(
        messages,
        functions=functions,
        model=model,
        connection_params=connection_params,
        stream=True,
        **kwargs,
    )

    content = ""
    function_name = ""
    function_arguments = ""

    for chunk in response:
        if len(chunk.choices) == 0:
            continue

        delta = chunk.choices[0].delta
        if delta.content:
            content += delta.content
            if content_stream_callback:
                content_stream_callback(delta.content)

        function_call = delta.function_call
        if function_call:
            if function_call.name:
                function_name += function_call.name
            if function_call.arguments:
                function_arguments += function_call.arguments
            if function_stream_callback:
                function_stream_callback(function_name, function_arguments)

    function = None
    if function_name:
        function = {"name": function_name}
        if function_arguments:
            try:
                function["arguments"] = json.loads(function_arguments)
            except json.decoder.JSONDecodeError:
                pass

    if function:
        completion_tokens = content + json.dumps(function)
    else:
        completion_tokens = content

    completion_token_count = count_tokens(completion_tokens, model)
    prompt_tokens = json.dumps(messages)
    prompt_token_count = count_tokens(prompt_tokens, model)

    calculate_cost(
        model,
        {
            "total_tokens": prompt_token_count + completion_token_count,
            "prompt_tokens": prompt_token_count,
            "completion_tokens": completion_token_count,
        },
    )

    _log_completion(
        messages,
        functions=functions,
        response_content=content,
        response_function=function,
    )

    return content, function


def _log_completion(
    messages: List[Dict] | None = None,
    functions: List[Dict] | None = None,
    response_content: str | None = None,
    response_function: Dict | None = None,
):
    if messages is None:
        messages = []
    if functions is None:
        functions = []
    if response_content is None:
        response_content = ""

    global logger
    if not logger:
        return
    prompt_log = ""

    if len(functions) > 0:
        fs_str = json.dumps(functions)
        prompt_log += f"TOOLS:\n{fs_str}\n\n"

    if len(messages) > 0:
        m_str = json.dumps(messages)
        prompt_log += f"MESSAGES:\n{m_str}\n\n"

    logger.log(prompt_log, response_content, function=response_function)


def _get_completion(
    messages: List[Dict] | None = None,
    functions: List[Dict] | None = None,
    model: str = "gpt-4",
    connection_params: Dict | None = None,
    **kwargs,
) -> (str, Dict | None):
    if messages is None:
        messages = []
    if functions is None:
        functions = []
    if connection_params is None:
        connection_params = {}

    params = {
        "messages": messages,
        "temperature": DEFAULT_TEMPERATURE,
    }

    if connection_params.get("api_type", "") == OpenAIConnectionType.AZURE.value:
        client = AzureOpenAI(
            api_key=connection_params["api_key"],
            api_version=connection_params["api_version"],
            azure_endpoint=connection_params["azure_endpoint"],
            azure_deployment=connection_params["azure_deployment"],
        )
        params["model"] = connection_params["azure_deployment"]
    else:
        client = OpenAI(**connection_params)
        params["model"] = model

    if len(functions) > 0:
        params["functions"] = functions

    return client.chat.completions.create(**params, **kwargs)
