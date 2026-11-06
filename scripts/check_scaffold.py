"""Check command routes, fixture decoding, work-item paths and SQLite schema offline."""

import ast
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from event_based.bootstrap import build
from event_based.messages import COMMAND_TOPICS, FLOW_EDGES
from layered.application import COMMAND_ROUTES
from shared.codec import decode, load_json
from shared.commands import COMMAND_TYPES
from shared.models.world import CampaignDraft
from shared.work_items import WORK_ITEMS


def main() -> None:
    paths = [
        p
        for p in ROOT.rglob("*.py")
        if not any(
            x.startswith(".") or x in {"dist", "__pycache__"} for x in p.relative_to(ROOT).parts
        )
    ]
    for path in paths:
        ast.parse(path.read_text(), filename=str(path.relative_to(ROOT)))
    for work_id, work in WORK_ITEMS.items():
        for name in work.files:
            assert (ROOT / name).is_file(), (work_id, name)
    assert set(COMMAND_TYPES) == set(COMMAND_ROUTES) == set(COMMAND_TOPICS)
    app = build(start_worker=False)
    try:
        for source, destination in FLOW_EDGES:
            assert source in app.bus.subscriptions and destination in app.bus.subscriptions
    finally:
        app.close()
    fixture = load_json((ROOT / "fixtures/thornmere.json").read_text())
    draft = decode(fixture["draft"], CampaignDraft)
    assert any(c.playable for c in draft.content.world.characters)
    with sqlite3.connect(":memory:") as connection:
        connection.executescript((ROOT / "shared/infrastructure/schema.sql").read_text())
        count = connection.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    print(
        f"Structural check: {len(paths)} Python files; {len(COMMAND_TYPES)} commands mapped twice; {count} SQL tables."
    )
    print("Fixture, work-item paths and handler registrations passed.")


if __name__ == "__main__":
    main()
