from pydantic import BaseModel
from bondai.tools import Tool
from typing import Dict


class TaskCompletedToolParameters(BaseModel):
    user_response: str


class TaskCompletedTool(Tool):
    def __init__(self):
        super().__init__(
            "task_completed",
            "Use the task_completed tool when you have completed the requested task.",
            TaskCompletedToolParameters,
        )

    def run(self, arguments: Dict) -> Dict[str, bool]:
        return arguments["user_response"], True
