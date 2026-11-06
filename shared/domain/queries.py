from ..errors import unfinished
from ..models.common import RequestContext
from ..ports import CampaignRepository, ProfileRepository, SessionRepository
from ..queries import Query, QueryResult
from .accounts import AccountService
from .knowledge import KnowledgePolicy
from .reporting import ReportingService
from .updates import UpdateService


class QueryService:
    def __init__(
        self,
        accounts: AccountService,
        campaigns: CampaignRepository,
        sessions: SessionRepository,
        profiles: ProfileRepository,
        reporting: ReportingService,
        updates: UpdateService,
        knowledge: KnowledgePolicy,
    ) -> None:
        self.accounts, self.campaigns, self.sessions = accounts, campaigns, sessions
        self.profiles, self.reporting, self.updates = profiles, reporting, updates
        self.knowledge = knowledge

    def read(self, context: RequestContext, query: Query) -> QueryResult:
        """TODO UI/PERSISTENCE: read through authorized domain/repository ports.
        Catalog -> CatalogEntry tuples; my drafts -> owner summaries; editor -> owned draft;
        sessions -> SessionSummary; resume -> PlayerView + accepted transcript; report ->
        owner-authorized aggregates; cards -> redacted owner profiles; update preview ->
        player-safe summary without candidate world/private conflict text. Never expose a raw
        SessionSnapshot or private provider capture to player/catalog/profile views.
        """
        unfinished("PERSISTENCE")
