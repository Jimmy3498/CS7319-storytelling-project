from ..commands import AdoptCampaignUpdate
from ..errors import unfinished
from ..models.gameplay import MergePreview, SessionSnapshot
from ..ports import CampaignRepository, SessionRepository


class UpdateService:
    def __init__(self, campaigns: CampaignRepository, sessions: SessionRepository) -> None:
        self.campaigns = campaigns
        self.sessions = sessions

    def preview(self, owner_id: str, session_id: str, target_version_id: str) -> MergePreview:
        """TODO MERGE: three-way comparison old base/new base/current state, stable IDs.
        Carry session-created items and progress. Non-overlap still needs whole-state/reference
        validation. Conflicts or deletion of referenced objects block the complete adoption.
        Internal candidate/conflict detail must be filtered before player-facing display.
        """
        unfinished("MERGE")

    def adopt(
        self, owner_id: str, operation_id: str, command: AdoptCampaignUpdate
    ) -> SessionSnapshot:
        """TODO MERGE: recompute/validate preview, retain immutable pre-update checkpoint,
        recheck session revision, atomically adopt whole candidate + new base reference.
        On conflict leave state/version/history unchanged. No automatic smart merge or edits
        to old published snapshots; absence of adoption merely leaves update-available notice.
        """
        unfinished("MERGE")
