import os
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

class ConversationMemoryDataSource(ABC):

    @property
    @abstractmethod
    def messages(self) -> List[str]:
        pass

    @abstractmethod
    def search(self, query: str, start_date: datetime = None, end_date: datetime = None, page: int = 0) -> List[str]:
        pass


class JSONConversationMemoryDataSource(ConversationMemoryDataSource):
    def __init__(self, file_path: str = './.memory/conversation-memory.json', page_size = 10):
        self._file_path = file_path
        self._page_size = page_size
        self._data = self._load_data()

    def _load_data(self):
        try:
            with open(self._file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_data(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        with open(self._file_path, 'w') as file:
            json.dump(self._data, file, indent=4)

    @property
    def messages(self) -> List[str]:
        return [message['content'] for message in self._data]

    def add_message(self, content: str) -> None:
        message = {
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self._data.append(message)
        self._save_data()

    def search(self, query: str, start_date: datetime = None, end_date: datetime = None, page: int = 0) -> List[str]:
        results = []
        for message in self._data:
            timestamp = datetime.fromisoformat(message['timestamp'])
            if (not start_date or timestamp >= start_date) and (not end_date or timestamp <= end_date):
                if query.lower() in message['content'].lower():
                    results.append(message['content'])

        # Implementing a simple pagination
        start_index = page * self._page_size
        end_index = start_index + self._page_size
        return results[start_index:end_index]


class InMemoryConversationMemoryDataSource(ConversationMemoryDataSource):
    def __init__(self, page_size = 10):
        self._page_size = page_size
        self._data = []

    @property
    def messages(self) -> List[str]:
        return [message['content'] for message in self._data]

    def add_message(self, content: str) -> None:
        message = {
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self._data.append(message)

    def search(self, query: str, start_date: datetime = None, end_date: datetime = None, page: int = 0) -> List[str]:
        results = []
        for message in self._data:
            timestamp = datetime.fromisoformat(message['timestamp'])
            if (not start_date or timestamp >= start_date) and (not end_date or timestamp <= end_date):
                if query.lower() in message['content'].lower():
                    results.append(message['content'])

        # Implementing a simple pagination
        start_index = page * self._page_size
        end_index = start_index + self._page_size
        return results[start_index:end_index]