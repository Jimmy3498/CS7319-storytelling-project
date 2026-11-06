"""Structural regressions for access metadata, message envelopes and queue lifecycle."""

import unittest

from event_based.bus import InProcessBus
from event_based.messages import Message, Topic
from shared import commands as c
from shared.models.common import Access, RequestContext, SecretInput, Visibility
from shared.models.gameplay import CommittedTurnNotice, TurnAdmission


class BoundaryTests(unittest.TestCase):
    def test_invalid_access_scopes_fail_closed(self):
        for args in (
            (Visibility.CHARACTER, ()),
            (Visibility.PUBLIC, ("rowan",)),
            (Visibility.CHARACTER, ("rowan", "rowan")),
            ("public", ()),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                Access(*args)

    def test_admission_requires_exactly_one_result_branch(self):
        with self.assertRaises(ValueError):
            TurnAdmission(None, None)

    def test_private_command_cannot_be_attached_to_public_completion(self):
        ctx = RequestContext("client", None, "c")
        command = c.Login("name", SecretInput("SECRET"))
        notice = CommittedTurnNotice("event", "operation", "session", "campaign", "version", 1)
        with self.assertRaises(ValueError):
            Message(
                "event",
                "operation",
                "c",
                None,
                Topic.TURN_COMMITTED,
                ctx,
                command=command,
                notice=notice,
            )
        with self.assertRaises(ValueError):
            Message(
                "event", "operation", "c", None, Topic.LOGIN, ctx
            )  # required private command absent

    def test_error_callback_failure_does_not_stop_healthy_subscriber(self):
        ctx = RequestContext("client", None, "c")
        called = []

        def callback(*args):
            raise RuntimeError("CALLBACK-PRIVATE-DATA")

        def broken(message):
            raise RuntimeError("HANDLER-PRIVATE-DATA")

        bus = InProcessBus(callback)
        bus.subscribe(Topic.LOGIN, "broken", broken)
        bus.subscribe(Topic.LOGIN, "healthy", lambda message: called.append(message.id))
        bus.publish(
            Message(
                "event",
                "operation",
                "c",
                None,
                Topic.LOGIN,
                ctx,
                command=c.Login("test", SecretInput("TEST")),
            )
        )
        try:
            bus.dispatch_one()
        finally:
            bus.close()
        self.assertEqual(called, ["event"])
        self.assertNotIn("PRIVATE-DATA", repr(bus.trace))

    def test_shutdown_drops_pending_private_command(self):
        ctx = RequestContext("client", None, "c")
        bus = InProcessBus(lambda *args: None)
        bus.publish(
            Message(
                "event",
                "operation",
                "c",
                None,
                Topic.LOGIN,
                ctx,
                command=c.Login("test", SecretInput("TEST")),
            )
        )
        bus.close()
        self.assertEqual(bus.pending, 0)
