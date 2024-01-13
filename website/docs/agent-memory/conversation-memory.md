---
sidebar_position: 2
---

# Conversation Memory

Conversation Memory in BondAI, inspired by the [MemGPT paper](https://arxiv.org/pdf/2310.08560.pdf), assists with maintaining a coherent and continuous dialogue with users. It stores the complete history of interactions and messages, allowing agents to reference previous conversations and provide more relevant and personalized responses. This memory layer is crucial for tasks that require recalling past interactions that may no longer fit inside the LLM context window.

# ConversationMemoryDataSource
**bondai.memory.ConversationMemoryDataSource**

The ConversationMemoryDataSource class is an abstract base class in BondAI that defines the interface for conversation memory management. It outlines methods for adding, removing, searching, and clearing conversation messages, facilitating dynamic interaction history management.

```
class ConversationMemoryDataSource(ABC):
    @property
    @abstractmethod
    def messages(self) -> List[AgentMessage]:
        pass

    @abstractmethod
    def add(self, message: AgentMessage):
        pass

    @abstractmethod
    def remove(self, message: AgentMessage):
        pass

    def remove_after(self, timestamp: datetime, inclusive: bool = True):
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        start_date: datetime = None,
        end_date: datetime = None,
        page: int = 0,
    ) -> List[str]:
        pass

    @abstractmethod
    def clear(self):
        pass
```


### Key Features

- **Dynamic Interaction History**: Stores and manages the history of conversations between agents and users.
- **Search Functionality**: Provides methods to search through past messages based on queries or date ranges.
- **Message Management**: Offers functions to add new messages, remove specific messages, and clear the entire history.


# InMemoryConversationMemoryDataSource
**bondai.memory.InMemoryConversationMemoryDataSource**

The InMemoryConversationMemoryDataSource class is an implementation of ConversationMemoryDataSource that stores conversation history in memory. This variant is suitable for temporary or testing environments where persistence of conversation history is not necessary.

```
class InMemoryConversationMemoryDataSource(ConversationMemoryDataSource):
    def __init__(self, page_size=10):
        ...
```

### Usage Example

```python
from bondai.memory.conversation.datasources import InMemoryConversationMemoryDataSource

# Initialize an In-Memory Conversation Memory Data Source
conversation_memory = InMemoryConversationMemoryDataSource()

# Add messages
conversation_memory.add(ConversationMessage(message="My dog's name is Max."))

# Search messages
results = conversation_memory.search('dog')
print(results)
```

### Parameters

- **page_size (int)**: Determines the number of messages to return per page during search operations.


# PersistentConversationMemoryDataSource
**bondai.memory.PersistentConversationMemoryDataSource**

The PersistentConversationMemoryDataSource class offers a persistent approach to storing conversation history. It saves the interaction data to a file, ensuring that conversation history is maintained even after the agent or application restarts.

```
class PersistentConversationMemoryDataSource(InMemoryConversationMemoryDataSource):
    def __init__(
        self, 
        file_path: str = "./.memory/conversation-memory.json", 
        page_size=10
    ):
        ...
```

### Usage Example

```python
from bondai.memory.conversation.datasources import PersistentConversationMemoryDataSource

# Initialize a Persistent Conversation Memory Data Source
persistent_memory = PersistentConversationMemoryDataSource()

# Adding a message automatically saves it disk
persistent_memory.add(ConversationMessage(message="Persistent message"))
```

### Parameters

- **file_path (str)**: Path to the file where conversation history is stored.
- **page_size (int)**: The number of messages to display per page in search results.
