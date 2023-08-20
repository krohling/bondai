from bondai.prompt.steps_formatter import format_previous_steps

QUERY_SYSTEM_PROMPT = "You are a helpful question and answer assistant designed to answer questions about a file. Use the provided information to answer the user's QUESTION at the very end."

def build_prompt(task, steps):
    return f"""

# Task #

This is the task the AI agent is working on:
{task}


# Previous Work #

{steps}


IMPORTANT: You are being asked to analyze the work of an AI agent. 
You must rewrite the  Previous Work section, removing any unnecessary information. 
Try to reduce the amount of text but don't remove too much or the AI agent won't be able to continue working. 
It is VERY important that you make sure the agent still has enough information about each step to continue working.
"""

def compress_steps(task, steps, model):
    formatted_steps = format_previous_steps(steps)
    prompt = build_prompt(task, formatted_steps)
    response = model.get_completion(prompt, QUERY_SYSTEM_PROMPT)[0]
    split = response.split('# Previous Work #')
    
    result = split[1] if len(split) > 1 else split[0]
    return result
