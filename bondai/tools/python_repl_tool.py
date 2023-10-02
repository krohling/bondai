import threading
import io
from contextlib import redirect_stdout, redirect_stderr
from pydantic import BaseModel
from bondai.tools import Tool

DEFAULT_EXECUTION_TIMEOUT = 60
TOOL_NAME = 'python_repl'
TOOL_DESCRIPTION = (
    "This tool allows you to execute Python code. "
    "Specify your Python code in the 'code' parameter and it will return the result."
)

class Parameters(BaseModel):
    code: str
    thought: str

class PythonREPLTool(Tool):
    def __init__(self, execution_timeout=DEFAULT_EXECUTION_TIMEOUT):
        super(PythonREPLTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, parameters=Parameters, dangerous=True)
        self.execution_timeout = execution_timeout
    
    def run(self, arguments):
        code = arguments.get('code')

        if code is None:
            raise Exception("'code' parameter is required")

        result, stdout, stderr = self.execute_code(code)
        
        response = ""
        
        # Include stdout if present
        if stdout:
            response += f"Output:\n{stdout}\n"
            
        # Include stderr if present
        if stderr:
            response += f"Errors:\n{stderr}\n"
        
        # Include result if present
        if result:
            formatted_result = "\n".join([f"{key}: {value}" for key, value in result.items()])
            response += f"Result Variables:\n{formatted_result}\n"

        if not response:
            response = "Code executed successfully. No output or result variables."
        
        return response
    
    def execute_code(self, code):
        # Capture stdout and stderr
        thread_exception = None
        stdout_io = io.StringIO()
        stderr_io = io.StringIO()

        # Use threading to enforce timeout
        def target(local_vars, code):
            nonlocal thread_exception
            try:
                with redirect_stdout(stdout_io), redirect_stderr(stderr_io):
                    exec(code, {}, local_vars)
            except Exception as e:
                thread_exception = e
        
        local_vars = {}
        thread = threading.Thread(target=target, args=(local_vars, code))
        thread.start()
        thread.join(timeout=self.execution_timeout)

        if thread_exception:
            raise thread_exception
        
        if thread.is_alive():
            thread.join(timeout=10)
            raise Exception("Code execution timed out")

        stdout = stdout_io.getvalue()
        stderr = stderr_io.getvalue()

        return local_vars, stdout, stderr

