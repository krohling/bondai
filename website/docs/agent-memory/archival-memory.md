---
sidebar_position: 3
---

# Archival Memory

Archival Memory in BondAI, inspired by the [MemGPT paper](https://arxiv.org/pdf/2310.08560.pdf), represents an advanced memory layer that enables semantic search over a virtually infinite memory space. It utilizes embeddings and the faiss library to store and retrieve large volumes of data, making it particularly suitable for extensive historical information, comprehensive data sets, and long-term memory retention. This memory layer allows BondAI agents to access information beyond the immediate conversation or core memory.

# ArchivalMemoryDataSource
**bondai.memory.ArchivalMemoryDataSource**

The ArchivalMemoryDataSource class is an abstract base class defining the interface for archival memory. It allows for the insertion of content and provides a semantic search mechanism to retrieve relevant information based on query embeddings.

```
class ArchivalMemoryDataSource(ABC):
    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def insert(self, content: str):
        pass

    @abstractmethod
    def insert_bulk(self, content: List[str]):
        pass

    @abstractmethod
    def search(self, query: str, page: int = 0) -> List[str]:
        pass

    @abstractmethod
    def clear(self):
        pass
```


### Key Features

- **Semantic Search**: Leverages embeddings for deep semantic search, offering precise and relevant results.
- **Vast Memory Capacity**: Suitable for large-scale data storage, effectively handling extensive information.
- **Dynamic Data Management**: Supports insertion, bulk insertion, and deletion of memory content.


# InMemoryArchivalMemoryDataSource
**bondai.memory.InMemoryArchivalMemoryDataSource**

The InMemoryArchivalMemoryDataSource class provides an in-memory implementation of ArchivalMemoryDataSource. This variant is designed for temporary storage and fast access to archival data, primarily used in testing or non-persistent applications.

```
class InMemoryArchivalMemoryDataSource(ArchivalMemoryDataSource):
    def __init__(self, embedding_model: EmbeddingModel | None = None, page_size=10):
        ...
```

### Usage Example

```python
from bondai.memory.archival.datasources import InMemoryArchivalMemoryDataSource
from bondai.models.openai import OpenAIEmbeddingModel, OpenAIModelNames

# Initialize an In-Memory Archival Memory Data Source
in_memory_archival = InMemoryArchivalMemoryDataSource(
    embedding_model=OpenAIEmbeddingModel(OpenAIModelNames.TEXT_EMBEDDING_ADA_002)
)

# Insert and search content
in_memory_archival.insert("Temporary archival data")
results = in_memory_archival.search("archival data")
print(results)
```

### Parameters

- **embedding_model**: (EmbeddingModel): Model used for creating content embeddings.
- **page_size (int)**: Number of search results returned per page.


# PersistentArchivalMemoryDataSource
**bondai.memory.PersistentArchivalMemoryDataSource**

PersistentArchivalMemoryDataSource is a concrete implementation of ArchivalMemoryDataSource. It stores data persistently, ensuring the archival memory is retained across sessions. 

```
class PersistentArchivalMemoryDataSource(ArchivalMemoryDataSource):
    def __init__(
        self,
        file_path: str = "./.memory/archival-memory.json",
        embedding_model: EmbeddingModel | None = None,
        page_size=10,
    ):
        ...
```

### Usage Example

```python
from bondai.memory.archival.datasources import PersistentArchivalMemoryDataSource
from bondai.models.openai import OpenAIEmbeddingModel, OpenAIModelNames

# Initialize a Persistent Archival Memory Data Source
archival_memory = PersistentArchivalMemoryDataSource(
    embedding_model=OpenAIEmbeddingModel(OpenAIModelNames.TEXT_EMBEDDING_ADA_002)
)

# Insert and search content
archival_memory.insert("Historical data on global trends")
results = archival_memory.search("global trends")
print(results)
```

### Parameters

- **file_path (str)**: File path for storing archival memory data.
- **embedding_model (EmbeddingModel)**: Model used for creating content embeddings.
- **page_size (int)**: Number of search results returned per page.
