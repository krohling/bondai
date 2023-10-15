import json
import requests
from socketio import Client

class BondAIAPIClient:
    def __init__(self, base_url='http://127.0.0.1:2663'):
        self.base_url = base_url
        self.ws_client = None
        self._events = {
            'conversational_agent_started': [],
            'conversational_agent_message': [],
            'conversational_agent_completed': [],
            'task_agent_started': [],
            'task_agent_step_started': [],
            'task_agent_step_tool_selected': [],
            'task_agent_step_completed': [],
            'task_agent_completed': [],
        }
    
    def on(self, event_name):
        """Register a callback to an event."""
        if event_name not in self._events:
            raise ValueError(f"Unsupported event '{event_name}'")

        def decorator(callback):
            self._events[event_name].append(callback)
            return callback
        
        return decorator

    def _trigger_event(self, event_name, agent_id, *args, **kwargs):
        """Trigger the specified event."""
        for callback in self._events.get(event_name, []):
            callback(agent_id, *args, **kwargs)
    
    def connect_ws(self):
        if self.ws_client:
            self.disconnect_ws()
        self.ws_client = Client()
        self.ws_client.connect(self.base_url)

        @self.ws_client.on('message')
        def on_message(message):
            message = json.loads(message)
            print(message)
            event = message.get('event')
            agent_id = message['data']['agent_id']

            if event == 'conversational_agent_started':
                self._trigger_event(event, agent_id)
            elif event == 'conversational_agent_message':
                self._trigger_event(event, agent_id, message['data']['message'])
            elif event == 'conversational_agent_completed':
                self._trigger_event(event, agent_id)
            elif event == 'task_agent_started':
                self._trigger_event(event, agent_id)
            elif event == 'task_agent_completed':
                self._trigger_event(event, agent_id)
            elif event == 'task_agent_step_started':
                self._trigger_event(event, agent_id)
            elif event == 'task_agent_step_tool_selected':
                self._trigger_event(event, agent_id, message['data']['step'])
            elif event == 'task_agent_step_completed':
                self._trigger_event(event, agent_id, message['data']['step'])

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
    
    def send_user_message(self, agent_id, message):
        self.send_ws_message("user_message", {
            "agent_id": agent_id,
            "message": message
        })

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

    def create_agent(self):
        return self._request('POST', '/agents')
    
    def list_agents(self):
        return self._request('GET', '/agents')
    
    def get_agent(self, agent_id):
        return self._request('GET', f'/agents/{agent_id}')
    
    def get_agent_tool_options(self, agent_id):
        return self._request('GET', f'/agents/{agent_id}/tool_options')
    
    def get_agent_tools(self, agent_id):
        return self._request('GET', f'/agents/{agent_id}/tools')
    
    def add_agent_tool(self, agent_id, tool_name):
        data = {'tool_name': tool_name}
        return self._request('POST', f'/agents/{agent_id}/tools', data)
    
    def remove_agent_tool(self, agent_id, tool_name):
        return self._request('DELETE', f'/agents/{agent_id}/tools/{tool_name}')
    
    def start_agent(self, agent_id, task=None, task_budget=None, max_steps=None):
        data = {}
        if task:
            data['task'] = task
        if task_budget:
            data['task_budget'] = task_budget
        if max_steps:
            data['max_steps'] = max_steps
        return self._request('POST', f'/agents/{agent_id}/start', data)
    
    def stop_agent(self, agent_id):
        return self._request('POST', f'/agents/{agent_id}/stop')
    
    def get_settings(self):
        return self._request('GET', '/settings')
    
    def set_settings(self, settings):
        return self._request('POST', '/settings', settings)