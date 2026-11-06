"""Composition root helper, not an application coordinator. No I/O on construction."""

from pathlib import Path

from .domain.accounts import AccountService
from .domain.ai import AIService
from .domain.editor import EditorService
from .domain.gameplay import GameplayService
from .domain.knowledge import KnowledgePolicy
from .domain.profiles import ProfileService
from .domain.queries import QueryService
from .domain.reporting import ReportingService
from .domain.services import Services
from .domain.updates import UpdateService
from .domain.world import WorldService
from .infrastructure.provider import CompatibleHttpProvider
from .infrastructure.secrets import LocalCredentialStore
from .infrastructure.security import ScryptPasswordHasher
from .infrastructure.sqlite import SQLiteStore


def compose_services(data_root: Path) -> Services:
    repository = SQLiteStore(data_root / "application.sqlite3")
    credentials = LocalCredentialStore(data_root / "private")
    accounts = AccountService(repository, ScryptPasswordHasher())
    knowledge = KnowledgePolicy()
    updates = UpdateService(repository, repository)
    reporting = ReportingService(repository, repository)
    return Services(
        accounts=accounts,
        world=WorldService(repository),
        editor=EditorService(repository),
        knowledge=knowledge,
        gameplay=GameplayService(repository, repository),
        profiles=ProfileService(repository, credentials),
        ai=AIService(CompatibleHttpProvider()),
        updates=updates,
        reporting=reporting,
        queries=QueryService(
            accounts, repository, repository, repository, reporting, updates, knowledge
        ),
    )
