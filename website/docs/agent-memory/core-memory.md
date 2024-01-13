---
sidebar_position: 1
---

# Core Memory

Core Memory in BondAI, inspired by the [MemGPT paper](https://arxiv.org/pdf/2310.08560.pdf), serves as a primary memory layer for retaining and accessing critical information relevant to an agent's ongoing tasks and user interactions. It acts as a dynamic, accessible storage that agents use to maintain continuity and context in their activities. The data stored in Core Memory is always available to the Agent via the system prompt. As such, it is important that the amount of information stored in Core Memory is limited. When using a CoreMemoryDataSource with a [MemoryManager](./memory-manager.md), Agents are automatically given access to a set of tools that allow editing of their Core Memory. By leveraging Core Memory, BondAI agents can maintain an understanding of the user's needs and preferences, adapt to changing requirements, and provide more personalized and effective responses

# CoreMemoryDataSource
**bondai.memory.CoreMemoryDataSource**

The CoreMemoryDataSource class in BondAI is an abstract class that describes the interface for managing core memory. It defines the structure and methods that any concrete core memory data source must implement. This makes implementation of custom DataSources straightforward (i.e. Databases).

```
class CoreMemoryDataSource(ABC):
    @property
    @abstractmethod
    def sections(self) -> List[str]:
        pass

    @abstractmethod
    def get(self, section: str) -> str:
        pass

    @abstractmethod
    def set(self, section: str, content: str) -> None:
        pass
```


## Key Features

- **Sectioned Memory**: Divides memory into sections for organized storage and retrieval.
- **Persistent and In-Memory Variants**: Offers flexibility in memory persistence, catering to different operational needs.
- **Memory Management**: Agents can interact with Core Memory via get/set tools, allowing them to store and retrieve task-relevant data.


# InMemoryCoreMemoryDataSource
**bondai.memory.InMemoryCoreMemoryDataSource**

The InMemoryCoreMemoryDataSource class in BondAI is an implementation of the CoreMemoryDataSource interface that stores core memory data in memory. This class is suitable for scenarios where persistent storage of memory data is not required, such as temporary or test environments.

```
class InMemoryCoreMemoryDataSource(CoreMemoryDataSource):
    def __init__(
        self, 
        sections: Dict[str, str] | None = None, 
        max_section_size: int = 1024
    ):
```

## Usage Example

```python
from bondai.memory.core.datasources import InMemoryCoreMemoryDataSource

# Initialize an In-Memory Core Memory Data Source
core_memory = InMemoryCoreMemoryDataSource({
    "user": "Name is George. Lives in New York. Has a dog named Max."
})

print(core_memory.get('user'))
```

## Parameters

- **sections (Dict[str, str])**: A dictionary specifying the initial sections and their content.
- **max_section_size (int)**: The maximum size of content that can be stored in each section.


# PersistentCoreMemoryDataSource
**bondai.memory.PersistentCoreMemoryDataSource**

The PersistentCoreMemoryDataSource class is a concrete implementation of CoreMemoryDataSource in BondAI that provides persistent storage for core memory data, allowing the information to be retained across different sessions and agent restarts.

```
class PersistentCoreMemoryDataSource(CoreMemoryDataSource):
    def __init__(
        self,
        file_path: str = "./.memory/core-memory.json",
        sections: Dict[str, str] | None = None,
        max_section_size: int = 1024,
    ):
```

## Usage Example

```python
from bondai.memory.core.datasources import PersistentCoreMemoryDataSource

# Initialize a Persistent Core Memory Data Source
core_memory = PersistentCoreMemoryDataSource()

# Set and retrieve data from a specific section
core_memory.set('user', 'User information')
print(core_memory.get('user'))
```

## Parameters

- **file_path (str)**: The file path where the core memory data is stored.
- **sections (Dict[str, str])**: A dictionary specifying the initial sections and their content.
- **max_section_size (int)**: The maximum size of content that can be stored in each section.

