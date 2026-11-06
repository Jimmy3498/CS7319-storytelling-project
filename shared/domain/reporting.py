from ..errors import unfinished
from ..models.gameplay import CommittedTurnNotice
from ..models.reporting import CampaignReport
from ..ports import ReportRepository, SessionRepository


class ReportingService:
    def __init__(self, repository: ReportRepository, sessions: SessionRepository) -> None:
        self.repository = repository
        self.sessions = sessions

    def consume_committed_turn(self, notice: CommittedTurnNotice) -> None:
        """TODO REPORTS: retrieve committed before/after states through authorized internal
        projection; evaluate closed milestone conditions; unique event/consumer + session/marker
        fingerprint prevents double counts. Rejected turns never earn achievements.
        """
        unfinished("REPORTS")

    def report(self, owner_id: str, campaign_id: str, version_id: str | None) -> CampaignReport:
        """TODO REPORTS: authorize campaign owner; aggregate counts, distinct accounts,
        version/marker semantics, explicit denominators and projection freshness. No transcript.
        Failed/rejected attempts are counted separately, not as accepted gameplay.
        """
        unfinished("REPORTS")

    def catch_up(self) -> None:
        """TODO REPORTS: replay pending committed notices, not provider requests. Consumer
        failure does not undo a completed turn or block the result consumer.
        """
        unfinished("REPORTS")
