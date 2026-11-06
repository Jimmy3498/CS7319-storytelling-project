"""Stable contribution IDs. These describe missing work, not completed capabilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkItem:
    title: str
    files: tuple[str, ...]
    acceptance: tuple[str, ...]


WORK_ITEMS = {
    "AUTH": WorkItem(
        "Accounts, password hashes, login/logout and ownership",
        ("shared/domain/accounts.py", "shared/infrastructure/sqlite.py"),
        ("A0",),
    ),
    "WORLD": WorkItem(
        "Rich typed world editing and structural publication readiness",
        ("shared/domain/world.py", "shared/ui/editor.py"),
        ("A1",),
    ),
    "EDITOR": WorkItem(
        "Contextual AI proposals; review changes the edit buffer, Save persists",
        ("shared/domain/editor.py", "shared/ui/editor.py"),
        ("A1", "A3"),
    ),
    "PRIVACY": WorkItem(
        "Fail-closed context projections and explicit disclosure gates",
        ("shared/domain/knowledge.py",),
        ("A11",),
    ),
    "GAMEPLAY": WorkItem(
        "Preset-PC sessions, supported effects, retries and turn validation",
        ("shared/domain/gameplay.py", "shared/ui/play.py"),
        ("A2", "A4", "A5", "A13"),
    ),
    "MERGE": WorkItem(
        "Opt-in conflict-free three-way adoption with retained checkpoint",
        ("shared/domain/updates.py",),
        ("A9",),
    ),
    "REPORTS": WorkItem(
        "Activity and version-aware milestone projections",
        ("shared/domain/reporting.py", "shared/ui/activity.py"),
        ("A7", "A10"),
    ),
    "PROFILES": WorkItem(
        "Private per-account API cards and captured request configuration",
        ("shared/domain/profiles.py", "shared/infrastructure/secrets.py"),
        ("A12",),
    ),
    "PROVIDER": WorkItem(
        "Supported HTTP API plus explicit deterministic test provider",
        ("shared/infrastructure/provider.py",),
        ("A3", "A5", "A12"),
    ),
    "PERSISTENCE": WorkItem(
        "SQLite repositories, atomic turn commit, receipts and durable notifications",
        ("shared/infrastructure/sqlite.py", "shared/infrastructure/schema.sql"),
        ("A1", "A2", "A6", "A9", "A13"),
    ),
    "LAYERED": WorkItem(
        "Fill explicit call/return workflows through domain-facing services",
        ("layered/application.py",),
        ("A8",),
    ),
    "EVENTS": WorkItem(
        "Fill registered handlers, durable outbox recovery and deduplication",
        ("event_based/handlers.py", "event_based/recovery.py"),
        ("A5", "A6", "A8"),
    ),
    "UI": WorkItem(
        "Connect forms, owner-scoped navigation, edit buffers and operation status",
        (
            "shared/ui/shell.py",
            "shared/ui/accounts.py",
            "shared/ui/catalog.py",
            "shared/ui/editor.py",
            "shared/ui/play.py",
            "shared/ui/activity.py",
            "shared/ui/profiles.py",
        ),
        ("A0", "A1", "A2", "A3", "A7"),
    ),
}
