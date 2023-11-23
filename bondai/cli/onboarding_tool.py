import json
from pydantic import BaseModel
from typing import List
from bondai.tools import Tool

TOOL_NAME = 'final_answer'
TOOL_DESCRIPTION = """Use this tool ONLY after you have captured ALL of the required information from the user. This tool will send the information to the next AI assistant that will complete the task.
- user_exit: This is a boolean value that indicates whether the user has asked to exit. If the user has asked to exit you should NOT ask for any other information from the user.
- task_description: This must be detailed enough for the next AI assistant to understand what the user wants to do. Ask the user any necessary follow up questions.
- task_budget: This parameter is OPTIONAL. DO NOT force the user to provide this. The task budget is the maximum amount of money the user is willing to spend on OpenAI API calls to complete this task.
- user_confirmation: This is a boolean value that indicates whether the user has confirmed the task description, task budget, and tool ids.
"""

class Parameters(BaseModel):
    user_exit: bool = False
    task_description: str
    task_budget: float
    user_confirmation: bool = False

class OnboardingTool(Tool):
    def __init__(self):
        super(OnboardingTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
    
    def run(self, arguments):
        user_exit = arguments.get('user_exit')
        if user_exit:
            return json.dumps({
                'user_exit': True
            })

        task_description = arguments.get('task_description')
        task_budget = arguments.get('task_budget') if arguments.get('task_budget') else None
        user_confirmation = arguments.get('user_confirmation')

        if not task_description:
            raise Exception('You must provide a task description.')
        if not user_confirmation:
            raise Exception('You must confirm the task description with the user before calling the final_answer tool.')
        
        return json.dumps({
            'task_description': task_description,
            'task_budget': task_budget
        })
