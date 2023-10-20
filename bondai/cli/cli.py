#!/usr/bin/env python3

import argparse
import os
import json
from termcolor import cprint
from bondai import Agent, BudgetExceededException
from bondai.tools import Tool, HumanTool
from bondai.util import ModelLogger
from bondai.api import BondAIAPIServer
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613, 
    enable_logging,
    OPENAI_CONNECTION_TYPE,
    OPENAI_CONNECTION_TYPE_OPENAI,
)
from .default_tools import get_tools
from .task_agent_tool import TaskAgentTool
from .conversational_agent_prompt_builder import ConversationalAgentPromptBuilder

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

parser.add_argument('--server', 
                    nargs='?', 
                    const='2663', 
                    metavar='server_port',
                    help='Starts the BondAI web server. If no port is specified, defaults to 5000.')

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

def build_tools():
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
    
    return tools


def run_cli():
    try:
        tools = build_tools()
        if args.server:
            port = int(args.server)
            server = BondAIAPIServer(tools=tools, port=port)

            try:
                server.run()
            except KeyboardInterrupt:
                cprint(f"\n\nStopping BondAI server...\n", 'red')
                pass
        else:
            llm=OpenAILLM(MODEL_GPT4_0613)
            human_tool = HumanTool()
            human_tool.description = (
                "This tool allows you to communicate with the user and ask them questions."
                "To use this tool just put your question in the 'input' parameter."
                "Remember to always be friendly and polite!"
            )
            exit_tool = Tool('exit_tool', (
                "This tool allows you to exit the BondAI CLI."
                'You MUST call this tool if the user wants to exit the application.'
                'Do not use this tool unless the user says they want to exit the application.'
            ))

            task_agent = Agent(llm=llm, tools=tools, quiet=args.quiet, enable_sub_agent=True)
            conversational_agent = Agent(
                llm = llm,
                prompt_builder=ConversationalAgentPromptBuilder(llm, tools), 
                final_answer_tool=exit_tool,
                tools=[
                    human_tool,
                    TaskAgentTool(task_agent),
                ], 
                quiet=True
            )
            
            try:
                conversational_agent.run()
            except KeyboardInterrupt:
                cprint(f"\n\nStopping BondAI CLI...\n", 'red')
                pass
        
    except BudgetExceededException as e:
        cprint(f"\n\nThe budget for this task has been exceeded and will stop.\n", 'red')
