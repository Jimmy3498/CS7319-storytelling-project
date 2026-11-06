"""Public, payload-free failure vocabulary. Stubs never report business success."""

from enum import StrEnum


class ErrorCode(StrEnum):
    NOT_IMPLEMENTED = "not_implemented"
    UNAUTHENTICATED = "unauthenticated"
    FORBIDDEN = "forbidden"
    INVALID = "invalid"
    CONFLICT = "conflict"
    PROVIDER = "provider_failed"
    PROVIDER_UNCERTAIN = "provider_outcome_uncertain"
    STORAGE = "storage_failed"
    INTERNAL = "internal_error"


class ApplicationError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.public_message = message


class FeatureNotImplemented(ApplicationError):
    def __init__(self, work_item: str) -> None:
        super().__init__(ErrorCode.NOT_IMPLEMENTED, f"Unimplemented work item: {work_item}")
        self.work_item = work_item


def unfinished(work_item: str) -> None:
    raise FeatureNotImplemented(work_item)
