import json
from pydantic import BaseModel
import traceback
from termcolor import colored, cprint
from bondai.tools import Tool, ResponseQueryTool, AgentTool
from bondai.prompt import DefaultPromptBuilder
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613, 
    MODEL_GPT35_TURBO_0613, 
    get_total_cost
)

class FinalAnswerParameters(BaseModel):
    input: str

TOOL_MAX_TOKEN_RESPONSE = 2000
DEFAULT_FINAL_ANSWER_TOOL = Tool('final_answer', "Use the final_answer tool when you have all the information you need to provide the final answer.", FinalAnswerParameters)

def format_print_string(s, length=100):
    # Remove newlines
    s = s.replace('\n', ' ').replace('\r', '')
    
    if len(s) <= length:
        return s
    return s[:length - 3] + "..."

def load_alternative_function(llm, function, options):
    args = {}
    thought = ''
    if 'arguments' in function:
        try:
            args = json.loads(function['arguments'])
            if 'thought' in args:
                thought = "Thought: " + args['thought'] + "\n"
        except:
            pass
    
    function_descriptions = '\n'.join([f"{tool['name']: {tool['description']}}" for tool in options])
    prompt = f"""An AI agent is attempting to use a function that does not exist. Please determine if one of the options provided is a good alternative.
Incorrect Function: {function['name']}
{thought}

VERY IMPORTANT:
- If none of the options is a match simpley return "NO MATCH" as the output.

Options:
id: description
{function_descriptions}
"""
    _, new_function = llm.get_completion(prompt, options)

    result = next((f for f in options if f.name == new_function['name']), None)

    return result


class AgentStep:

    def __init__(self, prompt, message, function=None):
        self.prompt = prompt
        self.message = message
        self.function = function
        self.output = None
        self.error = False
        self.exit = False

class BudgetExceededException(Exception):
    pass

class Agent:

    def __init__(self, prompt_builder=None, tools=[], llm=OpenAILLM(MODEL_GPT4_0613), fallback_llm=OpenAILLM(MODEL_GPT35_TURBO_0613), final_answer_tool=DEFAULT_FINAL_ANSWER_TOOL, budget=None, quiet=False, enable_sub_agent=False):
        if not prompt_builder:
            self.prompt_builder = DefaultPromptBuilder(llm)
        else:
            self.prompt_builder = prompt_builder
        
        if enable_sub_agent:
            tools.append(AgentTool(tools=tools, llm=llm))
        
        self.previous_steps = []
        self.response_query_tool = ResponseQueryTool()
        self.tools = tools
        self.llm = llm
        self.fallback_llm = fallback_llm
        self.final_answer_tool = final_answer_tool
        self.budget = budget
        self.quiet = quiet
    
    def run_once(self, task=''):
        tools = self.tools
        if len(self.response_query_tool.responses) > 0:
            tools.append(self.response_query_tool)

        prompt = self.prompt_builder.build_prompt(task, tools, self.previous_steps)
        functions = list(map(lambda t: t.get_tool_function(), tools))

        message, function = self.llm.get_completion(prompt, '', [], functions)

        if not function:
            message, function = self.fallback_llm.get_completion(message, system_prompt='Select the correct function and parameters to use based on the prompt', previous_messages=[], functions=functions)

        if not function and not self.quiet:
            cprint(f"No function was selected.", 'red')
            cprint(message, 'red')
            
        if function:
            step = AgentStep(prompt, message, function)
            tools = [t for t in self.tools if t.name == function['name']]
            if len(tools) > 0:
                tool = tools[0]
                
                try:
                    args = {}
                    if 'arguments' in function:
                        args = json.loads(function['arguments'])
                    
                    if not self.quiet:
                        cprint(f"\n\nUsing the {tool.name} tool", 'yellow', attrs=["bold"])
                        if len(args) > 0:
                            if 'thought' in args:
                                print(colored("Thought:", 'white', attrs=["bold"]), colored(args['thought'], 'white'))

                            cprint("Arguments", 'white', attrs=["bold"])
                            for key, value in args.items():
                                if key != 'thought':
                                    cprint(f"{key}: {format_print_string(str(value))}", 'white')


                    try:
                        step.output = tool.run(args)
                        step.exit = tool.exit_agent or (self.final_answer_tool and tool.name == self.final_answer_tool.name)
                        
                        if step.output:
                            if self.llm.count_tokens(step.output) > TOOL_MAX_TOKEN_RESPONSE:
                                response_id = self.response_query_tool.add_response(step.output)
                                step.output = f"The result from this tool was greater than {TOOL_MAX_TOKEN_RESPONSE} tokens and could not be displayed. However, you can use the response_query tool to ask questions about the content of this response. Just use response_id = {response_id}."
                        else:
                            step.output = "This command ran successfully with no output."
                        
                        if not self.quiet:
                            print(colored("Output:", 'white', attrs=["bold"]), colored(format_print_string(step.output), 'white'))
                    except Exception as e:
                        # traceback.print_exc()
                        if not self.quiet:
                            cprint(f"An Error occured: {e}", 'red', attrs=["bold"])
                        step.error = True
                        step.output = "An Error occured: " + str(e)
                except Exception as e:
                    if not self.quiet:
                        cprint(f"An Error occured: {e}", 'red', attrs=["bold"])
                    step.error = True
                    step.output = 'An Error occured: The provided arguments were not valid JSON. Valid JSON must ALWAYS BE PROVIDED in the response.'
            else:
                step.error = True
                step.output = f"An Error occured: The function '{function['name']}' does not exist."

                if not self.quiet:
                    cprint(f"No tools found for: {function['name']}", 'red', attrs=["bold"])
                
        else:
            step = AgentStep(prompt, message)
            step.output = "No function was provided."
        
        return step
    
    def reset_memory(self):
        self.previous_steps = []

    def run(self, task=''):
        if self.final_answer_tool:
            self.tools = self.tools + [self.final_answer_tool]

        while True:
            step = self.run_once(task)

            if step.function or len(self.previous_steps) == 0 or self.previous_steps[-1].function:
                self.previous_steps.append(step)
            
            total_cost = get_total_cost()
            if not self.quiet:
                print(colored("Total Cost:", 'green', attrs=["bold"]), colored('$' + str(round(total_cost, 2)), 'white'))

            if step.exit:
                return step

            if self.budget and total_cost >= self.budget:
                raise BudgetExceededException("The budget for this task has been reached without successfully finishing.")


