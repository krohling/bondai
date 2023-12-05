from pydantic import BaseModel
from bondai.tools import Tool
from typing import Dict, Tuple
from bondai.agents.messages import ConversationMessage


SEND_MESSAGE_TOOL_NAME = 'send_message'

class SendMessageToolParameters(BaseModel):
    recipient_name: str
    message: str

class SendMessageTool(Tool):
    def __init__(self):
        super().__init__(
            SEND_MESSAGE_TOOL_NAME,
            "Use the send_message tool to send messages to other members of the conversation.", 
            SendMessageToolParameters
        )

    def run(self, arguments: Dict) -> Dict[str, bool]:
        if not arguments['recipient_name']:
            raise ValueError('recipient_name is required')
        if not arguments['message']:
            raise ValueError('message is required')

        return ConversationMessage(
            role='assistant',
            recipient_name=arguments['recipient_name'],
            message=arguments['message'],
        ), True

EXIT_CONVERSATION_TOOL_NAME = 'exit_conversation'

class ExitConversationTool(Tool):
    def __init__(self):
        super().__init__(
            EXIT_CONVERSATION_TOOL_NAME, 
            "Use the exit_conversation tool to exit the conversation once your task has been completed."
        )
    
    def run(self, arguments: Dict) -> Tuple[str, bool]:
        return None, True
