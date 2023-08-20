from pydantic import BaseModel

class InputParameters(BaseModel):
    input: str
    thought: str

class EmptyParameters(BaseModel):
    thought: str

class Tool():
     def __init__(self, name: str, description: str, parameters: BaseModel = EmptyParameters):
          if name is None:
               raise Exception('name is required')
          if description is None:
               raise Exception('description is required')
          if parameters is None:
               parameters = EmptyParameters

          self.name = name
          self.description = description
          self.parameters = parameters
    
     def get_tool_function(self):
          return {
               "name": self.name,
               "description": self.description,
               "parameters": self.parameters.schema()
          }

     def run(self, arguments):
          if self.parameters == InputParameters and 'input' in arguments:
               return arguments['input']
               
    