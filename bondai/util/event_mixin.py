from enum import Enum
from typing import List, Callable


class EventMixin:
    def __init__(self, allowed_events: List[str]):
        # Initialize the dictionary to hold event callbacks with the allowed events
        self._events = {}
        for event in allowed_events:
            if isinstance(event, Enum):
                event = event.value
            self._events[event] = []

    def on(self, event_name: str, target: Callable = None) -> Callable | None:
        """Register a callback to an event."""
        if isinstance(event_name, Enum):
            event_name = event_name.value

        if event_name not in self._events:
            raise ValueError(f"Unsupported event '{event_name}'")

        if target:
            self._events[event_name].append(target)
        else:

            def decorator(callback):
                self._events[event_name].append(callback)
                return callback

            return decorator

    def _trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger the specified event."""
        if isinstance(event_name, Enum):
            event_name = event_name.value

        for callback in self._events.get(event_name, []):
            callback(*args, **kwargs)
