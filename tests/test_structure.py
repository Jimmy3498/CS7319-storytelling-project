import ast
import dataclasses
import sqlite3
import unittest
from pathlib import Path
from threading import Event

from event_based.bootstrap import build as event_based
from event_based.bus import InProcessBus
from event_based.messages import COMMAND_TOPICS, FLOW_EDGES, Message, Topic
from layered.application import COMMAND_ROUTES
from layered.bootstrap import build as layered
from shared import commands as c
from shared.codec import decode, load_json
from shared.errors import ApplicationError, FeatureNotImplemented
from shared.gateway import OperationStatus
from shared.infrastructure.provider import CompatibleHttpProvider, ScriptedTestProvider
from shared.infrastructure.sqlite import SQLiteStore
from shared.models.ai import (
    PlayerView,
    ProviderCapture,
    ProviderProfile,
    ProviderResponse,
)
from shared.models.common import Access, RequestContext, SecretInput
from shared.models.gameplay import CommittedTurnNotice
from shared.models.world import CampaignDraft, EditorBuffer
from shared.operation_status import OperationStatusStore
from shared.work_items import WORK_ITEMS

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return decode(load_json((ROOT / "fixtures/thornmere.json").read_text())["draft"], CampaignDraft)


def commands():
    draft = fixture()
    buffer = EditorBuffer(draft.id, 0, 0, draft.content)
    return (
        c.RegisterAccount("test", SecretInput("NOT-A-REAL-PASSWORD")),
        c.Login("test", SecretInput("TEST")),
        c.Logout(),
        c.CreateCampaign("Title", "Summary"),
        c.SaveDraft(draft.id, 0, draft.content),
        c.PublishCampaign(draft.id, 0),
        c.RequestEditorProposal(buffer, "Improve this description", ()),
        c.ReviewEditorProposal("proposal", buffer, True),
        c.StartSession("version-1", "rowan"),
        c.SubmitTurn("session", 0, "Look around"),
        c.RetryTurn("previous", "session", 0),
        c.AdoptCampaignUpdate("session", "version-2", 0),
        c.SaveProviderCard(
            None,
            None,
            "Test",
            "https://HOST/v1/chat/completions",
            "MODEL",
            "chat-completions-compatible",
            None,
        ),
        c.ActivateProviderCard("card", 0),
        c.DeleteProviderCard("card", 0),
    )


class ContractStructureTests(unittest.TestCase):
    def test_commands_have_both_architecture_routes(self):
        self.assertEqual(set(c.COMMAND_TYPES), set(COMMAND_ROUTES))
        self.assertEqual(set(c.COMMAND_TYPES), set(COMMAND_TOPICS))
        self.assertEqual(set(c.COMMAND_TYPES), {type(x) for x in commands()})

    def test_every_stub_command_reports_unimplemented_not_success(self):
        context = RequestContext("client", None, "correlation")
        direct = layered()
        queued = event_based(start_worker=False)
        try:
            for index, command in enumerate(commands()):
                with self.subTest(command=type(command).__name__):
                    self.assertEqual(
                        direct.submit(context, command, str(index)).status,
                        OperationStatus.UNIMPLEMENTED,
                    )
                    receipt = queued.submit(context, command, str(index))
                    self.assertEqual(receipt.status, OperationStatus.PENDING)
                    self.assertTrue(queued.bus.dispatch_one())
                    self.assertEqual(
                        queued.poll(context, receipt.operation_id).status,
                        OperationStatus.UNIMPLEMENTED,
                    )
        finally:
            direct.close()
            queued.close()

    def test_all_declared_edges_and_independent_completion_consumers_registered(self):
        app = event_based(start_worker=False)
        try:
            for source, target in FLOW_EDGES:
                self.assertIn(source, app.bus.subscriptions)
                self.assertIn(target, app.bus.subscriptions)
            self.assertEqual(
                app.bus.subscriptions[Topic.TURN_COMMITTED], ("result-consumer", "report-consumer")
            )
        finally:
            app.close()

    def test_adapters_fail_closed(self):
        with self.assertRaises(FeatureNotImplemented):
            SQLiteStore(Path("NOT-CREATED.sqlite3")).catalog()
        profile = ProviderProfile(
            "id",
            "owner",
            "test",
            "https://HOST/v1/chat/completions",
            "MODEL",
            "chat-completions-compatible",
            0,
            True,
        )
        capture = ProviderCapture(profile, SecretInput("PRIVATE-CANARY"))
        with self.assertRaises(FeatureNotImplemented):
            CompatibleHttpProvider().complete((), capture)
        self.assertNotIn("PRIVATE-CANARY", repr(capture))
        self.assertNotIn("PRIVATE-CANARY", repr(SecretInput("PRIVATE-CANARY")))
        self.assertFalse((ROOT / "NOT-CREATED.sqlite3").exists())

    def test_scripted_provider_is_explicit_and_does_not_fabricate_more_responses(self):
        provider = ScriptedTestProvider((ProviderResponse("synthetic"),))
        response = provider.complete(
            (), None
        )  # structural test double ignores capture, never network.
        self.assertEqual(response.content, "synthetic")
        self.assertEqual(provider.calls, 1)
        self.assertEqual(provider.mode, "scripted-test-double")
        with self.assertRaises(ApplicationError):
            provider.complete((), None)

    def test_required_access_and_unknown_fields_reject_structurally(self):
        with self.assertRaises(ValueError):
            decode({}, Access)
        with self.assertRaises(ValueError):
            decode({"visibility": "all-secrets"}, Access)
        with self.assertRaises(ValueError):
            decode({"visibility": "public", "private_blob": "x"}, Access)
        with self.assertRaises(ValueError):
            load_json('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            load_json('{"a":NaN}')
        self.assertNotIn("world", {f.name for f in dataclasses.fields(PlayerView)})
        self.assertNotIn("planner_prose", {f.name for f in dataclasses.fields(PlayerView)})

    def test_fixture_shape_and_private_canary_classification(self):
        draft = fixture()
        world = draft.content.world
        self.assertTrue(any(x.playable for x in world.characters))
        locations = {x.id for x in world.locations}
        templates = {x.id for x in world.item_templates}
        for character in world.characters:
            self.assertIn(character.location_id, locations)
        for item in world.items:
            self.assertIn(item.template_id, templates)
            self.assertNotEqual(item.holder_id is None, item.location_id is None)
        cedric = next(x for x in world.characters if x.id == "cedric")
        record = cedric.knowledge[0]
        self.assertEqual(record.access.visibility.value, "character")
        self.assertEqual(record.access.character_ids, ("cedric",))
        self.assertIsNone(record.reveal_when)
        self.assertTrue(any(x.spawn_when is not None for x in world.item_templates))

    def test_work_item_targets_exist(self):
        for item in WORK_ITEMS.values():
            for path in item.files:
                self.assertTrue((ROOT / path).is_file(), path)

    def test_schema_parses_and_enforces_basic_foreign_keys(self):
        with sqlite3.connect(":memory:") as db:
            db.executescript((ROOT / "shared/infrastructure/schema.sql").read_text())
            self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertIn(
                "player_input", {row[1] for row in db.execute("PRAGMA table_info(turn_attempts)")}
            )
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "INSERT INTO campaigns VALUES (?,?,?,?,?)", ("c", "unknown", 0, "{}", "now")
                )
            self.assertTrue(
                db.execute(
                    "SELECT name FROM sqlite_master WHERE name='session_version_memberships'"
                ).fetchone()
            )

    def test_dependency_directions(self):
        for package, forbidden in (
            ("shared", {"layered", "event_based"}),
            ("layered", {"event_based"}),
            ("event_based", {"layered"}),
        ):
            for path in (ROOT / package).rglob("*.py"):
                for node in ast.walk(ast.parse(path.read_text())):
                    if isinstance(node, ast.ImportFrom):
                        modules = (node.module or "",)
                    elif isinstance(node, ast.Import):
                        modules = tuple(alias.name for alias in node.names)
                    else:
                        continue
                    for module in modules:
                        self.assertNotIn(module.split(".")[0], forbidden, str(path))
                        if package == "shared" and ("ui" in path.parts or "domain" in path.parts):
                            self.assertNotIn("infrastructure", module.split("."), str(path))


class StatusAndBusTests(unittest.TestCase):
    def setUp(self):
        self.context = RequestContext("client", None, "correlation")

    def test_status_owner_and_request_payload_isolation(self):
        store = OperationStatusStore()
        command = c.RegisterAccount("test", SecretInput("SECRET-CANARY"))
        receipt, fresh = store.begin(self.context, "same-id", command)
        self.assertTrue(fresh)
        same, fresh = store.begin(self.context, "same-id", command)
        self.assertFalse(fresh)
        self.assertEqual(same.operation_id, receipt.operation_id)
        with self.assertRaises(ApplicationError):
            store.begin(
                self.context, "same-id", c.RegisterAccount("test", SecretInput("different"))
            )
        with self.assertRaises(ApplicationError):
            store.read(RequestContext("other", None, "c"), receipt.operation_id)
        with self.assertRaises(ApplicationError):
            store.read(RequestContext("client", "another-account", "c"), receipt.operation_id)
        self.assertNotIn("SECRET-CANARY", repr(store.__dict__))
        failed = store.fail(receipt.operation_id, ValueError("DO-NOT-EXPOSE"))
        self.assertNotIn("DO-NOT-EXPOSE", failed.message)

    def test_publish_does_not_dispatch_inline(self):
        calls = []
        errors = []
        bus = InProcessBus(lambda *args: errors.append(args))
        bus.subscribe(Topic.LOGIN, "one", lambda message: calls.append(message.id))
        bus.publish(
            Message(
                "e",
                "o",
                "c",
                None,
                Topic.LOGIN,
                self.context,
                command=c.Login("probe", SecretInput("TEST")),
            )
        )
        self.assertEqual(calls, [])
        self.assertEqual(bus.pending, 1)
        self.assertTrue(bus.dispatch_one())
        self.assertEqual(calls, ["e"])
        self.assertEqual(errors, [])
        bus.close()

    def test_subscriber_failure_does_not_block_other_subscriber(self):
        calls = []
        errors = []
        bus = InProcessBus(lambda message, name, error: errors.append(name))

        def broken(message):
            raise ValueError("PRIVATE-ERROR")

        bus.subscribe(Topic.TURN_COMMITTED, "broken", broken)
        bus.subscribe(Topic.TURN_COMMITTED, "healthy", lambda message: calls.append(message.id))
        bus.publish(
            Message(
                "e",
                "o",
                "c",
                None,
                Topic.TURN_COMMITTED,
                self.context,
                notice=CommittedTurnNotice("e", "o", "s", "c", "v", 1),
            )
        )
        bus.dispatch_one()
        bus.close()
        self.assertEqual(errors, ["broken"])
        self.assertEqual(calls, ["e"])
        self.assertNotIn("PRIVATE-ERROR", repr(bus.trace))

    def test_real_worker_dispatch_and_shutdown(self):
        observed = Event()
        errors = []
        bus = InProcessBus(lambda *args: errors.append(args))
        bus.subscribe(Topic.LOGIN, "probe", lambda message: observed.set())
        bus.start()
        bus.publish(
            Message(
                "e",
                "o",
                "c",
                None,
                Topic.LOGIN,
                self.context,
                command=c.Login("probe", SecretInput("TEST")),
            )
        )
        self.assertTrue(observed.wait(2))
        bus.close()
        self.assertEqual(errors, [])
        with self.assertRaises(RuntimeError):
            bus.publish(
                Message(
                    "late",
                    "o",
                    "c",
                    None,
                    Topic.LOGIN,
                    self.context,
                    command=c.Login("probe", SecretInput("TEST")),
                )
            )
