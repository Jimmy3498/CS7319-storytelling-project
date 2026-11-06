"""Private workflow context port. Do not broadcast full frames in messages."""

from dataclasses import dataclass

from shared.commands import SubmitTurn
from shared.errors import unfinished
from shared.models.ai import PlayerView, ProviderCapture
from shared.models.common import RequestContext
from shared.models.gameplay import SessionSnapshot, TurnProposal


@dataclass(frozen=True)
class TurnWork:
    context: RequestContext
    command: SubmitTurn
    baseline: SessionSnapshot
    capture: ProviderCapture
    proposal: TurnProposal | None = None
    candidate: SessionSnapshot | None = None


@dataclass(frozen=True)
class NarrationWork:
    view: PlayerView
    capture: ProviderCapture


class WorkflowStateStore:
    def retain_turn(self, operation_id: str, work: TurnWork) -> str:
        """TODO EVENTS: bounded owner-scoped worker state; opaque work reference. Secrets
        stay in process/private credential storage, not durable public event payloads.
        """
        unfinished("EVENTS")

    def private_turn(self, reference: str, context: RequestContext) -> TurnWork:
        """TODO EVENTS: authorize stage and owner; for planner/validator/committer only."""
        unfinished("EVENTS")

    def narration(self, reference: str, context: RequestContext) -> NarrationWork:
        """TODO EVENTS: exact player-scoped projection, not a full TurnWork frame."""
        unfinished("EVENTS")

    def release(self, operation_id: str) -> None:
        """TODO EVENTS: terminal cleanup, cancel/failure handling; no restart paid replay."""
        unfinished("EVENTS")
