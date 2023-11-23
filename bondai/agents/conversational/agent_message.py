import uuid
from enum import Enum
from typing import List, Set
from datetime import datetime
from dataclasses import dataclass, field

USER_MEMBER_NAME = 'user'

class AgentMessageType(Enum):
    AGENT: str = 'AGENT'
    TOOL: str = 'TOOL'

@dataclass
class AgentMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: AgentMessageType = field(default=AgentMessageType.AGENT)
    sender_name: str | None = field(default=None)
    recipient_name: str | None = field(default=None)
    message: str | None = field(default=None)
    response: str | None = field(default=None)
    tool_name: str | None = field(default=None)
    tool_arguments: dict | None = field(default=None)
    success: bool = field(default=False)
    is_conversation_complete: bool = field(default=False)
    error: Exception | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: datetime | None = field(default=None)


class AgentMessageList:
    """
    A custom data structure that stores a list of `AgentMessage` instances while maintaining their order 
    and ensuring uniqueness based on the 'id' attribute of the messages.

    The `AgentMessageList` behaves like a set in that it automatically removes duplicate entries 
    (where a duplicate is defined as having the same 'id'), but it also maintains the insertion order 
    like a list.

    Attributes:
        items (list): The list of unique `AgentMessage` instances.
        ids (set): A set of 'id' attributes to quickly check for uniqueness.

    Methods:
        add(item): Add a unique `AgentMessage` to the list.
        __iter__(): Allow iteration over the `AgentMessageList`.
        __contains__(item): Check if a `AgentMessage` is in the list based on its 'id'.
        __len__(): Return the number of unique messages in the list.

    Usage:
        >>> messages = [AgentMessage(sender_id='123', ...), AgentMessage(sender_id='456', ...)]
        >>> unique_messages = AgentMessageList(messages)
        >>> for message in unique_messages:
        >>>     print(message)

    Note that the constructor can accept an initial list of `AgentMessage` instances, which will be automatically
    de-duped upon creation of the `AgentMessageList` instance.

    The `AgentMessage` class should have an 'id' attribute and ideally is a dataclass for ease of use.
    """
    
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
            self._items = list(sorted(self._items, key=lambda x: x.created_at))
    
    def remove(self, item: AgentMessage):
        if item.id in self._ids:
            self._ids.remove(item.id)
            self._items.remove(item)
    
    def remove_after(self, timestamp: datetime, inclusive: bool=True):
        if inclusive:
            self._items = [item for item in self._items if item.created_at <= timestamp]
        else:
            self._items = [item for item in self._items if item.created_at < timestamp]
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
