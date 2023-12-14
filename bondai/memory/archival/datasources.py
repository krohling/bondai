import os
import json
import numpy as np
import faiss
from typing import List
from abc import ABC, abstractmethod
from bondai.models import EmbeddingModel
from bondai.models.openai import OpenAIEmbeddingModel, OpenAIModelNames


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


class PersistentArchivalMemoryDataSource(ArchivalMemoryDataSource):
    def __init__(
        self,
        file_path: str = "./.memory/archival-memory.json",
        embedding_model: EmbeddingModel | None = None,
        page_size=10,
    ):
        if embedding_model is None:
            embedding_model = OpenAIEmbeddingModel(
                OpenAIModelNames.TEXT_EMBEDDING_ADA_002
            )

        self._file_path = file_path
        self._embedding_model = embedding_model
        self._page_size = page_size
        self._data = self._load_data()
        self._index = faiss.IndexFlatL2(self._embedding_model.embedding_size)
        self._rebuild_index()

    @property
    def size(self) -> int:
        return len(self._data)

    def _load_data(self):
        try:
            with open(self._file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_data(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        with open(self._file_path, "w") as file:
            json.dump(self._data, file, indent=4)

    def _rebuild_index(self):
        self._index = faiss.IndexFlatL2(self._embedding_model.embedding_size)
        if self._data:
            embeddings = np.array([d["embedding"] for d in self._data]).astype(
                "float32"
            )
            self._index.add(embeddings)

    def insert(self, content: str):
        embedding = self._embedding_model.create_embedding(content)
        self._data.append({"content": content, "embedding": embedding})
        self._save_data()
        self._rebuild_index()  # Rebuild the index with the new data

    def insert_bulk(self, content: List[str]):
        embeddings = self._embedding_model.create_embedding(content)
        for i, c in enumerate(content):
            self._data.append({"content": c, "embedding": embeddings[i]})
        self._save_data()
        self._rebuild_index()

    def search(self, query: str, page: int = 0) -> List[str]:
        query_embedding = np.array(
            self._embedding_model.create_embedding(query)
        ).astype("float32")
        _, indices = self._index.search(query_embedding, self._page_size * (page + 1))
        result_indices = indices[0][
            page * self._page_size : (page + 1) * self._page_size
        ]
        return [self._data[i]["content"] for i in result_indices if i < len(self._data)]

    def clear(self):
        self._data = []
        self._save_data()
        self._rebuild_index()


class InMemoryArchivalMemoryDataSource(ArchivalMemoryDataSource):
    def __init__(self, embedding_model: EmbeddingModel | None = None, page_size=10):
        if embedding_model is None:
            embedding_model = OpenAIEmbeddingModel(
                OpenAIModelNames.TEXT_EMBEDDING_ADA_002
            )

        self._embedding_model = embedding_model
        self._page_size = page_size
        self._data = []
        self._embeddings = []
        self._index = faiss.IndexFlatL2(self._embedding_model.embedding_size)

    @property
    def size(self) -> int:
        return len(self._data)

    def insert(self, content: str):
        embedding = np.array(self._embedding_model.create_embedding(content)).astype(
            "float32"
        )
        self._data.append(content)
        self._embeddings.append(embedding)
        self._rebuild_index()

    def insert_bulk(self, content: List[str]):
        content_embeddings = np.array(
            self._embedding_model.create_embedding(content)
        ).astype("float32")

        for i, c in enumerate(content):
            self._data.append(c)
            self._embeddings.append(content_embeddings[i])

        self._rebuild_index()

    def _rebuild_index(self):
        self._index = faiss.IndexFlatL2(self._embedding_model.embedding_size)
        if self._data:
            embeddings = np.array(self._embeddings).astype("float32")
            self._index.add(embeddings)

    def search(self, query: str, page: int = 0) -> List[str]:
        print(f"Searching archival memory for: {query}")
        query_embedding = np.array(
            self._embedding_model.create_embedding(query)
        ).astype("float32")
        start_idx = (
            page * self._page_size
        )  # Calculate the starting index for the current page
        end_idx = (
            start_idx + self._page_size
        )  # Calculate the ending index for the current page

        # Fetch results for the specific page
        _, indices = self._index.search(query_embedding, end_idx)

        # Return the slice of results for the current page
        results = [self._data[i] for i in indices[0][start_idx:end_idx]]
        return results

    def clear(self):
        self._data = []
        self._embeddings = []
        self._rebuild_index()
