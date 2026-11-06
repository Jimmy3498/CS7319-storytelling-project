from dataclasses import dataclass
from enum import StrEnum

from .models.ai import PlayerView, ProviderProfile
from .models.gameplay import SessionSummary
from .models.reporting import CampaignReport
from .models.views import CampaignSummary, UpdatePreviewView
from .models.world import CampaignDraft, CatalogEntry


class QueryKind(StrEnum):
    CATALOG = "catalog"
    MY_CAMPAIGNS = "my_campaigns"
    EDITOR_DRAFT = "editor_draft"
    MY_SESSIONS = "my_sessions"
    RESUME_SESSION = "resume_session"
    CAMPAIGN_REPORT = "campaign_report"
    PROVIDER_CARDS = "provider_cards"
    UPDATE_PREVIEW = "update_preview"


@dataclass(frozen=True)
class Query:
    kind: QueryKind
    resource_id: str | None = None
    version_id: str | None = None


# Closed query result families; implementation still performs caller authorization/projection.
QueryResult = (
    tuple[CatalogEntry, ...]
    | tuple[CampaignSummary, ...]
    | CampaignDraft
    | tuple[SessionSummary, ...]
    | PlayerView
    | CampaignReport
    | tuple[ProviderProfile, ...]
    | UpdatePreviewView
)
