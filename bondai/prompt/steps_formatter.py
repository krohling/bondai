import json

def format_step(step, count):
    str_work = ''
    if step.function:
        args = {}
        if step.function and 'arguments' in step.function:
            if isinstance(step.function['arguments'], str):
                try:
                    args = json.loads(step.function['arguments'])
                except Exception:
                    pass
            elif isinstance(step.function['arguments'], dict):
                args = step.function['arguments']
        
        function_input = ''
        for k in args.keys():
            function_input += f"{k}: {args[k]}\n"

        if function_input:
            str_work += f"""

## Step {count} ##
In Step #{count} you used the {step.function['name']} function. You used these parameters:
{function_input}

The following results were returned:
{step.output}
"""
        else:
            str_work += f"""
## Step {count} ##
In Step #{count} you used the {step.function['name']} function. The following results were returned:
{step.output}
"""
    else:
        str_work += f"""

## Step {count} ##
In Step #{count} you made a mistake and did not specify a function to use. It is important that you select a function.
"""

    return str_work

def format_previous_steps(model, previous_steps, max_tokens=None):
    str_work = ''
    retained_steps = []

    for i,s in enumerate(reversed(previous_steps)):
        step_num = len(previous_steps)-i
        str_step = format_step(s, step_num)
        if not max_tokens or model.count_tokens(str_work + str_step) <= max_tokens:
            str_work += str_step
            retained_steps.append([step_num,s])
        else:
            break

    str_work = ''
    for s in reversed(retained_steps):
        str_step = format_step(s[1], s[0])
        str_work += str_step

    return str_work