import json

def format_previous_steps(previous_steps):
    str_work = ''
    for i, s in enumerate(previous_steps):
                # print(f"s.function: {s.function}")

                if s.function:
                    function_input = ...
                    try:
                        args = json.loads(s.function['arguments'])
                        function_input = ''
                        for k in args.keys():
                            function_input += f"{k}: {args[k]}\n"

                        # function_input = json.loads(s.function['arguments'])['input']
                    except Exception:
                        pass

                    if function_input:
                        str_work += f"""

## Step {i+1} ##
In Step #{i+1} you used the {s.function['name']} function. You used these parameters:
{function_input}

The following results were returned:
{s.output}
"""
                    else:
                        str_work += f"""
## Step {i+1} ##
In Step #{i+1} you used the {s.function['name']} function. The following results were returned:
{s.output}
"""
                else:
                    str_work += f"""

## Step {i+1} ##
In Step #{i+1} you made a mistake and did not specify a function to use. It is important that you select a function.
"""
    return str_work