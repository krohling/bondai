OPENAI_CONNECTION_TYPE_AZURE = 'azure'
OPENAI_CONNECTION_TYPE_OPENAI = 'openai'

MODEL_TYPE_LLM = 'MODEL_TYPE_LLM'
MODEL_TYPE_EMBEDDING = 'MODEL_TYPE_EMBEDDING'

MODEL_FAMILY_GPT35 = 'MODEL_FAMILY_GPT_35'
MODEL_FAMILY_GPT4 = 'MODEL_FAMILY_GPT_4'

MODEL_FAMILIES = [
    MODEL_FAMILY_GPT35,
    MODEL_FAMILY_GPT4,
]

MODEL_GPT4 = 'gpt-4'
MODEL_GPT4_0613 = 'gpt-4-0613'
MODEL_GPT4_32K = 'gpt-4-32k'
MODEL_GPT35_TURBO = 'gpt-3.5-turbo'
MODEL_GPT35_TURBO_16K = 'gpt-3.5-turbo-16k'
MODEL_GPT35_TURBO_0613 = 'gpt-3.5-turbo-0613'
MODEL_GPT35_TURBO_16K_0613 = 'gpt-3.5-turbo-16k-0613'
MODEL_TEXT_EMBEDDING_ADA_002 = 'text-embedding-ada-002'

MODEL_NAMES = [
    MODEL_GPT4,
    MODEL_GPT4_0613,
    MODEL_GPT4_32K,
    MODEL_GPT35_TURBO,
    MODEL_GPT35_TURBO_16K,
    MODEL_GPT35_TURBO_0613,
    MODEL_GPT35_TURBO_16K_0613,
    MODEL_TEXT_EMBEDDING_ADA_002,
]

MODELS = {
    MODEL_GPT4: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT4,
        'max_tokens': 8191,
        'input_price_per_token': 0.00003,
        'output_price_per_token': 0.00006,
    },
    MODEL_GPT4_0613: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT4,
        'max_tokens': 8191,
        'input_price_per_token': 0.00003,
        'output_price_per_token': 0.00006,
    },
    MODEL_GPT4_32K: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT4,
        'max_tokens': 32767,
        'input_price_per_token': 0.00006,
        'output_price_per_token': 0.00012,
    },
    MODEL_GPT35_TURBO: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT35,
        'max_tokens': 4095,
        'input_price_per_token': 0.0000015,
        'output_price_per_token': 0.000002,
    },
    MODEL_GPT35_TURBO_16K: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT35,
        'max_tokens': 16383,
        'input_price_per_token': 0.000003,
        'output_price_per_token': 0.000004,
    },
    MODEL_GPT35_TURBO_0613: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT35,
        'max_tokens': 4095,
        'input_price_per_token': 0.0000015,
        'output_price_per_token': 0.000002,
    },
    MODEL_GPT35_TURBO_16K_0613: {
        'model_type': MODEL_TYPE_LLM,
        'family': MODEL_FAMILY_GPT35,
        'max_tokens': 16383,
        'input_price_per_token': 0.000003,
        'output_price_per_token': 0.000004,
    },
    MODEL_TEXT_EMBEDDING_ADA_002: {
        'model_type': MODEL_TYPE_EMBEDDING,
        'max_tokens': 8190,
        'price_per_token': 0.0000001
    },
}