import os
from .openai_models import OPENAI_CONNECTION_TYPE_OPENAI, OPENAI_CONNECTION_TYPE_AZURE

OPENAI_CONNECTION_TYPE = os.environ.get('OPENAI_CONNECTION_TYPE', OPENAI_CONNECTION_TYPE_OPENAI)

# Standard OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
EMBEDDINGS_CONNECTION_PARAMS = { 'api_key': OPENAI_API_KEY }
GPT_35_CONNECTION_PARAMS = { 'api_key': OPENAI_API_KEY }
GPT_4_CONNECTION_PARAMS = { 'api_key': OPENAI_API_KEY }
DALLE_CONNECTION_PARAMS = { 'api_key': OPENAI_API_KEY }

# Azure Embeddings Configuration
AZURE_OPENAI_EMBEDDINGS_API_KEY = os.environ.get('AZURE_OPENAI_EMBEDDINGS_API_KEY')
AZURE_OPENAI_EMBEDDINGS_API_BASE = os.environ.get('AZURE_OPENAI_EMBEDDINGS_API_BASE')
AZURE_OPENAI_EMBEDDINGS_API_VERSION = os.environ.get('AZURE_OPENAI_EMBEDDINGS_API_VERSION')
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT = os.environ.get('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')

# GPT-3.5 Azure Configuration
AZURE_OPENAI_GPT35_API_KEY = os.environ.get('AZURE_OPENAI_GPT35_API_KEY')
AZURE_OPENAI_GPT35_API_BASE = os.environ.get('AZURE_OPENAI_GPT35_API_BASE')
AZURE_OPENAI_GPT35_API_VERSION = os.environ.get('AZURE_OPENAI_GPT35_API_VERSION')
AZURE_OPENAI_GPT35_DEPLOYMENT = os.environ.get('AZURE_OPENAI_GPT35_DEPLOYMENT')

# GPT-4 Azure Configuration
AZURE_OPENAI_GPT4_API_KEY = os.environ.get('AZURE_OPENAI_GPT4_API_KEY')
AZURE_OPENAI_GPT4_API_BASE = os.environ.get('AZURE_OPENAI_GPT4_API_BASE')
AZURE_OPENAI_GPT4_API_VERSION = os.environ.get('AZURE_OPENAI_GPT4_API_VERSION')
AZURE_OPENAI_GPT4_DEPLOYMENT = os.environ.get('AZURE_OPENAI_GPT4_DEPLOYMENT')

AZURE_OPENAI_DALLE_API_KEY = os.environ.get('AZURE_OPENAI_DALLE_API_KEY')
AZURE_OPENAI_DALLE_API_BASE = os.environ.get('AZURE_OPENAI_DALLE_API_BASE')
AZURE_OPENAI_DALLE_API_VERSION = os.environ.get('AZURE_OPENAI_DALLE_API_VERSION')
AZURE_OPENAI_DALLE_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DALLE_DEPLOYMENT')

if OPENAI_CONNECTION_TYPE == OPENAI_CONNECTION_TYPE_AZURE:
    if not AZURE_OPENAI_GPT35_API_KEY:
        raise Exception("AZURE_OPENAI_GPT35_API_KEY is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT35_API_BASE:
        raise Exception("AZURE_OPENAI_GPT35_API_BASE is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT35_API_VERSION:
        raise Exception("AZURE_OPENAI_GPT35_API_VERSION is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT35_DEPLOYMENT:
        raise Exception("AZURE_OPENAI_GPT35_DEPLOYMENT is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT4_API_KEY:
        raise Exception("AZURE_OPENAI_GPT4_API_KEY is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT4_API_BASE:
        raise Exception("AZURE_OPENAI_GPT4_API_BASE is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT4_API_VERSION:
        raise Exception("AZURE_OPENAI_GPT4_API_VERSION is required for 'azure' connection type.")
    if not AZURE_OPENAI_GPT4_DEPLOYMENT:
        raise Exception("AZURE_OPENAI_GPT4_DEPLOYMENT is required for 'azure' connection type.")
    
    EMBEDDINGS_CONNECTION_PARAMS = {
        'api_type': 'azure',
        'api_key': AZURE_OPENAI_EMBEDDINGS_API_KEY,
        'api_base': AZURE_OPENAI_EMBEDDINGS_API_BASE,
        'api_version': AZURE_OPENAI_EMBEDDINGS_API_VERSION,
        'deployment_id': AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT
    }

    GPT_35_CONNECTION_PARAMS = {
        'api_type': 'azure',
        'api_key': AZURE_OPENAI_GPT35_API_KEY,
        'api_base': AZURE_OPENAI_GPT35_API_BASE,
        'api_version': AZURE_OPENAI_GPT35_API_VERSION,
        'engine': AZURE_OPENAI_GPT35_DEPLOYMENT
    }

    GPT_4_CONNECTION_PARAMS = {
        'api_type': 'azure',
        'api_key': AZURE_OPENAI_GPT4_API_KEY,
        'api_base': AZURE_OPENAI_GPT4_API_BASE,
        'api_version': AZURE_OPENAI_GPT4_API_VERSION,
        'engine': AZURE_OPENAI_GPT4_DEPLOYMENT
    }

    DALLE_CONNECTION_PARAMS = {
        'api_type': 'azure',
        'api_key': AZURE_OPENAI_DALLE_API_KEY,
        'api_base': AZURE_OPENAI_DALLE_API_BASE,
        'api_version': AZURE_OPENAI_DALLE_API_VERSION,
        'engine': AZURE_OPENAI_DALLE_DEPLOYMENT
    }