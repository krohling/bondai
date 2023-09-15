#!/usr/bin/env python3

import argparse
import os
import json
from termcolor import cprint, colored
from bondai import Agent, BudgetExceededException
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613, 
    enable_logging,
    OPENAI_CONNECTION_TYPE,
    OPENAI_CONNECTION_TYPE_OPENAI,
)
from bondai.tools import HumanTool
from bondai.prompt import DefaultPromptBuilder
from bondai.util import ModelLogger, load_local_resource
from .default_tools import get_tools
from .onboarding_tool import OnboardingTool

if OPENAI_CONNECTION_TYPE == OPENAI_CONNECTION_TYPE_OPENAI and not os.environ.get('OPENAI_API_KEY'):
    cprint(f"The OPENAI_API_KEY environment variable has not been set. Please input your OpenAI API Key now or type 'exit'.", 'yellow')
    user_input = input()
    if user_input == 'exit':
        exit(1)
    else:
        import openai
        openai.api_key = user_input




cprint(f"Loading BondAI...", 'white')

parser = argparse.ArgumentParser(description="BondAI CLI tool options")

parser.add_argument('--enable-dangerous', 
                    action='store_true', 
                    help='Allows potentially dangerous Tools to be loaded (i.e. ShellTool and PythonREPLTool)')

# --enable-prompt-logging with optional log_dir
parser.add_argument('--enable-prompt-logging', 
                    nargs='?', 
                    const='logs', 
                    metavar='log_dir',
                    help='Turns on prompt logging which will write all prompt inputs into the specified directory. Defaults to "logs" if no directory provided.')

# --load-tools with specified Python file
parser.add_argument('--load-tools', 
                    metavar='my_tools.py', 
                    help='Specify a Python file to load tools from. The file should have a function named get_tools() that returns a list of Tools.')

 # --quiet
parser.add_argument('--quiet', 
                    action='store_true', 
                    default=False,
                    help='If set, minimizes the output to the console.')

args = parser.parse_args()


if args.enable_prompt_logging:
    log_dir = args.enable_prompt_logging
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    enable_logging(ModelLogger(log_dir))
    cprint(f"Prompt logging is enabled. Logs will be written to: {log_dir}", "yellow")

tools = []
if args.load_tools:
    tools_file = args.load_tools
    if os.path.exists(tools_file):
        import importlib.util
        spec = importlib.util.spec_from_file_location("module.name", tools_file)
        tools_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tools_module)
        tools = tools_module.get_tools()  # Assuming get_tools() returns a list of tools
        cprint(f"Loaded tools from {tools_file}", "yellow")
    else:
        cprint(f"Error: {tools_file} does not exist.", "red")
        exit(1)
else:
    tools = get_tools()

if args.enable_dangerous:
    cprint("Dangerous Tools are enabled.", "red")
else:
    tools = [tool for tool in tools if not tool.dangerous]

tool_descriptions = ''.join([f"{tool.name}: {tool.description}\n" for tool in tools])

onboarding_prompt_template = load_local_resource(__file__, 'onboarding_prompt_template.md')
onboarding_prompt_template = onboarding_prompt_template.replace('{TOOLS}', tool_descriptions)

def get_task_definition():
    llm=OpenAILLM(MODEL_GPT4_0613)
    human_tool = HumanTool()
    human_tool.description = (
        "This tool allows you to communicate with the user and ask them questions."
        "To use this tool just put your question in the 'input' parameter."
        "Remember to always be friendly and polite!"
    )

    onboarding_result = Agent(
        llm = llm,
        prompt_builder=DefaultPromptBuilder(llm, onboarding_prompt_template), 
        tools=[
            human_tool,
            OnboardingTool()
        ], 
        quiet=True).run()

    return json.loads(onboarding_result.output)

def run_task(task_config):
    task_description = task_config['task_description']
    task_budget = task_config.get('task_budget')
    tool_descriptions = ', '.join([f"{tool.name}" for tool in tools])

    print(colored("\n\nGetting started on your task.", 'yellow', attrs=["bold"]))
    print(colored("Available tools:", 'white', attrs=["bold"]), colored(tool_descriptions, 'white'))
    print(colored("Description of the task:\n", 'white', attrs=["bold"]), colored(task_description, 'white'))
    if task_budget:
        task_budget = int(task_budget)
        print(colored("Budget:", 'white', attrs=["bold"]), colored(f"${task_budget}", 'white'))
    
    
    agent = Agent(tools=tools, budget=task_budget, quiet=args.quiet, enable_sub_agent=True)
    try:
        result = agent.run(task_description)
        print(colored("\n\nYour task has been completed.", 'yellow'))
        cprint(f"{result.output}\n", 'white')
    except BudgetExceededException as e:
        cprint(f"\n\nThe budget for this task has been exceeded and will stop.\n", 'red')


def run_cli():
    while True:
        task_config = get_task_definition()
        if task_config.get('user_exit'):
            break
        run_task(task_config)
