"""Typed repository shells. See schema.sql and docs/CONTRACTS.md for transaction boundaries.
No database is opened by this scaffold. Implement ownership and compare-and-commit here.
"""

from __future__ import annotations

from pathlib import Path

from ..errors import FeatureNotImplemented
from ..models.accounts import AccountView
from ..models.ai import ProviderProfile
from ..models.gameplay import (
    AcceptedTurn,
    CommittedTurnNotice,
    SessionSnapshot,
    SessionSummary,
    TurnAdmission,
    TurnCommit,
)
from ..models.reporting import CampaignReport
from ..models.views import CampaignSummary
from ..models.world import (
    CampaignContent,
    CampaignDraft,
    CatalogEntry,
    EditorProposal,
    PublishedCampaign,
)


class SQLiteStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def create_account(self, username: str, password_hash: str) -> AccountView:
        raise FeatureNotImplemented("PERSISTENCE")

    def credential_record(self, username: str) -> tuple[AccountView, str] | None:
        raise FeatureNotImplemented("PERSISTENCE")

    def establish_login(self, account_id: str, client_session_id: str) -> str:
        raise FeatureNotImplemented("PERSISTENCE")

    def resolve_login(self, client_session_id: str) -> AccountView | None:
        raise FeatureNotImplemented("PERSISTENCE")

    def end_login(self, client_session_id: str) -> None:
        raise FeatureNotImplemented("PERSISTENCE")

    def create_campaign(self, owner_id: str, title: str, summary: str) -> CampaignDraft:
        raise FeatureNotImplemented("PERSISTENCE")

    def load_draft(self, owner_id: str, campaign_id: str) -> CampaignDraft:
        raise FeatureNotImplemented("PERSISTENCE")

    def save_draft(
        self, owner_id: str, campaign_id: str, expected_revision: int, content: CampaignContent
    ) -> CampaignDraft:
        raise FeatureNotImplemented("PERSISTENCE")

    def publish(self, owner_id: str, campaign_id: str, expected_revision: int) -> PublishedCampaign:
        raise FeatureNotImplemented("PERSISTENCE")

    def published(self, version_id: str) -> PublishedCampaign:
        raise FeatureNotImplemented("PERSISTENCE")

    def catalog(self) -> tuple[CatalogEntry, ...]:
        raise FeatureNotImplemented("PERSISTENCE")

    def start_session(
        self, owner_id: str, campaign: PublishedCampaign, pc_id: str
    ) -> SessionSnapshot:
        raise FeatureNotImplemented("PERSISTENCE")

    def load_session(self, owner_id: str, session_id: str) -> SessionSnapshot:
        raise FeatureNotImplemented("PERSISTENCE")

    def commit_turn(
        self,
        owner_id: str,
        operation_id: str,
        expected_revision: int,
        candidate: SessionSnapshot,
        player_input: str,
        narration: str,
    ) -> TurnCommit:
        raise FeatureNotImplemented("PERSISTENCE")

    def accepted_history(self, owner_id: str, session_id: str) -> tuple[AcceptedTurn, ...]:
        raise FeatureNotImplemented("PERSISTENCE")

    def adopt_update(
        self, owner_id: str, operation_id: str, expected_revision: int, candidate: SessionSnapshot
    ) -> SessionSnapshot:
        raise FeatureNotImplemented("PERSISTENCE")

    def record_attempt_failure(
        self,
        owner_id: str,
        operation_id: str,
        session_id: str,
        public_code: str,
        uncertain_provider_outcome: bool,
    ) -> None:
        raise FeatureNotImplemented("PERSISTENCE")

    def pending_notifications(self) -> tuple[CommittedTurnNotice, ...]:
        raise FeatureNotImplemented("PERSISTENCE")

    def acknowledge_notification(self, consumer: str, event_id: str) -> None:
        raise FeatureNotImplemented("PERSISTENCE")

    def list_profiles(self, owner_id: str) -> tuple[ProviderProfile, ...]:
        raise FeatureNotImplemented("PERSISTENCE")

    def active_profile(self, owner_id: str) -> ProviderProfile:
        raise FeatureNotImplemented("PERSISTENCE")

    def credential_reference(self, owner_id: str, profile_id: str, revision: int) -> str:
        raise FeatureNotImplemented("PERSISTENCE")

    def apply_committed_notice(self, notice: CommittedTurnNotice) -> None:
        raise FeatureNotImplemented("PERSISTENCE")

    def campaign_report(
        self, owner_id: str, campaign_id: str, version_id: str | None
    ) -> CampaignReport:
        raise FeatureNotImplemented("PERSISTENCE")

    def save_editor_proposal(self, owner_id: str, proposal: EditorProposal) -> None:
        raise FeatureNotImplemented("PERSISTENCE")

    def load_editor_proposal(self, owner_id: str, proposal_id: str) -> EditorProposal:
        raise FeatureNotImplemented("PERSISTENCE")

    def drafts_for_owner(self, owner_id: str) -> tuple[CampaignSummary, ...]:
        raise FeatureNotImplemented("PERSISTENCE")

    def sessions_for_owner(self, owner_id: str) -> tuple[SessionSummary, ...]:
        raise FeatureNotImplemented("PERSISTENCE")

    def save_profile(
        self,
        owner_id: str,
        profile: ProviderProfile,
        expected_revision: int | None,
        credential_reference: str | None,
    ) -> ProviderProfile:
        raise FeatureNotImplemented("PERSISTENCE")

    def activate_profile(
        self, owner_id: str, profile_id: str, expected_revision: int
    ) -> ProviderProfile:
        raise FeatureNotImplemented("PERSISTENCE")

    def delete_profile(
        self,
        owner_id: str,
        profile_id: str,
        expected_revision: int,
        replacement_profile_id: str | None,
    ) -> None:
        raise FeatureNotImplemented("PERSISTENCE")

    def initialize(self) -> None:
        """TODO PERSISTENCE: explicit initialization/migration; no implicit overwrite or fixture seed."""
        raise FeatureNotImplemented("PERSISTENCE")

    def admit_turn(
        self,
        owner_id: str,
        operation_id: str,
        request_id: str,
        session_id: str,
        expected_revision: int,
        player_input: str,
    ) -> TurnAdmission:
        """TODO PERSISTENCE: owner/revision/fingerprint admission or previous accepted receipt.
        Retain failed-attempt input privately for explicit retries; no provider call here.
        """
        raise FeatureNotImplemented("PERSISTENCE")
