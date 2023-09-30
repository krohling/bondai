import json
import threading
from bondai.tools import Tool, InputParameters

TOOL_NAME = 'conversation_tool'
TOOL_DESCRIPTION = (
    "This tool allows you to communicate with the user and ask them questions."
    "To use this tool just put your message in the 'input' parameter."
    "Remember to always be friendly and polite!"
)

class ConversationTool(Tool):
    def __init__(self, socketio):
        super(ConversationTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, InputParameters)
        self.socketio = socketio
        self.message_arrived_event = threading.Event()
        self.user_message = None
        self._setup_socket_listener()

    def _setup_socket_listener(self):
        # Set up the event listener once during initialization
        @self.socketio.on('message')
        def handle_message(message):
            message = json.loads(message)
            if message.get('event') == 'user_message':
                self.user_message = message['data']['message']
                self.message_arrived_event.set()

    def run(self, arguments):
        # Check for required arguments
        question = arguments.get('input')
        if not question:
            raise ValueError("'input' argument is required")

        # Reset for each run
        self.user_message = None
        self.message_arrived_event.clear()

        # Emit message, now that our listener is guaranteed to be active
        message = {
            'event': 'agent_message',
            'data': {
                'message': question
            }
        }
        payload = json.dumps(message)
        self.socketio.send(payload)

        # Wait for user message
        self.message_arrived_event.wait()
        result = self.user_message
        self.user_message = None
        print(result)

        return result
