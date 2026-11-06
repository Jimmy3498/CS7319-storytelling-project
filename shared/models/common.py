from dataclasses import dataclass, field
from enum import StrEnum


@dataclass(frozen=True)
class SecretInput:
    value: str = field(repr=False)

    def __repr__(self) -> str:
        return "SecretInput(<redacted>)"


@dataclass(frozen=True)
class RequestContext:
    """Server-authenticated user identity must be established by AUTH, never a widget."""

    client_session_id: str
    user_id: str | None
    correlation_id: str
    request_id: str | None = None  # Gateway binds the explicit submission ID before dispatch.


class Visibility(StrEnum):
    PUBLIC = "public"
    DIRECTOR = "director"
    CHARACTER = "character"


@dataclass(frozen=True)
class Access:
    # Deliberately no default-to-public. CHARACTER requires character_ids.
    visibility: Visibility
    character_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.visibility, Visibility):
            raise ValueError("Explicit typed visibility is required")
        if not isinstance(self.character_ids, tuple):
            raise ValueError("Reader IDs must be an immutable tuple")
        if self.visibility is Visibility.CHARACTER:
            if not self.character_ids or len(set(self.character_ids)) != len(self.character_ids):
                raise ValueError("Character-private scope requires unique explicit readers")
            if any(not isinstance(value, str) or not value.strip() for value in self.character_ids):
                raise ValueError("Invalid reader identity")
        elif self.character_ids:
            raise ValueError("Public/Director scope must not mix character readers")


class ConditionKind(StrEnum):
    AT_LOCATION = "at_location"
    OWNS_ITEM = "owns_item"
    FLAG_EQUALS = "flag_equals"


@dataclass(frozen=True)
class Condition:
    """Small closed condition menu, not a script or natural-language rule interpreter."""

    kind: ConditionKind
    target_id: str
    expected: bool = True


@dataclass(frozen=True)
class Issue:
    path: str
    code: str
    message: str
