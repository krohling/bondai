import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class AgentMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_name: str
    recipient_name: str
    message: str
    response_id: str
    success: bool
    error_message: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: datetime


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
    
    def __init__(self, messages=None):
        self.items = []
        self.ids = set()
        if messages:
            for message in messages:
                self.add(message)

    def add(self, item):
        if item.id not in self.ids:
            self.items.append(item)
            self.ids.add(item.id)

    def union(self, messages):
        return AgentMessageList(self.items + messages)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item):
        return item.id in self.ids

    def __len__(self):
        return len(self.items)
