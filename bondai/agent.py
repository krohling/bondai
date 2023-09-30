import json
import threading
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

AGENT_STATE_RUNNING = 'AGENT_STATE_RUNNING'
AGENT_STATE_STOPPED = 'AGENT_STATE_STOPPED'

def format_print_string(s, length=100):
    # Remove newlines
    s = s.replace('\n', ' ').replace('\r', '')
    
    if len(s) <= length:
        return s
    return s[:length - 3] + "..."


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

class MaxStepsExceededException(Exception):
    pass

class Agent:

    def __init__(self, prompt_builder=None, tools=[], llm=OpenAILLM(MODEL_GPT4_0613), fallback_llm=OpenAILLM(MODEL_GPT35_TURBO_0613), final_answer_tool=DEFAULT_FINAL_ANSWER_TOOL, quiet=False, enable_sub_agent=False):
        if not prompt_builder:
            self.prompt_builder = DefaultPromptBuilder(llm)
        else:
            self.prompt_builder = prompt_builder
        
        if enable_sub_agent:
            tools.append(AgentTool(tools=tools, llm=llm))
        
        self.state = AGENT_STATE_STOPPED
        self.previous_steps = []
        self.previous_messages = []
        self.response_query_tool = ResponseQueryTool()
        self.tools = tools
        self.llm = llm
        self.fallback_llm = fallback_llm
        self.final_answer_tool = final_answer_tool
        self.quiet = quiet
        self._thread = None
        self._stop_thread = False
        self._events = {
            'started': [],
            'step_completed': [],
            'completed': [],
        }
    
    def on(self, event_name):
        """Register a callback to an event."""
        if event_name not in self._events:
            raise ValueError(f"Unsupported event '{event_name}'")

        def decorator(callback):
            self._events[event_name].append(callback)
            return callback
        
        return decorator
    
    def _trigger_event(self, event_name, *args, **kwargs):
        """Trigger the specified event."""
        for callback in self._events.get(event_name, []):
            callback(*args, **kwargs)


    def add_tool(self, tool):
        if self.state == AGENT_STATE_RUNNING:
            raise Exception('Cannot modify agent while it is in a running state.')
        if not any([t.name == tool.name for t in self.tools]):
            self.tools.append(tool)
    
    def remove_tool(self, tool_name):
        if self.state == AGENT_STATE_RUNNING:
            raise Exception('Cannot modify agent while it is in a running state.')
        self.tools = [t for t in self.tools if t.name != tool_name]
    
    def run_once(self, task=''):
        tools = self.tools
        if len(self.response_query_tool.responses) > 0:
            tools.append(self.response_query_tool)

        prompt = self.prompt_builder.build_prompt(task, tools, self.previous_steps)
        functions = list(map(lambda t: t.get_tool_function(), tools))

        use_streaming = self.llm.supports_streaming() and any([t.supports_streaming for t in self.tools])
        if use_streaming:
            def function_stream_callback(function_name, arguments_buffer):
                streaming_tools = [t for t in self.tools if t.name == function_name and t.supports_streaming]
                if len(streaming_tools) > 0:
                    tool = streaming_tools[0]
                    tool.handle_stream_update(arguments_buffer)
            
            message, function = self.llm.get_streaming_completion(
                prompt, 
                previous_messages=self.previous_messages, 
                functions=functions, 
                function_stream_callback=function_stream_callback
            )
        else:
            message, function = self.llm.get_completion(
                prompt, 
                previous_messages=self.previous_messages, 
                functions=functions
            )

        if not function:
            message, function = self.fallback_llm.get_completion(
                message, 
                system_prompt='Select the correct function and parameters to use based on the prompt', 
                previous_messages=[], 
                functions=functions
            )

        if not function and not self.quiet:
            cprint(f"No function was selected.", 'red')
            cprint(message, 'red')
            
        if function:
            step = AgentStep(prompt, message, function)
            tools = [t for t in self.tools if t.name == function['name']]
            if len(tools) > 0:
                tool = tools[0]
                
                try:
                    args = function['arguments'] if 'arguments' in function else {}
                    
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
        if self.state == AGENT_STATE_RUNNING:
            raise Exception('Cannot modify agent while it is in a running state.')
        self.previous_steps = []

    def run(self, task='', task_budget=None, max_steps=None):
        task = '' if not task else task
        if self.state == AGENT_STATE_RUNNING:
            raise Exception('Cannot modify agent while it is in a running state.')
        
        self.state = AGENT_STATE_RUNNING
        try:
            self._trigger_event('started')
            if self.final_answer_tool:
                self.tools = self.tools + [self.final_answer_tool]

            step_counter = 0
            while True:
                if self._stop_thread:
                    break
                step_counter += 1
                step = self.run_once(task)

                if step.function or len(self.previous_steps) == 0 or self.previous_steps[-1].function:
                    self.previous_steps.append(step)
                    self._trigger_event('step_completed', step)
                
                total_cost = get_total_cost()
                if not self.quiet:
                    print(colored("Total Cost:", 'green', attrs=["bold"]), colored('$' + str(round(total_cost, 2)), 'white'))

                if step.exit:
                    self.previous_messages.append({
                        'prompt': task,
                        'response': step.output
                    })
                    return step

                if task_budget and total_cost >= task_budget:
                    raise BudgetExceededException("The budget for this task has been reached without successfully finishing.")
                if max_steps and step_counter >= max_steps:
                    raise MaxStepsExceededException("The maximum number of steps has been reached without successfully finishing.")
        finally:
            self._trigger_event('completed')
            self.state = AGENT_STATE_STOPPED

    def run_async(self, task='', task_budget=None, max_steps=None):
        """Runs the agent's task in a separate thread."""
        if self.state == AGENT_STATE_RUNNING or (self._thread and self._thread.is_alive()):
            raise Exception('Cannot start agent while it is in a running state.')
        self._thread = threading.Thread(target=self.run, args=(task, task_budget, max_steps))
        self._thread.start()

    def join(self):
        """Blocks until the thread completes."""
        if self._thread:
            self._thread.join()

    def stop(self):
        """Gracefully stops the thread."""
        self._stop_thread = True
        if self._thread:
            self._thread.join()
        self._stop_thread = False

