from collections import deque
from threading import Lock

from ..errors import ApplicationError, ErrorCode, unfinished
from ..models.ai import ProviderCapture, ProviderMessage, ProviderResponse


class CompatibleHttpProvider:
    mode = "real-unimplemented"

    def complete(
        self, messages: tuple[ProviderMessage, ...], capture: ProviderCapture
    ) -> ProviderResponse:
        """TODO PROVIDER: HTTPS or explicit loopback HTTP full chat-completions endpoint;
        Bearer credential only in outbound headers; model/messages from captured configuration.
        Bounded connect/read timeout and response size; parse status/choices/usage explicitly.
        No key in logs, no automatic paid retry or fallback to mock, no calls during card edits.
        """
        unfinished("PROVIDER")


class ScriptedTestProvider:
    """Return supplied responses in order for deterministic tests."""

    mode = "scripted-test-double"

    def __init__(self, responses: tuple[ProviderResponse, ...]) -> None:
        self._responses = deque(responses)
        self._lock = Lock()
        self.calls = 0

    def complete(
        self, messages: tuple[ProviderMessage, ...], capture: ProviderCapture
    ) -> ProviderResponse:
        with self._lock:
            if not self._responses:
                raise ApplicationError(ErrorCode.PROVIDER, "Test-provider script exhausted")
            self.calls += 1
            return self._responses.popleft()
