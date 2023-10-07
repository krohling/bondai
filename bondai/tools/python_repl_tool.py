import io
from contextlib import redirect_stdout, redirect_stderr
from pydantic import BaseModel
from multiprocessing import Process, Pipe
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

def execute_target(conn, code):
    local_vars = {}
    stdout_str, stderr_str = "", ""
    
    try:
        with io.StringIO() as stdout_io, io.StringIO() as stderr_io, redirect_stdout(stdout_io), redirect_stderr(stderr_io):
            exec(code, {}, local_vars)
            stdout_str = stdout_io.getvalue()
            stderr_str = stderr_io.getvalue()

        # Remove non-picklable objects from local_vars if any
        for key in list(local_vars.keys()):
            if not isinstance(local_vars[key], (int, float, str, list, dict, tuple)):
                del local_vars[key]
                
        conn.send([local_vars, stdout_str, stderr_str])
    except Exception as e:
        conn.send([str(e), stdout_str, stderr_str])

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
        # Create a pipe for communication
        parent_conn, child_conn = Pipe()

        process = Process(target=execute_target, args=(child_conn, code))
        process.start()
        process.join(timeout=self.execution_timeout)

        if process.is_alive():
            process.terminate()
            process.join(10)
            raise Exception("Code execution timed out")

        result, stdout, stderr = parent_conn.recv()
        if isinstance(result, str):
            raise Exception(result)

        return result, stdout, stderr








