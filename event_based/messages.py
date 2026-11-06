"""Named command/event contracts. Intermediate events carry work references, not secret blobs."""

from dataclasses import dataclass, field
from enum import StrEnum

from shared import commands as c
from shared.models.common import RequestContext
from shared.models.gameplay import CommittedTurnNotice


class Topic(StrEnum):
    REGISTER = "account.register_requested"
    LOGIN = "account.login_requested"
    LOGOUT = "account.logout_requested"
    CREATE_CAMPAIGN = "campaign.create_requested"
    SAVE_DRAFT = "campaign.save_requested"
    PUBLISH = "campaign.publish_requested"
    EDITOR_REQUEST = "editor.proposal_requested"
    EDITOR_CONTEXT = "editor.context_prepared"
    EDITOR_CANDIDATE = "editor.candidate_proposed"
    EDITOR_REVIEW = "editor.review_requested"
    START_SESSION = "session.start_requested"
    TURN_REQUEST = "turn.requested"
    TURN_CONTEXT = "turn.context_prepared"
    TURN_PLAN = "turn.plan_proposed"
    TURN_VALIDATED = "turn.validated_for_narration"
    NARRATION = "turn.narration_proposed"
    TURN_COMMITTED = "turn.committed"
    TURN_FAILED = "turn.rejected_or_failed"
    RETRY = "turn.retry_requested"
    UPDATE = "session.update_requested"
    SAVE_CARD = "profile.save_requested"
    ACTIVATE_CARD = "profile.activate_requested"
    DELETE_CARD = "profile.delete_requested"


COMMAND_TOPICS = {
    c.RegisterAccount: Topic.REGISTER,
    c.Login: Topic.LOGIN,
    c.Logout: Topic.LOGOUT,
    c.CreateCampaign: Topic.CREATE_CAMPAIGN,
    c.SaveDraft: Topic.SAVE_DRAFT,
    c.PublishCampaign: Topic.PUBLISH,
    c.RequestEditorProposal: Topic.EDITOR_REQUEST,
    c.ReviewEditorProposal: Topic.EDITOR_REVIEW,
    c.StartSession: Topic.START_SESSION,
    c.SubmitTurn: Topic.TURN_REQUEST,
    c.RetryTurn: Topic.RETRY,
    c.AdoptCampaignUpdate: Topic.UPDATE,
    c.SaveProviderCard: Topic.SAVE_CARD,
    c.ActivateProviderCard: Topic.ACTIVATE_CARD,
    c.DeleteProviderCard: Topic.DELETE_CARD,
}


@dataclass(frozen=True)
class Message:
    id: str
    operation_id: str
    correlation_id: str
    causation_id: str | None
    topic: Topic
    context: RequestContext
    # Only the first private command message may contain command data.
    command: c.Command | None = field(default=None, repr=False)
    work_reference: str | None = None
    notice: CommittedTurnNotice | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.topic, Topic):
            raise ValueError("An explicit typed topic is required")
        if self.topic in COMMAND_TOPICS.values():
            if COMMAND_TOPICS.get(type(self.command)) != self.topic:
                raise ValueError("Command must match its request topic")
        elif self.command is not None:
            raise ValueError("Private commands must not be carried by intermediate/public events")
        if self.topic is Topic.TURN_COMMITTED:
            if (
                self.notice is None
                or self.notice.operation_id != self.operation_id
                or self.notice.event_id != self.id
            ):
                raise ValueError("Completion notice identities must match the event")
        elif self.notice is not None:
            raise ValueError("Completion notice belongs only on its committed topic")


# Educational topology, mirrored by registered handlers. No handler invokes the next inline.
FLOW_EDGES = (
    (Topic.EDITOR_REQUEST, Topic.EDITOR_CONTEXT),
    (Topic.EDITOR_CONTEXT, Topic.EDITOR_CANDIDATE),
    (Topic.TURN_REQUEST, Topic.TURN_CONTEXT),
    (Topic.TURN_CONTEXT, Topic.TURN_PLAN),
    (Topic.TURN_PLAN, Topic.TURN_VALIDATED),
    (Topic.TURN_VALIDATED, Topic.NARRATION),
    (Topic.NARRATION, Topic.TURN_COMMITTED),
    (Topic.RETRY, Topic.TURN_REQUEST),
)
