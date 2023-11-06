class EventMixin:
    def __init__(self, allowed_events):
        # Initialize the dictionary to hold event callbacks with the allowed events
        self._events = {event_name: [] for event_name in allowed_events}

    def on(self, event_name):
        """Register a callback to an event."""
        if event_name not in self._events:
            raise ValueError(f"Unsupported event '{event_name}'")

        def decorator(callback):
            self._events[event_name].append(callback)
            return callback
        
        return decorator
    
    def _trigger_event(self, event_name, *args, **kwargs):
        """Trigger the specified event."""
        for callback in self._events.get(event_name, []):
            callback(*args, **kwargs)
