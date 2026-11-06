"""In-process event queue; one worker dispatches registered subscribers sequentially."""

from collections import defaultdict
from queue import Empty, Queue
from threading import Event, Lock, Thread, current_thread
from typing import Callable

from .messages import Message, Topic

Handler = Callable[[Message], None]
ErrorHandler = Callable[[Message, str, Exception], None]


class InProcessBus:
    def __init__(self, on_error: ErrorHandler) -> None:
        self._queue: Queue[Message] = Queue()
        self._subscriptions: dict[Topic, list[tuple[str, Handler]]] = defaultdict(list)
        self._on_error = on_error
        self._stop = Event()
        self._thread: Thread | None = None
        self._lock = Lock()
        self.trace: list[tuple[str, str, str]] = []  # topic, component, operation ID only.

    def subscribe(self, topic: Topic, component: str, handler: Handler) -> None:
        with self._lock:
            if self._thread is not None:
                raise RuntimeError("Register handlers before starting the bus")
            if any(name == component for name, _ in self._subscriptions[topic]):
                raise ValueError("Duplicate component subscription")
            self._subscriptions[topic].append((component, handler))

    @property
    def subscriptions(self) -> dict[Topic, tuple[str, ...]]:
        with self._lock:
            return {
                topic: tuple(name for name, _ in entries)
                for topic, entries in self._subscriptions.items()
            }

    @property
    def pending(self) -> int:
        return self._queue.qsize()

    def publish(self, message: Message) -> None:
        with self._lock:
            if self._stop.is_set():
                raise RuntimeError("Bus is closed")
            self._queue.put(message)

    def _report_error(self, message: Message, component: str, error: Exception) -> None:
        try:
            self._on_error(message, component, error)
        except Exception:
            # A broken diagnostic/status callback must not kill the other subscribers.
            # Retain metadata only, never the exception text or private command.
            self.trace.append(
                (message.topic.value, component + ":error-callback", message.operation_id)
            )

    def dispatch_one(self, timeout: float = 0.0) -> bool:
        if self._stop.is_set():
            return False
        try:
            message = self._queue.get(timeout=timeout)
        except Empty:
            return False
        try:
            handlers = tuple(self._subscriptions.get(message.topic, ()))
            if not handlers:
                self._report_error(message, "router", ValueError("No registered handler"))
            for component, handler in handlers:
                self.trace.append((message.topic.value, component, message.operation_id))
                try:
                    handler(message)
                except Exception as error:
                    self._report_error(message, component, error)
        finally:
            self._queue.task_done()
        return True

    def start(self) -> None:
        with self._lock:
            if self._stop.is_set():
                raise RuntimeError("Bus is closed")
            if self._thread is None:
                self._thread = Thread(target=self._run, name="cs7319-event-worker", daemon=True)
                self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            self.dispatch_one(timeout=0.1)

    def close(self) -> None:
        with self._lock:
            self._stop.set()
        thread = self._thread
        if thread and thread is not current_thread():
            thread.join(timeout=2)
        while True:
            try:
                message = self._queue.get_nowait()
            except Empty:
                break
            self._report_error(message, "shutdown", RuntimeError("Queue closed before dispatch"))
            self._queue.task_done()
