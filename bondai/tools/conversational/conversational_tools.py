from pydantic import BaseModel
from bondai.tools import Tool
from typing import Dict, Tuple
from bondai.agents.messages import ConversationMessage


SEND_MESSAGE_TOOL_NAME = "send_message"
SEND_MESSAGE_TOOL_DESCRIPTION = (
    "Use the send_message tool to send messages to other members of the conversation including agents and the user. "
    "The send_message tool takes three arguments: recipient_name, message, and require_response. "
    "The recipient_name argument is the name of the recipient of the message. "
    "The message argument is the message to be sent to the recipient. "
    "The require_response argument is a boolean value that indicates whether a response from the recipient is necessary. "
    "The require_response argument defaults to True. If you do not require a response from the message recipient, set require_response to False."
)


class SendMessageToolParameters(BaseModel):
    recipient_name: str
    message: str
    require_response: bool = True


class SendMessageTool(Tool):
    def __init__(self):
        super().__init__(
            SEND_MESSAGE_TOOL_NAME,
            SEND_MESSAGE_TOOL_DESCRIPTION,
            SendMessageToolParameters,
        )

    def run(
        self, recipient_name: str, message: str, require_response: bool = True
    ) -> Dict[str, bool]:
        return (
            ConversationMessage(
                role="assistant",
                recipient_name=recipient_name,
                message=message,
                require_response=require_response,
            ),
            True,
        )


EXIT_CONVERSATION_TOOL_NAME = "exit_conversation"


class ExitConversationTool(Tool):
    def __init__(self):
        super().__init__(
            EXIT_CONVERSATION_TOOL_NAME,
            "Use the exit_conversation tool to exit the conversation once your task has been completed.",
        )

    def run(self, arguments: Dict) -> Tuple[str, bool]:
        return None, True
