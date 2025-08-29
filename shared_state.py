import threading


class SharedLookDirection:
    def __init__(self):
        self._direction = "center"
        self._lock = threading.Lock()

    def set_direction(self, direction: str):
        with self._lock:
            self._direction = direction

    def get_direction(self) -> str:
        with self._lock:
            return self._direction
