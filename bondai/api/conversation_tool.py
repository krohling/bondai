import json
from threading import Event
from socketio import Server
from typing import List
from bondai.tools import Tool, InputParameters

TOOL_NAME = 'conversation_tool'
TOOL_DESCRIPTION = (
    "This tool allows you to communicate with the user and ask them questions."
    "To use this tool just put your message in the 'input' parameter."
    "Remember to always be friendly and polite!"
)

class ConversationTool(Tool):
    def __init__(self, socketio: Server):
        super(ConversationTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, InputParameters)
        self._socketio: Server = socketio
        self._message_arrived_event: Event = Event()
        self._user_message: str = None
        self._setup_socket_listener()

    def _setup_socket_listener(self):
        # Set up the event listener once during initialization
        @self._socketio.on('message')
        def handle_message(message):
            message = json.loads(message)
            if message.get('event') == 'user_message':
                self._user_message = message['data']['message']
                self._message_arrived_event.set()

    def run(self, arguments) -> str:
        # Check for required arguments
        question = arguments.get('input')
        if not question:
            raise ValueError("'input' argument is required")

        # Reset for each run
        self._user_message = None
        self._message_arrived_event.clear()

        # Emit message, now that our listener is guaranteed to be active
        message = {
            'event': 'agent_message',
            'data': {
                'message': question
            }
        }
        payload = json.dumps(message)
        self._socketio.send(payload)

        # Wait for user message
        self._message_arrived_event.wait()
        result = self._user_message
        self._user_message = None
        print(result)

        return result
