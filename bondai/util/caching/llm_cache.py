import os
import json
import hashlib
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional


class LLMCache(ABC):
    def _get_cache_key(self, input_parameters: Dict) -> str:
        key_str = json.dumps(input_parameters, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    @abstractmethod
    def get_cache_item(self, input_parameters: Dict) -> Optional[Tuple[str, Dict]]:
        pass

    @abstractmethod
    def save_cache_item(self, input_parameters: Dict, response: (str, Dict)) -> None:
        pass


class PersistentLLMCache(LLMCache):
    def __init__(self, cache_dir: str = "./.cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get_cache_item(self, input_parameters: Dict) -> Optional[Tuple[str, Dict]]:
        cache_key = self._get_cache_key(input_parameters=input_parameters)
        cache_path = os.path.join(self.cache_dir, cache_key)

        if os.path.exists(cache_path):
            with open(cache_path, "r") as file:
                return json.load(file)

    def save_cache_item(self, input_parameters: Dict, response: (str, Dict)) -> None:
        print(input_parameters)
        print(response)
        cache_key = self._get_cache_key(input_parameters=input_parameters)
        print(cache_key)
        cache_path = os.path.join(self.cache_dir, cache_key)
        print(cache_path)

        with open(cache_path, "w") as file:
            json.dump(response, file)


class InMemoryLLMCache(LLMCache):
    def __init__(self):
        self.cache = {}

    def get_cache_item(self, input_parameters: Dict) -> Optional[Tuple[str, Dict]]:
        cache_key = self._get_cache_key(input_parameters=input_parameters)

        # Return the cached item if it exists
        return self.cache.get(cache_key)

    def save_cache_item(self, input_parameters: Dict, response: (str, Dict)) -> None:
        cache_key = self._get_cache_key(input_parameters=input_parameters)

        # Save the response to the cache
        self.cache[cache_key] = response
