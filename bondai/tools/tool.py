from pydantic import BaseModel

class InputParameters(BaseModel):
    input: str
    thought: str

class EmptyParameters(BaseModel):
    thought: str

class Tool():
     def __init__(self, name: str, description: str, parameters: BaseModel = EmptyParameters, dangerous=False, supports_streaming=False):
          if name is None:
               raise Exception('name is required')
          if description is None:
               raise Exception('description is required')
          if parameters is None:
               parameters = EmptyParameters

          self.name = name
          self.description = description
          self.parameters = parameters
          self.dangerous = dangerous
          self.supports_streaming = supports_streaming
          self.exit_agent = False
     
     def get_tool_function(self):
          return {
               "name": self.name,
               "description": self.description,
               "parameters": self.parameters.schema()
          }

     def run(self, arguments):
          if 'input' in arguments:
               return arguments['input']
     
     def handle_stream_update(self, arguments_buffer):
          # This function is called when the agent is streaming data to the tool.
          # The arguments_buffer is a string buffer containing the latest argument data that has been received.
          pass
    