import uuid
from abc import ABC
from enum import Enum
from typing import List, Dict, Set
from datetime import datetime
from dataclasses import dataclass, field

USER_MEMBER_NAME = 'user'

@dataclass
class AgentMessage(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str | None = field(default=None)
    timestamp: datetime = field(default_factory=lambda: datetime.now())

@dataclass
class StatusMessage(AgentMessage):
    role: str = field(default='status')
    message: str | None = field(default=None)

@dataclass
class ConversationMessage(AgentMessage):
    role: str = field(default='user')
    sender_name: str | None = field(default=None)
    recipient_name: str | None = field(default=None)
    message: str | None = field(default=None)
    success: bool = field(default=False)
    error: Exception | None = field(default=None)
    agent_exited: bool = field(default=False)
    cost: float | None = field(default=None)
    completed_at: datetime | None = field(default=None)

@dataclass
class ToolUsageMessage(AgentMessage):
    role: str = field(default='tool')
    tool_name: str | None = field(default=None)
    tool_arguments: Dict | None = field(default=None)
    tool_output: str | None = field(default=None)
    success: bool = field(default=False)
    error: Exception | None = field(default=None)
    agent_exited: bool = field(default=False)
    cost: float | None = field(default=None)
    completed_at: datetime | None = field(default=None)


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
    
    def remove_after(self, timestamp: datetime, inclusive: bool=True):
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

    def __add__(self, other: List[AgentMessage] | 'AgentMessageList'):
        if isinstance(other, AgentMessageList):
            # If the other object is also an AgentMessageList, extend with its items
            return self._items + other._items
        elif isinstance(other, list):
            # If the other object is a list, just concatenate the lists
            return self._items + other
        else:
            # If the other object is neither, raise an exception
            raise TypeError(f"Unsupported operand type(s) for +: 'AgentMessageList' and '{type(other).__name__}'")

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        return item.id in self._ids

    def __len__(self):
        return len(self._items)
