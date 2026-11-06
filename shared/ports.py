"""Domain-facing ports. Implementations live in infrastructure; composition roots inject them.

Application workflows see domain services, not SQL/HTTP/credential implementations.
"""

from typing import Protocol

from .models.accounts import AccountView
from .models.ai import ProviderCapture, ProviderMessage, ProviderProfile, ProviderResponse
from .models.common import SecretInput
from .models.gameplay import (
    AcceptedTurn,
    CommittedTurnNotice,
    SessionSnapshot,
    SessionSummary,
    TurnAdmission,
    TurnCommit,
)
from .models.reporting import CampaignReport
from .models.views import CampaignSummary
from .models.world import (
    CampaignContent,
    CampaignDraft,
    CatalogEntry,
    EditorProposal,
    PublishedCampaign,
)


class AccountRepository(Protocol):
    def create_account(self, username: str, password_hash: str) -> AccountView: ...
    def credential_record(self, username: str) -> tuple[AccountView, str] | None: ...
    def establish_login(self, account_id: str, client_session_id: str) -> str: ...
    def resolve_login(self, client_session_id: str) -> AccountView | None: ...
    def end_login(self, client_session_id: str) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, secret: SecretInput) -> str: ...
    def verify(self, secret: SecretInput, encoded_hash: str) -> bool: ...


class CampaignRepository(Protocol):
    def drafts_for_owner(self, owner_id: str) -> tuple[CampaignSummary, ...]: ...
    def create_campaign(self, owner_id: str, title: str, summary: str) -> CampaignDraft: ...
    def load_draft(self, owner_id: str, campaign_id: str) -> CampaignDraft: ...
    def save_draft(
        self, owner_id: str, campaign_id: str, expected_revision: int, content: CampaignContent
    ) -> CampaignDraft: ...
    def publish(
        self, owner_id: str, campaign_id: str, expected_revision: int
    ) -> PublishedCampaign: ...
    def published(self, version_id: str) -> PublishedCampaign: ...
    def catalog(self) -> tuple[CatalogEntry, ...]: ...


class SessionRepository(Protocol):
    def admit_turn(
        self,
        owner_id: str,
        operation_id: str,
        request_id: str,
        session_id: str,
        expected_revision: int,
        player_input: str,
    ) -> TurnAdmission: ...
    def sessions_for_owner(self, owner_id: str) -> tuple[SessionSummary, ...]: ...
    def start_session(
        self, owner_id: str, campaign: PublishedCampaign, pc_id: str
    ) -> SessionSnapshot: ...
    def load_session(self, owner_id: str, session_id: str) -> SessionSnapshot: ...
    def commit_turn(
        self,
        owner_id: str,
        operation_id: str,
        expected_revision: int,
        candidate: SessionSnapshot,
        player_input: str,
        narration: str,
    ) -> TurnCommit: ...
    def accepted_history(self, owner_id: str, session_id: str) -> tuple[AcceptedTurn, ...]: ...
    def adopt_update(
        self, owner_id: str, operation_id: str, expected_revision: int, candidate: SessionSnapshot
    ) -> SessionSnapshot: ...
    def record_attempt_failure(
        self,
        owner_id: str,
        operation_id: str,
        session_id: str,
        public_code: str,
        uncertain_provider_outcome: bool,
    ) -> None: ...
    def pending_notifications(self) -> tuple[CommittedTurnNotice, ...]: ...
    def acknowledge_notification(self, consumer: str, event_id: str) -> None: ...


class ProfileRepository(Protocol):
    def save_profile(
        self,
        owner_id: str,
        profile: ProviderProfile,
        expected_revision: int | None,
        credential_reference: str | None,
    ) -> ProviderProfile: ...
    def activate_profile(
        self, owner_id: str, profile_id: str, expected_revision: int
    ) -> ProviderProfile: ...
    def delete_profile(
        self,
        owner_id: str,
        profile_id: str,
        expected_revision: int,
        replacement_profile_id: str | None,
    ) -> None: ...
    def list_profiles(self, owner_id: str) -> tuple[ProviderProfile, ...]: ...
    def active_profile(self, owner_id: str) -> ProviderProfile: ...
    def credential_reference(self, owner_id: str, profile_id: str, revision: int) -> str: ...


class CredentialStore(Protocol):
    def read(self, owner_id: str, reference: str) -> SecretInput: ...
    def write(self, owner_id: str, reference: str, value: SecretInput) -> None: ...
    def remove(self, owner_id: str, reference: str) -> None: ...


class ProviderTransport(Protocol):
    mode: str

    def complete(
        self, messages: tuple[ProviderMessage, ...], capture: ProviderCapture
    ) -> ProviderResponse: ...


class ReportRepository(Protocol):
    def apply_committed_notice(self, notice: CommittedTurnNotice) -> None: ...
    def campaign_report(
        self, owner_id: str, campaign_id: str, version_id: str | None
    ) -> CampaignReport: ...


class EditorProposalRepository(Protocol):
    def save_editor_proposal(self, owner_id: str, proposal: EditorProposal) -> None: ...
    def load_editor_proposal(self, owner_id: str, proposal_id: str) -> EditorProposal: ...
