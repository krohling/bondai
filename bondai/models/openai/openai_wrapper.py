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

def create_embedding(text, model="text-embedding-ada-002", connection_params={}):
    tries = 0
    while True:
        try:
            params = {
                'input': text if isinstance(text, list) else [text],
            }
            if 'deployment_id' not in connection_params:
                params['model'] = model

            response = openai.Embedding.create(
                **params,
                **connection_params
            )

            calculate_cost(model, response['usage'])

            embeddings = [d['embedding'] for d in response['data']]
            if len(embeddings) > 0:
                return embeddings
            else:
                return embeddings[0]

        except Exception as e:
            if tries >= 3:
                raise e
            
            print(e)
            time.sleep(5)
            tries += 1

def get_completion(
    prompt, 
    system_prompt='', 
    previous_messages=[], 
    functions=[], 
    model='gpt-4', 
    connection_params={}
):
    messages = __build_completion_messages(prompt, system_prompt=system_prompt, previous_messages=previous_messages)
    response = __get_completion(messages=messages, functions=functions, model=model, connection_params=connection_params)

    function = None
    message = response["choices"][0]["message"]
    content = message.get('content')
    if message.get("function_call"):
        function = {
            'name': message["function_call"]['name']
        }
        if 'arguments' in message["function_call"]:
            try:
                function['arguments'] = json.loads(message["function_call"]['arguments'])
            except json.decoder.JSONDecodeError:
                pass
    
    calculate_cost(model, response['usage'])
    __log_completion(
        prompt,
        system_prompt=system_prompt, 
        previous_messages=previous_messages, 
        functions=functions,
        response_content=content
    )

    return content, function


def get_streaming_completion(
    prompt, 
    system_prompt='', 
    previous_messages=[], 
    functions=[], 
    model='gpt-4', 
    connection_params={},
    content_stream_callback=None, 
    function_stream_callback=None
):
    connection_params['stream'] = True
    messages = __build_completion_messages(prompt, system_prompt=system_prompt, previous_messages=previous_messages)
    response = __get_completion(messages, functions=functions, model=model, connection_params=connection_params)

    content = ''
    function_name = ''
    function_arguments = ''

    for chunk in response:
        if len(chunk['choices']) == 0:
            continue
        
        choice = chunk['choices'][0]
        delta = choice.get('delta', {})
        
        if delta.get('content'):
            content += delta['content']
            if content_stream_callback:
                content_stream_callback(delta['content'])
        
        function_call = delta.get('function_call')
        if function_call:
            if function_call.get('name'):
                function_name += function_call['name']
            if function_call.get('arguments'):
                function_arguments += function_call['arguments']
            if function_stream_callback:
                function_stream_callback(function_name, function_arguments)

    function = None
    if function_name:
        function = { 'name': function_name }
        if function_arguments:
            try:
                function['arguments'] = json.loads(function_arguments)
            except json.decoder.JSONDecodeError:
                pass

    if function:
        completion_tokens = content + json.dumps(function)
    else:
        completion_tokens = content
    
    completion_token_count = count_tokens(completion_tokens, model)
    prompt_tokens = json.dumps(messages)
    prompt_token_count = count_tokens(prompt_tokens, model)
    
    calculate_cost(model, {
        'total_tokens': prompt_token_count + completion_token_count,
        'prompt_tokens': prompt_token_count,
        'completion_tokens': completion_token_count
    })

    __log_completion(
        prompt,
        system_prompt=system_prompt, 
        previous_messages=previous_messages, 
        functions=functions,
        response_content=content
    )

    return content, function


def __build_completion_messages(prompt, system_prompt='', previous_messages=[]):
    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    if len(previous_messages) > 0:
        for m in previous_messages:
            messages.append({
                "role": "user",
                "content": m['prompt']
            })
            messages.append({
                "role": "assistant",
                "content": m['response']
            })

    messages.append({
        "role": "user",
        "content": prompt
    })

    return messages

def __log_completion(prompt, system_prompt='', previous_messages=[], functions=[], response_content='', response_function=None):
    global logger
    if not logger:
        return
    prompt_log = ''

    if len(functions) > 0:
        fs_str = json.dumps(functions)
        prompt_log += f"TOOLS:\n{fs_str}\n\n"

    if system_prompt:
        prompt_log += f"SYSTEM: {system_prompt}\n\n"
    
    if len(previous_messages) > 0:
        prompt_log += "PREVIOUS MESSAGES:\n"
        for m in previous_messages:
            prompt_log += f"{m}\n"
        prompt_log += '\n'

    prompt_log += f"PROMPT: {prompt}\n\n"
    logger.log(prompt_log, response_content, function=response_function)


def __get_completion(
    messages,
    functions=None, 
    model='gpt-4', 
    connection_params={}
):
    attempts = 0
    max_retries = 3
    while True:
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

            return openai.ChatCompletion.create(
                **params,
                **connection_params
            )
        except Exception as e:
            time.sleep(15)
            if attempts >= max_retries:
                raise e
