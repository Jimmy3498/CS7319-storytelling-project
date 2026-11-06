"""Unimplemented business acceptance, deliberately skipped; never empty passing tests."""

import unittest


class AcceptanceCases:
    @unittest.skip("TODO AUTH; A0 is not implemented")
    def test_a0(self):
        """Register, login/logout, reject wrong credentials and cross-account campaign/session/card access."""
        self.fail("Replace with real A0 assertions through self.architecture")

    @unittest.skip("TODO WORLD / EDITOR; A1 is not implemented")
    def test_a1(self):
        """Save incomplete drafts; rich entity CRUD and reviewed AI edits; reject stale/invalid publication; publish valid catalog record."""
        self.fail("Replace with real A1 assertions through self.architecture")

    @unittest.skip("TODO GAMEPLAY; A2 is not implemented")
    def test_a2(self):
        """Start two preset-PC sessions; accepted changes affect only the selected session and preserve its base campaign."""
        self.fail("Replace with real A2 assertions through self.architecture")

    @unittest.skip("TODO PROVIDER / EDITOR; A3 is not implemented")
    def test_a3(self):
        """Run deterministic provider then explicit real configured API; inspect separate contexts and manual editor acceptance versus auto gameplay commit."""
        self.fail("Replace with real A3 assertions through self.architecture")

    @unittest.skip("TODO GAMEPLAY / PERSISTENCE; A4 is not implemented")
    def test_a4(self):
        """Reject malformed/unknown/illegal/stale effects; deduplicate same operation; conflict on changed payload."""
        self.fail("Replace with real A4 assertions through self.architecture")

    @unittest.skip("TODO LAYERED / EVENTS; A5 is not implemented")
    def test_a5(self):
        """Inject timeout/delay/storage/subscriber failures and late results; preserve state and expose explicit retry/uncertainty."""
        self.fail("Replace with real A5 assertions through self.architecture")

    @unittest.skip("TODO PERSISTENCE / EVENTS; A6 is not implemented")
    def test_a6(self):
        """Restart and resume accepted state; recover notifications without duplicate local effects or automatic paid-request replay."""
        self.fail("Replace with real A6 assertions through self.architecture")

    @unittest.skip("TODO REPORTS; A7 is not implemented")
    def test_a7(self):
        """Known accepted/rejected/failed attempt counts, no duplicate counts, reporting catch-up independent of gameplay result."""
        self.fail("Replace with real A7 assertions through self.architecture")

    @unittest.skip("TODO LAYERED / EVENTS; A8 is not implemented")
    def test_a8(self):
        """Equivalent observed outcomes and genuinely different call versus queued traces; same fixture/provider/delay inputs."""
        self.fail("Replace with real A8 assertions through self.architecture")

    @unittest.skip("TODO MERGE; A9 is not implemented")
    def test_a9(self):
        """Continue old version; adopt compatible update with checkpoint/progress; reject overlap/broken references atomically."""
        self.fail("Replace with real A9 assertions through self.architecture")

    @unittest.skip("TODO REPORTS; A10 is not implemented")
    def test_a10(self):
        """False-to-true marker hits once per session/fingerprint; distinct-account/session counts and version denominators; no rejected-turn awards."""
        self.fail("Replace with real A10 assertions through self.architecture")

    @unittest.skip("TODO PRIVACY; A11 is not implemented")
    def test_a11(self):
        """Inspect outbound prompts/history/UI/report projections for private canaries, wrong-actor/scope facts, missing labels and privileged free-text handoff."""
        self.fail("Replace with real A11 assertions through self.architecture")

    @unittest.skip("TODO PROFILES; A12 is not implemented")
    def test_a12(self):
        """Private account cards, captured config, endpoint rebinding, secret redaction and no calls on save/activate or unauthorized card access."""
        self.fail("Replace with real A12 assertions through self.architecture")

    @unittest.skip("TODO GAMEPLAY; A13 is not implemented")
    def test_a13(self):
        """Create a real allowed template instance; persist across resume; duplicate retry adds none; reject invalid templates/destinations/NPC creation."""
        self.fail("Replace with real A13 assertions through self.architecture")


class LayeredAcceptance(AcceptanceCases, unittest.TestCase):
    architecture = "layered"


class EventBasedAcceptance(AcceptanceCases, unittest.TestCase):
    architecture = "event_based"
