"""Layered application coordinator: explicit calls to domain-facing capabilities.

No HTTP, SQLite, credential-store implementation or event bus is imported here.
Business services deliberately raise FeatureNotImplemented until contributors fill them.
"""

from shared import commands as c
from shared.domain.services import Services
from shared.errors import ApplicationError, ErrorCode
from shared.models.common import RequestContext
from shared.models.gameplay import TurnCommit
from shared.models.views import TurnResultView

COMMAND_ROUTES = {
    c.RegisterAccount: "register",
    c.Login: "login",
    c.Logout: "logout",
    c.CreateCampaign: "create_campaign",
    c.SaveDraft: "save_draft",
    c.PublishCampaign: "publish_campaign",
    c.RequestEditorProposal: "editor_proposal",
    c.ReviewEditorProposal: "review_editor",
    c.StartSession: "start_session",
    c.SubmitTurn: "submit_turn",
    c.RetryTurn: "retry_turn",
    c.AdoptCampaignUpdate: "adopt_update",
    c.SaveProviderCard: "save_card",
    c.ActivateProviderCard: "activate_card",
    c.DeleteProviderCard: "delete_card",
}


class LayeredApplication:
    def __init__(self, services: Services) -> None:
        self.services = services

    def execute(self, context: RequestContext, command: c.Command, operation_id: str) -> object:
        """Direct ordered call/return; this method never publishes a message."""
        s = self.services
        if isinstance(command, c.RegisterAccount):
            return s.accounts.register(context, command)
        if isinstance(command, c.Login):
            return s.accounts.login(context, command)
        if isinstance(command, c.Logout):
            return s.accounts.logout(context)
        user = s.accounts.require_user(context)
        if isinstance(command, c.CreateCampaign):
            return s.world.create(user.id, command)
        if isinstance(command, c.SaveDraft):
            return s.world.save(user.id, command)
        if isinstance(command, c.PublishCampaign):
            return s.world.publish(user.id, command)
        if isinstance(command, c.SaveProviderCard):
            return s.profiles.save(user.id, command)
        if isinstance(command, c.ActivateProviderCard):
            return s.profiles.activate(user.id, command)
        if isinstance(command, c.DeleteProviderCard):
            return s.profiles.delete(user.id, command)
        if isinstance(command, c.ReviewEditorProposal):
            return s.editor.review(user.id, command)
        if isinstance(command, c.RequestEditorProposal):
            buffer = s.editor.prepare(user.id, command)
            capture = s.profiles.capture(user.id)
            candidate, summary = s.ai.propose_editor(
                buffer, command.instruction, command.selected_record_ids, capture
            )
            return s.editor.retain_proposal(user.id, buffer, candidate, summary)
        if isinstance(command, c.StartSession):
            session = s.gameplay.start(user.id, command)
            return s.knowledge.player_view(session, (), "")
        if isinstance(command, c.AdoptCampaignUpdate):
            session = s.updates.adopt(user.id, operation_id, command)
            history = s.gameplay.history(user.id, session.id)
            return s.knowledge.player_view(session, history, "")
        if isinstance(command, c.RetryTurn):
            retry = s.gameplay.retry(user.id, command, operation_id)
            if isinstance(retry, TurnCommit):
                return TurnResultView(retry.turn, None)
            return self._turn(user.id, retry, operation_id, context.request_id)
        if isinstance(command, c.SubmitTurn):
            return self._turn(user.id, command, operation_id, context.request_id)
        raise ApplicationError(ErrorCode.INVALID, "Unsupported application command")

    def _turn(
        self, owner_id: str, command: c.SubmitTurn, operation_id: str, request_id: str | None
    ) -> TurnResultView:
        """Layered turn sequence.

        TODO LAYERED: integrate durable admission/failure receipts and retry fencing
        with PERSISTENCE (A4/A5/A6). SQL commit must include
        a recoverable reporting notice. Network calls are outside the transaction.
        """
        s = self.services
        if request_id is None:
            raise ApplicationError(ErrorCode.INVALID, "Missing request identity")
        admission = s.gameplay.prepare(owner_id, command, operation_id, request_id)
        if admission.previous_commit is not None:
            return TurnResultView(admission.previous_commit.turn, None)
        baseline = admission.baseline
        if baseline is None:
            raise ApplicationError(ErrorCode.INTERNAL, "Invalid turn admission")
        capture = s.profiles.capture(owner_id)
        director_context = s.knowledge.director_context(baseline, command.player_input)
        proposal = s.ai.plan_turn(director_context, capture)
        candidate = s.gameplay.validate_and_project(baseline, proposal)
        candidate = s.knowledge.authorize_disclosures(baseline, candidate, proposal)
        history = s.gameplay.history(owner_id, baseline.id)
        visible = s.knowledge.player_view(candidate, history, command.player_input)
        narration = s.ai.narrate(visible, capture)
        commit = s.gameplay.commit(owner_id, operation_id, command, candidate, narration)
        try:
            s.reporting.consume_committed_turn(commit.notice)
        except Exception:
            # Already committed: do not turn this into a false gameplay failure.
            # Pending notification remains for explicit Layered reporting catch-up.
            return TurnResultView(commit.turn, True)
        return TurnResultView(commit.turn, False)
