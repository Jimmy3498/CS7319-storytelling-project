"""Process-local operation receipts.

Keep raw commands, credentials, provider captures and provider messages out of stored receipts.
TODO PERSISTENCE: replace transient receipts with durable, authenticated records.
"""

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, replace
from threading import Lock
from uuid import uuid4

from .commands import Command
from .errors import ApplicationError, ErrorCode, FeatureNotImplemented
from .gateway import OperationReceipt, OperationStatus
from .models.common import RequestContext


class OperationStatusStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._receipts: dict[str, OperationReceipt] = {}
        self._owners: dict[str, tuple[str, str | None]] = {}
        self._requests: dict[tuple[str, str | None, str], str] = {}
        self._fingerprints: dict[tuple[str, str | None, str], str] = {}
        self._fingerprint_key = secrets.token_bytes(32)

    @staticmethod
    def _owner(context: RequestContext) -> tuple[str, str | None]:
        return context.client_session_id, context.user_id

    def begin(
        self, context: RequestContext, request_id: str, command: Command
    ) -> tuple[OperationReceipt, bool]:
        if not request_id or not context.client_session_id:
            raise ApplicationError(ErrorCode.INVALID, "Request and client-session IDs are required")
        # Compare requests with a keyed digest instead of storing their contents.
        payload = json.dumps(
            {"type": type(command).__name__, "data": asdict(command)},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        fingerprint = hmac.new(self._fingerprint_key, payload, hashlib.sha256).hexdigest()
        key = (*self._owner(context), request_id)
        with self._lock:
            if key in self._requests:
                if not hmac.compare_digest(self._fingerprints[key], fingerprint):
                    raise ApplicationError(
                        ErrorCode.CONFLICT, "Request ID reused with different command data"
                    )
                return self._receipts[self._requests[key]], False
            operation_id = str(uuid4())
            receipt = OperationReceipt(
                operation_id, OperationStatus.PENDING, "Queued scaffold operation"
            )
            self._receipts[operation_id] = receipt
            self._owners[operation_id] = self._owner(context)
            self._requests[key] = operation_id
            self._fingerprints[key] = fingerprint
            return receipt, True

    def read(self, context: RequestContext, operation_id: str) -> OperationReceipt:
        with self._lock:
            if self._owners.get(operation_id) != self._owner(context):
                raise ApplicationError(
                    ErrorCode.FORBIDDEN, "Operation is not in this client/account scope"
                )
            return self._receipts[operation_id]

    def update(
        self, operation_id: str, status: OperationStatus, message: str, result: object = None
    ) -> OperationReceipt:
        with self._lock:
            current = self._receipts[operation_id]
            value = replace(current, status=status, message=message, result=result)
            self._receipts[operation_id] = value
            return value

    def fail(self, operation_id: str, error: Exception) -> OperationReceipt:
        if isinstance(error, FeatureNotImplemented):
            return self.update(operation_id, OperationStatus.UNIMPLEMENTED, error.public_message)
        if isinstance(error, ApplicationError):
            state = (
                OperationStatus.REJECTED
                if error.code
                in {
                    ErrorCode.INVALID,
                    ErrorCode.CONFLICT,
                    ErrorCode.FORBIDDEN,
                    ErrorCode.UNAUTHENTICATED,
                }
                else OperationStatus.FAILED
            )
            return self.update(operation_id, state, error.public_message)
        # Do not expose arbitrary exception text, payloads, secrets or raw responses.
        return self.update(
            operation_id, OperationStatus.FAILED, "Internal failure; inspect sanitized diagnostics"
        )
