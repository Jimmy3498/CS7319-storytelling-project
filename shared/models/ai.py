from dataclasses import dataclass, field

from .common import SecretInput
from .world import WorldDefinition


@dataclass(frozen=True)
class ProviderProfile:
    id: str
    owner_id: str
    name: str
    endpoint: str
    model: str
    protocol: str  # Initially chat-completions-compatible; arbitrary provider APIs are not implied.
    configuration_revision: int
    credential_present: bool


@dataclass(frozen=True)
class ProviderCapture:
    """Private per-operation capture. Never serialize into a public receipt/event."""

    profile: ProviderProfile
    credential: SecretInput = field(repr=False)


@dataclass(frozen=True)
class DirectorContext:
    campaign_id: str
    session_id: str
    revision: int
    world: WorldDefinition
    player_input: str


@dataclass(frozen=True)
class VisibleFact:
    id: str
    text: str
    stance: str


@dataclass(frozen=True)
class PlayerView:
    """Built by KnowledgePolicy; renderer accepts this type, never DirectorContext."""

    session_id: str
    revision: int
    player_character_id: str
    facts: tuple[VisibleFact, ...]
    accepted_history: tuple[str, ...]
    player_input: str


@dataclass(frozen=True)
class ProviderMessage:
    role: str
    content: str = field(repr=False)


@dataclass(frozen=True)
class ProviderResponse:
    content: str = field(repr=False)
    input_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None
