"""Application commands. New work uses new request IDs; retries link to a previous operation.

Application services authorize and validate commands. UI accesses infrastructure through those services.
"""

from dataclasses import dataclass
from typing import TypeAlias

from .models.common import SecretInput
from .models.world import CampaignContent, EditorBuffer


@dataclass(frozen=True)
class RegisterAccount:
    username: str
    password: SecretInput


@dataclass(frozen=True)
class Login:
    username: str
    password: SecretInput


@dataclass(frozen=True)
class Logout:
    pass


@dataclass(frozen=True)
class CreateCampaign:
    title: str
    summary: str


@dataclass(frozen=True)
class SaveDraft:
    campaign_id: str
    expected_revision: int
    content: CampaignContent


@dataclass(frozen=True)
class PublishCampaign:
    campaign_id: str
    expected_revision: int


@dataclass(frozen=True)
class RequestEditorProposal:
    buffer: EditorBuffer
    instruction: str
    selected_record_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviewEditorProposal:
    proposal_id: str
    buffer: EditorBuffer
    accept: bool


@dataclass(frozen=True)
class StartSession:
    published_version_id: str
    player_character_id: str


@dataclass(frozen=True)
class SubmitTurn:
    session_id: str
    expected_revision: int
    player_input: str


@dataclass(frozen=True)
class RetryTurn:
    previous_operation_id: str
    session_id: str
    expected_revision: int


@dataclass(frozen=True)
class AdoptCampaignUpdate:
    session_id: str
    target_version_id: str
    expected_session_revision: int


@dataclass(frozen=True)
class SaveProviderCard:
    profile_id: str | None
    expected_revision: int | None
    name: str
    endpoint: str
    model: str
    protocol: str
    credential: SecretInput | None


@dataclass(frozen=True)
class ActivateProviderCard:
    profile_id: str
    expected_revision: int


@dataclass(frozen=True)
class DeleteProviderCard:
    profile_id: str
    expected_revision: int
    replacement_profile_id: str | None = None


Command: TypeAlias = (
    RegisterAccount
    | Login
    | Logout
    | CreateCampaign
    | SaveDraft
    | PublishCampaign
    | RequestEditorProposal
    | ReviewEditorProposal
    | StartSession
    | SubmitTurn
    | RetryTurn
    | AdoptCampaignUpdate
    | SaveProviderCard
    | ActivateProviderCard
    | DeleteProviderCard
)

COMMAND_TYPES = (
    RegisterAccount,
    Login,
    Logout,
    CreateCampaign,
    SaveDraft,
    PublishCampaign,
    RequestEditorProposal,
    ReviewEditorProposal,
    StartSession,
    SubmitTurn,
    RetryTurn,
    AdoptCampaignUpdate,
    SaveProviderCard,
    ActivateProviderCard,
    DeleteProviderCard,
)
