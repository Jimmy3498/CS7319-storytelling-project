from dataclasses import dataclass

from .accounts import AccountService
from .ai import AIService
from .editor import EditorService
from .gameplay import GameplayService
from .knowledge import KnowledgePolicy
from .profiles import ProfileService
from .queries import QueryService
from .reporting import ReportingService
from .updates import UpdateService
from .world import WorldService


@dataclass(frozen=True)
class Services:
    accounts: AccountService
    world: WorldService
    editor: EditorService
    knowledge: KnowledgePolicy
    gameplay: GameplayService
    profiles: ProfileService
    ai: AIService
    updates: UpdateService
    reporting: ReportingService
    queries: QueryService
