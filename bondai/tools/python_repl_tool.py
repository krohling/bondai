import threading
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = 'python_repl'
TOOL_DESCRIPTION = (
    "This tool allows you to execute Python code. "
    "Specify your Python code in the 'code' parameter and it will return the result."
)

class Parameters(BaseModel):
    code: str
    thought: str

class PythonREPLTool(Tool):
    def __init__(self):
        super(PythonREPLTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, parameters=Parameters, dangerous=True)
    
    def run(self, arguments):
        code = arguments.get('code')

        if code is None:
            return 'Error: code is required'

        # Check for harmful patterns
        if self.is_harmful(code):
            return 'Error: Harmful patterns detected in code'

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

        print(response)
        return response
    
    def execute_code(self, code):
        # Capture stdout and stderr
        stdout_io = io.StringIO()
        stderr_io = io.StringIO()

        # Use threading to enforce timeout
        def target(local_vars, code):
            with redirect_stdout(stdout_io), redirect_stderr(stderr_io):
                exec(code, {}, local_vars)
        
        local_vars = {}
        thread = threading.Thread(target=target, args=(local_vars, code))
        thread.start()
        thread.join(timeout=5)  # 5 seconds timeout
        
        if thread.is_alive():
            thread.join()  # Ensure it's stopped
            raise Exception("Code execution timed out")

        stdout = stdout_io.getvalue()
        stderr = stderr_io.getvalue()

        return local_vars, stdout, stderr

    def is_harmful(self, code):
        # Simple checks for potentially harmful patterns. This should be more exhaustive!
        harmful_patterns = [
            'import os',
            'import sys',
            'open(',
            '__import__(',
            'exec(',
            'eval('
        ]
        for pattern in harmful_patterns:
            if pattern in code:
                return True
        return False

# Modular extension to allow imports (example)
class AdvancedPythonREPLTool(PythonREPLTool):
    def __init__(self):
        super(AdvancedPythonREPLTool, self).__init__()

    def allowed_imports(self):
        # Example allowed imports; this list can be expanded as needed
        return ['math', 'datetime']
    
    def is_harmful(self, code):
        # Check if the code tries to import a non-allowed module
        if 'import' in code:
            for module in self.allowed_imports():
                if f"import {module}" in code:
                    code = code.replace(f"import {module}", "")
        return super().is_harmful(code)

