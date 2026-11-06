from ..commands import RetryTurn, StartSession, SubmitTurn
from ..errors import unfinished
from ..models.gameplay import AcceptedTurn, SessionSnapshot, TurnAdmission, TurnCommit, TurnProposal
from ..ports import CampaignRepository, SessionRepository


class GameplayService:
    def __init__(self, campaigns: CampaignRepository, sessions: SessionRepository) -> None:
        self.campaigns = campaigns
        self.sessions = sessions

    def start(self, owner_id: str, command: StartSession) -> SessionSnapshot:
        """TODO GAMEPLAY: published version exists, PC is marked playable; materialize an
        isolated session with stable IDs and base revision. No mutation of campaign/other saves.
        """
        unfinished("GAMEPLAY")

    def prepare(
        self, owner_id: str, command: SubmitTurn, operation_id: str, request_id: str
    ) -> TurnAdmission:
        """TODO GAMEPLAY: authorize owner; reject stale revision/empty or over-limit input;
        check durable idempotency receipt before provider work. Capture immutable turn baseline.
        """
        unfinished("GAMEPLAY")

    def validate_and_project(
        self, baseline: SessionSnapshot, proposal: TurnProposal
    ) -> SessionSnapshot:
        """TODO GAMEPLAY: validate closed effect schema, IDs, movement/ownership, stat bounds,
        flags and allowed template spawn conditions. Allocate item IDs in application; no NPC/
        location generation. Produce candidate state only; no persistence or public rendering.
        PRIVACY separately authorizes disclosure requests before constructing player view.
        """
        unfinished("GAMEPLAY")

    def commit(
        self,
        owner_id: str,
        operation_id: str,
        command: SubmitTurn,
        candidate: SessionSnapshot,
        narration: str,
    ) -> TurnCommit:
        """TODO GAMEPLAY: one SQLite compare-and-commit transaction for accepted state,
        player input/narration, receipt and pending completion notice. Never hold SQL transaction
        across provider calls. Duplicate ID returns same receipt; different payload conflicts.
        """
        unfinished("GAMEPLAY")

    def history(self, owner_id: str, session_id: str) -> tuple[AcceptedTurn, ...]:
        """TODO GAMEPLAY: return only this owner's accepted public transcript."""
        unfinished("GAMEPLAY")

    def retry(
        self, owner_id: str, command: RetryTurn, new_operation_id: str
    ) -> SubmitTurn | TurnCommit:
        """TODO GAMEPLAY: inspect prior durable receipt/attempt, preserve input, explicitly link
        retry; committed old operation returns its result, never repeats billing. Unknown remote
        outcome stays visible. Fence late old replies; no automatic paid replay after restart.
        """
        unfinished("GAMEPLAY")

    def record_failure(
        self,
        owner_id: str,
        operation_id: str,
        session_id: str,
        public_code: str,
        provider_uncertain: bool,
    ) -> None:
        """TODO GAMEPLAY: retain failed/rejected attempt separately from accepted history/state."""
        unfinished("GAMEPLAY")
