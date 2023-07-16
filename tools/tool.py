from pydantic import BaseModel

class DefaultParameters(BaseModel):
    input: str
    thought: str

class Tool(object):
     """
     Base class for all tools.
     """
     def __init__(self, name: str, description: str, parameters: BaseModel = DefaultParameters):
          self.name = name
          self.description = description
          self.parameters = parameters
    
     def get_tool_function(self):
          return {
               "name": self.name,
               "description": self.description,
               "parameters": self.parameters.schema()
          }

     def run(self, input):
          raise NotImplementedError()
    