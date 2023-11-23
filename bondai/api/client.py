import json
import requests
from socketio import Client

class BondAIAPIClient:
    def __init__(self, base_url='http://127.0.0.1:2663'):
        self.base_url = base_url
        self.ws_client = None
        self._events = {
            'agent_message': [],
            'agent_started': [],
            'agent_step_completed': [],
            'agent_completed': [],
        }
    
    def on(self, event_name):
        """Register a callback to an event."""
        if event_name not in self._events:
            raise ValueError(f"Unsupported event '{event_name}'")

        def decorator(callback):
            self._events[event_name].append(callback)
            return callback
        
        return decorator

    def _trigger_event(self, event_name, *args, **kwargs):
        """Trigger the specified event."""
        for callback in self._events.get(event_name, []):
            callback(*args, **kwargs)
    
    def connect_ws(self):
        if self.ws_client:
            self.disconnect_ws()
        self.ws_client = Client()
        self.ws_client.connect(self.base_url)

        @self.ws_client.on('message')
        def on_message(message):
            message = json.loads(message)
            if message.get('event') == 'agent_message':
                self._trigger_event('agent_message', message['data']['message'])
            elif message.get('event') == 'agent_step_completed':
                self._trigger_event('agent_step_completed', message['data']['step'])
            elif message.get('event') == 'agent_started':
                self._trigger_event('agent_started')
            elif message.get('event') == 'agent_completed':
                self._trigger_event('agent_completed')

    def disconnect_ws(self):
        if self.ws_client:
            self.ws_client.disconnect()
            self.ws_client = None
    
    def is_ws_connected(self):
        return self.ws_client and self.ws_client.connected

    def send_ws_message(self, event, data):
        if not self.is_ws_connected():
            self.connect_ws()
        message = {"event": event, "data": data}
        message_bytes = json.dumps(message).encode('utf-8')
        self.ws_client.send(message_bytes)
    
    def send_user_message(self, message):
        self.send_ws_message("user_message", {"message": message})

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"HTTP Request Error: {e}")

    def get_agent(self):
        return self._request('GET', '/agent')

    def start_agent(self, task=None, task_budget=None, max_steps=None):
        data = {}
        if task:
            data['task'] = task
        if task_budget:
            data['task_budget'] = task_budget
        if max_steps:
            data['max_steps'] = max_steps
        return self._request('POST', '/agent/start', data)

    def add_agent_tool(self, tool_name):
        data = {'tool_name': tool_name}
        return self._request('POST', '/agent/tools', data)

    def remove_agent_tool(self, tool_name):
        return self._request('DELETE', f'/agent/tools/{tool_name}')

    def get_tools(self):
        return self._request('GET', '/tools')