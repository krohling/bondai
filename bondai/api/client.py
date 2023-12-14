import json
import requests
from socketio import Client
from bondai.util import EventMixin
from bondai.agents import AgentEventNames, ConversationMemberEventNames


class BondAIAPIClient(EventMixin):
    def __init__(self, base_url="http://127.0.0.1:2663"):
        EventMixin.__init__(
            self,
            allowed_events=[
                "agent_message",
                AgentEventNames.TOOL_SELECTED,
                AgentEventNames.TOOL_COMPLETED,
                AgentEventNames.TOOL_ERROR,
                AgentEventNames.STREAMING_CONTENT_UPDATED,
                AgentEventNames.STREAMING_FUNCTION_UPDATED,
                ConversationMemberEventNames.MESSAGE_RECEIVED,
                ConversationMemberEventNames.MESSAGE_COMPLETED,
                ConversationMemberEventNames.MESSAGE_ERROR,
                ConversationMemberEventNames.CONVERSATION_EXITED,
            ],
        )
        self.base_url = base_url
        self.ws_client = None

    def connect_ws(self):
        if self.ws_client:
            self.disconnect_ws()
        self.ws_client = Client()
        self.ws_client.connect(self.base_url)

        @self.ws_client.on("message")
        def on_message(message):
            message = json.loads(message)
            event = message.get("event")
            agent_id = message["data"]["agent_id"]

            if event == "streaming_content_updated":
                content_buffer = message["data"]["content_buffer"]
                self._trigger_event(event, agent_id, content_buffer=content_buffer)
            elif event == "streaming_function_updated":
                function_name = message["data"]["function_name"]
                arguments_buffer = message["data"]["arguments_buffer"]
                self._trigger_event(
                    event,
                    agent_id,
                    function_name=function_name,
                    arguments_buffer=arguments_buffer,
                )
            else:
                agent_message = message["data"]["message"]
                self._trigger_event(event, agent_id, message=agent_message)

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
        print(message)
        message_bytes = json.dumps(message).encode("utf-8")
        self.ws_client.send(message_bytes)

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"HTTP Request Error: {e}")

    def create_agent(self):
        return self._request("POST", "/agents")

    def send_message(self, agent_id, message):
        data = {"message": message}
        return self._request("POST", f"/agents/{agent_id}/messages", data)

    def list_agents(self):
        return self._request("GET", "/agents")

    def get_agent(self, agent_id):
        return self._request("GET", f"/agents/{agent_id}")

    def get_agent_tool_options(self, agent_id):
        return self._request("GET", f"/agents/{agent_id}/tool_options")

    def get_agent_tools(self, agent_id):
        return self._request("GET", f"/agents/{agent_id}/tools")

    def add_agent_tool(self, agent_id, tool_name):
        data = {"tool_name": tool_name}
        return self._request("POST", f"/agents/{agent_id}/tools", data)

    def remove_agent_tool(self, agent_id, tool_name):
        return self._request("DELETE", f"/agents/{agent_id}/tools/{tool_name}")

    def stop_agent(self, agent_id):
        return self._request("POST", f"/agents/{agent_id}/stop")

    def get_settings(self):
        return self._request("GET", "/settings")

    def set_settings(self, settings):
        return self._request("POST", "/settings", settings)
