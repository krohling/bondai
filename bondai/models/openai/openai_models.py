from enum import Enum


class OpenAIConnectionType(Enum):
    AZURE: str = "azure"
    OPENAI: str = "openai"


class OpenAIModelType(Enum):
    LLM = "MODEL_TYPE_LLM"
    EMBEDDING = "MODEL_TYPE_EMBEDDING"


class OpenAIModelFamilyType(Enum):
    GPT35 = "MODEL_FAMILY_GPT_35"
    GPT4 = "MODEL_FAMILY_GPT_4"


class OpenAIModelNames(Enum):
    GPT4 = "gpt-4"
    GPT4_0613 = "gpt-4-0613"
    GPT4_32K = "gpt-4-32k"
    GPT4_TURBO_1106 = "gpt-4-1106-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT35_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT35_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT35_TURBO_16K_0613 = "gpt-3.5-turbo-16k-0613"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


ModelConfig = {
    OpenAIModelNames.GPT4.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT4,
        "max_tokens": 8191,
        "input_price_per_token": 0.00003,
        "output_price_per_token": 0.00006,
    },
    OpenAIModelNames.GPT4_0613.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT4,
        "max_tokens": 8191,
        "input_price_per_token": 0.00003,
        "output_price_per_token": 0.00006,
    },
    OpenAIModelNames.GPT4_32K.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT4,
        "max_tokens": 32767,
        "input_price_per_token": 0.00006,
        "output_price_per_token": 0.00012,
    },
    OpenAIModelNames.GPT4_TURBO_1106.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT4,
        "max_tokens": 128000,
        "input_price_per_token": 0.00001,
        "output_price_per_token": 0.00003,
    },
    OpenAIModelNames.GPT35_TURBO.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT35,
        "max_tokens": 4095,
        "input_price_per_token": 0.0000015,
        "output_price_per_token": 0.000002,
    },
    OpenAIModelNames.GPT35_TURBO_16K.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT35,
        "max_tokens": 16383,
        "input_price_per_token": 0.000003,
        "output_price_per_token": 0.000004,
    },
    OpenAIModelNames.GPT35_TURBO_0613.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT35,
        "max_tokens": 4095,
        "input_price_per_token": 0.0000015,
        "output_price_per_token": 0.000002,
    },
    OpenAIModelNames.GPT35_TURBO_16K_0613.value: {
        "model_type": OpenAIModelType.LLM,
        "family": OpenAIModelFamilyType.GPT35,
        "max_tokens": 16383,
        "input_price_per_token": 0.000003,
        "output_price_per_token": 0.000004,
    },
    OpenAIModelNames.TEXT_EMBEDDING_ADA_002.value: {
        "model_type": OpenAIModelType.EMBEDDING,
        "max_tokens": 8190,
        "price_per_token": 0.0000001,
        "embedding_size": 1536,
    },
}
