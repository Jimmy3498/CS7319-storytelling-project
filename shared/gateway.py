"""Identical presentation-facing boundary for both architectures."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from .commands import Command
from .models.common import RequestContext
from .queries import Query


class OperationStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    UNIMPLEMENTED = "unimplemented"


@dataclass(frozen=True)
class OperationReceipt:
    operation_id: str
    status: OperationStatus
    message: str
    # Business result DTOs must be authorized before exposure; no raw world/secret captures.
    result: object | None = field(default=None, repr=False)


class ApplicationGateway(Protocol):
    architecture: str

    def submit(
        self, context: RequestContext, command: Command, request_id: str
    ) -> OperationReceipt: ...
    def poll(self, context: RequestContext, operation_id: str) -> OperationReceipt: ...
    def query(self, context: RequestContext, query: Query) -> object: ...
    def close(self) -> None: ...
