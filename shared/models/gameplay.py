from dataclasses import dataclass
from enum import StrEnum

from .common import Issue
from .world import WorldDefinition


class EffectKind(StrEnum):
    MOVE_CHARACTER = "move_character"
    TRANSFER_ITEM = "transfer_item"
    CHANGE_STAT = "change_stat"
    CHANGE_RELATIONSHIP_STAT = "change_relationship_stat"
    SET_FLAG = "set_flag"
    REQUEST_DISCLOSURE = "request_disclosure"
    CREATE_ITEM = "create_item"


@dataclass(frozen=True)
class Effect:
    """Closed fields: no arbitrary prose, entity schemas, files or commands in effects.

    Fields permitted per kind are specified in docs/CONTRACTS.md. Invalid extra values reject.
    CREATE_ITEM uses template_id; the application allocates the new instance ID.
    """

    kind: EffectKind
    actor_id: str
    target_id: str | None = None
    destination_id: str | None = None
    stat_id: str | None = None
    delta: float | None = None
    enabled: bool | None = None
    template_id: str | None = None


@dataclass(frozen=True)
class SessionSnapshot:
    id: str
    owner_id: str
    campaign_id: str
    base_version_id: str
    revision: int
    player_character_id: str
    world: WorldDefinition
    disclosed_ids: tuple[str, ...]  # Authorized TextRecord or item-instance IDs, not blanket scope.
    flag_values: tuple[
        tuple[str, bool], ...
    ]  # Current values; FlagDefinition.initial stays authored.


@dataclass(frozen=True)
class TurnProposal:
    expected_revision: int
    effects: tuple[Effect, ...]
    public_fact_ids: tuple[str, ...]
    # Planner prose is intentionally absent from the public handoff.


@dataclass(frozen=True)
class AcceptedTurn:
    id: str
    session_id: str
    operation_id: str
    revision: int
    player_input: str
    narration: str


@dataclass(frozen=True)
class CommittedTurnNotice:
    """IDs only; subscribers retrieve authorized projections instead of private world blobs."""

    event_id: str
    operation_id: str
    session_id: str
    campaign_id: str
    base_version_id: str
    revision: int


@dataclass(frozen=True)
class TurnCommit:
    turn: AcceptedTurn
    notice: CommittedTurnNotice


@dataclass(frozen=True)
class TurnAdmission:
    """Exactly one branch: fresh baseline OR previously committed result; never regenerate the latter."""

    baseline: SessionSnapshot | None
    previous_commit: TurnCommit | None

    def __post_init__(self) -> None:
        if (self.baseline is None) == (self.previous_commit is None):
            raise ValueError("Admission requires exactly one fresh or committed branch")


@dataclass(frozen=True)
class MergeConflict:
    entity_id: str
    field: str
    reason: str


@dataclass(frozen=True)
class MergePreview:
    session_id: str
    expected_session_revision: int
    old_version_id: str
    target_version_id: str
    conflicts: tuple[MergeConflict, ...]
    issues: tuple[Issue, ...]
    candidate: SessionSnapshot | None


@dataclass(frozen=True)
class SessionSummary:
    id: str
    campaign_title: str
    base_version_id: str
    revision: int
    update_available: bool
