import json

def format_step(step, count):
    str_work = ''
    if step.function:
        function_input = ...
        try:
            args = json.loads(step.function['arguments'])
            function_input = ''
            for k in args.keys():
                function_input += f"{k}: {args[k]}\n"
        except Exception:
            pass

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
    for i, s in enumerate(previous_steps):
        str_step = format_step(s, i+1)
        if not max_tokens or model.count_tokens(str_work + str_step) <= max_tokens:
            str_work += str_step
        else:
            break
    return str_work