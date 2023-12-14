from pydantic import BaseModel
from typing import Dict


class InputParameters(BaseModel):
    input: str
    thought: str


class EmptyParameters(BaseModel):
    pass


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: BaseModel = EmptyParameters,
        dangerous: bool = False,
        supports_streaming: bool = False,
    ):
        if name is None:
            raise Exception("name is required")
        if description is None:
            raise Exception("description is required")
        if parameters is None:
            parameters = EmptyParameters

        self.name = name
        self.description = description
        self.parameters = parameters
        self.dangerous = dangerous
        self.supports_streaming = supports_streaming

    def get_tool_function(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.schema(),
        }

    def run(self, arguments: Dict) -> str | Dict:
        if "input" in arguments:
            return arguments["input"]

    def handle_stream_update(self, arguments_buffer: str):
        # This function is called when the agent is streaming data to the tool.
        # The arguments_buffer is a string buffer containing the latest argument data that has been received.
        pass

    def save_state() -> Dict:
        # This function is called when the agent is saving state.
        # The state should be returned as a dictionary.
        return {}

    def load_state(state: Dict):
        # This function is called when the agent is loading state.
        # The state is passed in as a dictionary.
        pass

    def stop(self):
        # This function is called when the agent is being forcibly stopped.
        pass
