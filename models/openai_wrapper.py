import json
import time
import openai
import tiktoken

def count_tokens(prompt, model='gpt-4'):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt))

def create_embedding(text, model="text-embedding-ada-002"):
    max_tries = 3
    tries = 0
    while True:
        try:
            return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]
        except Exception as e:
            if tries >= 3:
                raise e
            
            print(e)
            time.sleep(5)
            tries += 1

def get_completion(prompt, system_prompt='', previous_messages=[], functions=[], model='gpt-4'):
    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    for m in previous_messages:
        messages.append({
            "role": "user",
            "content": m
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    # write prompt to a file named 
    # with open('prompt.md', 'w') as f:
    #     f.write(prompt)

    attempts = 0
    max_retries = 3
    success = False
    while not success:
        try:
            attempts += 1
            if len(functions) > 0:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    functions=functions,
                    temperature=0,
                )
            else:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                )
            
            success = True
        except Exception as e:
            time.sleep(15)
            if attempts >= max_retries:
                raise e
    
    message = response["choices"][0]["message"]

    if message.get("function_call"):
        return message["content"], message["function_call"]
    else:
        return message["content"], None
