from abc import ABC
from typing import List, Callable, Tuple
import threading


class Runnable(ABC):
    def __init__(self):
        self._force_stop: bool = False
        self._execution_thread = None

    def _start_execution_thread(self, target: Callable, args: Tuple = ()):
        if self._execution_thread and self._execution_thread.is_alive():
            raise Exception("Execution Thread is already running")

        self._execution_thread = threading.Thread(target=target, args=args)
        self._execution_thread.start()

    def join(self, timeout=None):
        """Blocks until the thread completes."""
        if self._execution_thread and self._execution_thread.is_alive():
            self._execution_thread.join(timeout)

    def stop(self, timeout=10):
        """Gracefully stops the thread, with a timeout."""
        self._force_stop = True
        if self._execution_thread and self._execution_thread.is_alive():
            self._execution_thread.join(timeout)
            if self._execution_thread.is_alive():
                # The thread is still alive after the timeout, so kill it.
                self._execution_thread.terminate()

        self._force_stop = False
