import os
import json
import time
import openai
import tiktoken
from .openai_models import MODELS, MODEL_TYPE_LLM

TEMPERATURE = 0.1

embedding_tokens = 0
embedding_costs = 0.0
gpt_tokens = 0
gpt_costs = 0.0

logger = None

def enable_logging(model_logger):
    global logger
    logger = model_logger

def disable_logging():
    global logger
    logger = None

def get_gpt_tokens():
    return gpt_tokens

def get_embedding_tokens():
    return embedding_tokens

def get_gpt_costs():
    return gpt_costs

def get_embedding_costs():
    return embedding_costs

def get_total_cost():
    return embedding_costs + gpt_costs

def reset_total_cost():
    global embedding_costs, embedding_tokens, gpt_costs, gpt_tokens
    embedding_costs = 0.0
    embedding_tokens = 0
    gpt_costs = 0.0
    gpt_tokens = 0

def calculate_cost(model_name, usage):
    global embedding_costs, embedding_tokens, gpt_costs, gpt_tokens

    if model_name in MODELS:
        model = MODELS[model_name]
        token_count = usage['total_tokens']

        if model['model_type'] == MODEL_TYPE_LLM:
            gpt_tokens += token_count
            gpt_costs += (usage['prompt_tokens'] * model['input_price_per_token']) + (usage['completion_tokens'] * model['output_price_per_token'])
        else:
            embedding_tokens += token_count
            embedding_costs += token_count * model['price_per_token']
    else:
        print(f"Unknown model: {model_name}")


def get_max_tokens(model):
    return MODELS[model]['max_tokens']


def count_tokens(prompt, model):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt))

def create_embedding(text, model="text-embedding-ada-002"):
    tries = 0
    while True:
        try:
            response = openai.Embedding.create(input=[text], model=model)
            calculate_cost(model, response['usage'])
            return response["data"][0]["embedding"]
        except Exception as e:
            if tries >= 3:
                raise e
            
            print(e)
            time.sleep(5)
            tries += 1

def get_completion(prompt, system_prompt='', previous_messages=[], functions=[], model='gpt-4', connection_params={}):
    global logger
    prompt_log = ''
    messages = []

    if len(functions) > 0:
        fs_str = json.dumps(functions)
        prompt_log += f"TOOLS:\n{fs_str}\n\n"

    if system_prompt:
        prompt_log += f"SYSTEM: {system_prompt}\n\n"
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    if len(previous_messages) > 0:
        prompt_log += "PREVIOUS MESSAGES:\n"
        for m in previous_messages:
            prompt_log += f"{m}\n"
            messages.append({
                "role": "user",
                "content": m
            })
        prompt_log += '\n'

    prompt_log += f"PROMPT: {prompt}\n\n"
    messages.append({
        "role": "user",
        "content": prompt
    })

    attempts = 0
    max_retries = 3
    success = False
    while not success:
        try:
            attempts += 1
            params = { 
                'messages': messages,
                'temperature': TEMPERATURE
            }

            if len(functions) > 0:
                params['functions'] = functions
            if 'engine' not in connection_params:
                params['model'] = model

            response = openai.ChatCompletion.create(
                **params,
                **connection_params
            )
            
            success = True
        except Exception as e:
            time.sleep(15)
            if attempts >= max_retries:
                raise e
    
    calculate_cost(model, response['usage'])
    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function = message["function_call"]
        if logger:
            try:
                logger.log(prompt_log, message["content"], {
                    'name': function['name'],
                    'arguments': json.loads(function['arguments'])
                })
            except json.decoder.JSONDecodeError:
                pass
        
        content = message["content"] if 'content' in message else ''
        return content, function
    else:
        if logger:
            logger.log(prompt_log, message["content"])
        return message["content"], None
