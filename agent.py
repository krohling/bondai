import json
from collections import namedtuple
from bond.models.openai_wrapper import get_completion
from bond.tools.tool import Tool
from bond.models.openai_wrapper import count_tokens

TOOL_MAX_TOKEN_RESPONSE = 2000
FINAL_ANSWER_TOOL = Tool('final_answer', "Use the final_answer tool when you have all the information you need to provide the final answer.")

class AgentStep:
    def __init__(self, prompt, message, function=None):
        self.prompt = prompt
        self.message = message
        self.function = function
        self.output = None
        self.error = False
        self.final_answer = False
        self.monitor_feedback = None


class Agent:

    def __init__(self, prompt_builder, tools=[], model='gpt-3.5-turbo-0613', max_step_memory=10, monitor_agent=None):
        self.previous_steps = []
        self.prompt_builder = prompt_builder
        self.tools = tools
        self.model = model
        self.max_step_memory = max_step_memory
        self.monitor_agent = monitor_agent
    
    def run_once(self, task, previous_steps=[]):
        prompt = self.prompt_builder.build_prompt(task, self.tools, previous_steps)
        functions = list(map(lambda t: t.get_tool_function(), self.tools))

        # print("**********************")
        print("Thinking about next step...")
        message, function = get_completion(prompt, '', [], functions, self.model)

        # print("******RESPONSE********")
        # print(message)
        print(function)
        
        if function:
            step = AgentStep(prompt, message, function)
            tools = [t for t in self.tools if t.name == function['name']]
            if len(tools) > 0:
                tool = tools[0]
                
                try:
                    args = json.loads(function['arguments'])
                    if tool.name == FINAL_ANSWER_TOOL.name:
                        step.output = args['input']
                        step.final_answer = True
                    else:
                        try:
                            step.output = tool.run(args)
                            if step.output:
                                if count_tokens(step.output) > TOOL_MAX_TOKEN_RESPONSE:
                                    step.output = f"The result from this tool was greater than {TOOL_MAX_TOKEN_RESPONSE} tokens and could not be displayed."
                            else:
                                step.output = "This command ran successfully with no output."
                            print(step.output)
                        except Exception as e:
                            print("An Error occured: " + str(e))
                            step.error = True
                            step.output = "An Error occured: " + str(e)
                except Exception as e:
                    step.error = True
                    step.output = 'An Error occured: The provided arguments were not valid JSON. Valid JSON must ALWAYS BE PROVIDED in the response.'
            else:
                step.error = True
                step.output = f"An Error occured: The function '{function['name']}' does not exist."
        else:
            step = AgentStep(prompt, message)
            step.output = "No function was provided."
        

        return step
    
    def reset_memory(self):
        self.previous_steps = []

    def run(self, task):
        self.tools = self.tools + [FINAL_ANSWER_TOOL]

        while True:
            visible_steps = self.previous_steps[-self.max_step_memory:]
            step = self.run_once(task, visible_steps)
            self.previous_steps.append(step)
            if step.final_answer:
                return step
            elif self.monitor_agent:
                print("Getting feedback...")
                monitor_step = self.monitor_agent.run_once(task, visible_steps)
                # step.monitor_feedback = monitor_step.message
                print(monitor_step.message)
                print(monitor_step.function)

