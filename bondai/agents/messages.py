import uuid
from abc import ABC
from typing import List, Dict, Set
from datetime import datetime
from dataclasses import dataclass, field, is_dataclass

USER_MEMBER_NAME = "user"
DEFAULT_MEMORY_WARNING_MESSAGE = (
    "Warning: the conversation history will soon reach its maximum length and be trimmed. "
    "Make sure to save any important information from the conversation to your memory before it is removed."
)


@dataclass
class AgentMessage(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str | None = field(default=None)
    timestamp: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class SystemMessage(AgentMessage):
    role: str = field(default="system")
    message: str | None = field(default=None)


@dataclass
class SummaryMessage(AgentMessage):
    role: str = field(default="user")
    message: str | None = field(default=None)
    children: List[AgentMessage] = field(default=None)


@dataclass
class ConversationMessage(AgentMessage):
    role: str = field(default="user")
    sender_name: str | None = field(default=None)
    recipient_name: str | None = field(default=None)
    message: str | None = field(default=None)
    message_summary: str | None = field(default=None)
    require_response: bool = field(default=True)
    success: bool = field(default=False)
    error: Exception | None = field(default=None)
    conversation_exited: bool = field(default=False)
    cost: float | None = field(default=None)
    completed_at: datetime | None = field(default=None)


@dataclass
class ToolUsageMessage(AgentMessage):
    role: str = field(default="function")
    tool_name: str | None = field(default=None)
    tool_arguments: Dict | None = field(default=None)
    tool_output: str | None = field(default=None)
    tool_output_summary: str | None = field(default=None)
    success: bool = field(default=False)
    error: Exception | None = field(default=None)
    agent_halted: bool = field(default=False)
    cost: float | None = field(default=None)
    completed_at: datetime | None = field(default=None)


def custom_serialization(value):
    """
    Serialize special types like datetime, Exception, and nested AgentMessage objects.
    """
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Exception):
        return str(value)
    elif is_dataclass(value) and not isinstance(value, type):
        return message_to_dict(value)
    return value


def message_to_dict(message: AgentMessage) -> Dict:
    """
    Convert an AgentMessage object to a dictionary with custom serialization.
    """

    message_dict = {
        k: custom_serialization(v)
        for k, v in message.__dict__.items()
        if k != "children"
    }
    message_dict["type"] = type(message).__name__  # Add the type for deserialization
    if "children" in message.__dict__:
        message_dict["children"] = [
            message_to_dict(child) for child in message.children
        ]

    return message_dict


class AgentMessageList:
    def __init__(self, messages: List[AgentMessage] | None = None):
        self._items: List[AgentMessage] = []
        self._ids: Set[str] = set()
        if messages:
            for message in messages:
                self.add(message)

    def add(self, item: AgentMessage):
        if item.id not in self._ids:
            self._ids.add(item.id)
            self._items.append(item)
            self._items = list(sorted(self._items, key=lambda x: x.timestamp))

    def remove(self, item: AgentMessage):
        if item.id in self._ids:
            self._ids.remove(item.id)
            self._items.remove(item)

    def remove_after(self, timestamp: datetime, inclusive: bool = True):
        if inclusive:
            self._items = [item for item in self._items if item.timestamp <= timestamp]
        else:
            self._items = [item for item in self._items if item.timestamp < timestamp]
        self._ids = set([item.id for item in self._items])

    def clear(self):
        self._items = []
        self._ids = set()

    def __getitem__(self, index: int):
        return self._items[index]

    def __add__(self, other: List[AgentMessage] | "AgentMessageList"):
        if isinstance(other, AgentMessageList):
            # If the other object is also an AgentMessageList, extend with its items
            return self._items + other._items
        elif isinstance(other, list):
            # If the other object is a list, just concatenate the lists
            return self._items + other
        else:
            # If the other object is neither, raise an exception
            raise TypeError(
                f"Unsupported operand type(s) for +: 'AgentMessageList' and '{type(other).__name__}'"
            )

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        return item.id in self._ids

    def __len__(self):
        return len(self._items)

    def to_dict(self) -> List[Dict]:
        """
        Convert the AgentMessageList to a list of dictionaries for serialization.
        """
        return [message_to_dict(message) for message in self._items]

    @classmethod
    def from_dict(cls, data: List[Dict]) -> "AgentMessageList":
        """
        Create an AgentMessageList from a list of dictionaries.
        """
        list_instance = cls()
        for item in data:
            item_type = item["type"]
            del item["type"]
            if item_type == "ConversationMessage":
                message = ConversationMessage(**item)
            elif item_type == "ToolUsageMessage":
                message = ToolUsageMessage(**item)
            elif item_type == "SystemMessage":
                message = SystemMessage(**item)
            elif item_type == "SummaryMessage":
                message = SummaryMessage(**item)
            # elif item_type == 'MemoryWarningMessage':
            #     message = MemoryWarningMessage(**item)
            else:
                raise ValueError(f"Unknown message type: {item_type}")

            if "timestamp" in item:
                message.timestamp = datetime.fromisoformat(item["timestamp"])
            if "completed_at" in item and item["completed_at"]:
                message.completed_at = datetime.fromisoformat(item["completed_at"])
            list_instance.add(message)

        return list_instance
