#!/usr/bin/env python3

import os
import sys
import json
from termcolor import cprint, colored
from bondai import Agent, BudgetExceededException
from bondai.models.openai import enable_logging
from bondai.tools import HumanTool
from bondai.cli import get_tools, OnboardingTool

if not os.environ.get('OPENAI_API_KEY'):
    cprint(f"Please set the OPENAI_API_KEY environment variable.", 'red')
    exit(1)

cprint(f"Loading BondAI...", 'white')

enable_dangerous = "--enable_dangerous" in sys.argv
tool_options = get_tools()

if not enable_dangerous:
    tool_options = [tool for tool in tool_options if not tool.dangerous]

tool_descriptions = ''.join([f"{tool.name}: {tool.description}\n" for tool in tool_options])

WELCOME_TEXT = """
Welcome to BondAI!
I have been trained to help you with a variety of tasks.
To get started, just tell me what task you would like me to help you with.
If you would like to exit, just type 'exit'.

What can I help you with today?
"""

ONBOARDING_TASK = f"""
You are BondAI's helpful and friendly Onboarding AI assistant. You should communicate in a friendly and helpful manner.
Your job is to help understand what task the user wants to complete and gather all the information needed to start the task.
This information will then be given to another AI assistant that will complete the task.
Once you have gathered ALL of the required information from the user you will call the 'final_answer' tool to send the information to the next AI assistant.
ALWAYS greet the user with a friendly message.


You MUST gather the following REQUIRED information from the user:
- The Task Description (task_description): This must be detailed enough for the next AI assistant to understand what the user wants to do. Ask the user any necessary follow up questions. Confirm that the description you have with the user before calling the 'final_answer' tool.
- The Task Budget (task_budget): This is the maximum amount of money the user is willing to spend on this task. Ask the user any necessary follow up questions. Confirm that the budget you have with the user before calling the 'final_answer' tool.


IMPORTANT information:
- ALWAYS greet the user with a friendly message.
- If the user asks to exit you should call the 'final_answer' tool with the 'user_exit' parameter set to True. DO NOT ask for any other information from the user.
- ALWAYS confirm the Task Description and Task Budget with the user before calling the 'final_answer' tool.


REMEMBER: ALWAYS greet the user with a friendly message. Here is an example greeting you can use to get started:
```
{WELCOME_TEXT}
```

This is the list of all tools that you have access to:
{tool_descriptions}
"""

def get_task_definition():
    onboarding_tools = [
        HumanTool(),
        OnboardingTool()
    ]
    onboarding_agent = Agent(tools=onboarding_tools, quiet=True)
    onboarding_result = onboarding_agent.run(ONBOARDING_TASK)
    return json.loads(onboarding_result.output)

def run_task(task_config):
    task_description = task_config.get('task_description')
    task_budget = task_config.get('task_budget')

    print(colored("Starting Task:", 'white', attrs=["bold"]), colored(task_description, 'white'))
    print(colored("Budget:", 'white', attrs=["bold"]), colored(f"${task_budget}", 'white'))
    print(colored("Tools:", 'white', attrs=["bold"]), colored("\n".join(tool_ids), 'white'))
    
    agent = Agent(tools=tool_options, budget=task_budget, quiet=False)
    try:
        result = agent.run(task_description)
        cprint(f"\n\n{result.output}\n", 'white')
    except BudgetExceededException as e:
        cprint(f"\n\nThe budget for this task has been exceeded and will stop.\n", 'red')


def main():
    while True:
        task_config = get_task_definition()
        if task_config.get('user_exit'):
            break
        run_task(task_config)

if __name__ == '__main__':
    main()
