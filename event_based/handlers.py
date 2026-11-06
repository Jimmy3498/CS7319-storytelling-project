"""Component handlers; no shared whole-turn coordinator or inline subscriber calls.

Small single-capability command paths are wired. Multi-stage editor/gameplay/recovery
handlers intentionally remain explicit pseudocode. See docs/ARCHITECTURE.md.
"""

from uuid import uuid4

from shared.domain.services import Services
from shared.errors import unfinished
from shared.gateway import OperationStatus
from shared.operation_status import OperationStatusStore

from .bus import InProcessBus
from .messages import Message, Topic
from .state import WorkflowStateStore


class ComponentHandlers:
    def __init__(
        self, services: Services, bus: InProcessBus, statuses: OperationStatusStore
    ) -> None:
        self.s, self.bus, self.statuses = services, bus, statuses
        self.state = WorkflowStateStore()

    def next_event(self, source: Message, topic: Topic, work_reference: str) -> None:
        """Queue continuation; do not call another handler directly or carry original command."""
        self.bus.publish(
            Message(
                str(uuid4()),
                source.operation_id,
                source.correlation_id,
                source.id,
                topic,
                source.context,
                work_reference=work_reference,
            )
        )

    def complete(self, message: Message, result: object = None) -> None:
        # TODO PERSISTENCE: durable authorized result receipt, not just this transient status.
        self.statuses.update(
            message.operation_id,
            OperationStatus.COMPLETED,
            "Application operation completed",
            result,
        )

    def account(self, message: Message) -> None:
        if message.topic == Topic.REGISTER:
            result = self.s.accounts.register(message.context, message.command)
        elif message.topic == Topic.LOGIN:
            result = self.s.accounts.login(message.context, message.command)
        else:
            result = self.s.accounts.logout(message.context)
        self.complete(message, result)

    def campaign(self, message: Message) -> None:
        user = self.s.accounts.require_user(message.context)
        action = {
            Topic.CREATE_CAMPAIGN: self.s.world.create,
            Topic.SAVE_DRAFT: self.s.world.save,
            Topic.PUBLISH: self.s.world.publish,
        }[message.topic]
        self.complete(message, action(user.id, message.command))

    def profile(self, message: Message) -> None:
        user = self.s.accounts.require_user(message.context)
        action = {
            Topic.SAVE_CARD: self.s.profiles.save,
            Topic.ACTIVATE_CARD: self.s.profiles.activate,
            Topic.DELETE_CARD: self.s.profiles.delete,
        }[message.topic]
        self.complete(message, action(user.id, message.command))

    def start_session(self, message: Message) -> None:
        user = self.s.accounts.require_user(message.context)
        session = self.s.gameplay.start(user.id, message.command)
        self.complete(message, self.s.knowledge.player_view(session, (), ""))

    def update_session(self, message: Message) -> None:
        user = self.s.accounts.require_user(message.context)
        session = self.s.updates.adopt(user.id, message.operation_id, message.command)
        history = self.s.gameplay.history(user.id, session.id)
        self.complete(message, self.s.knowledge.player_view(session, history, ""))

    def review_editor(self, message: Message) -> None:
        user = self.s.accounts.require_user(message.context)
        self.complete(message, self.s.editor.review(user.id, message.command))

    def editor_requested(self, message: Message) -> None:
        """TODO EVENTS: authenticate -> EditorService.prepare including unsaved local revision
        -> ProfileService.capture -> retain private editor work -> queue EDITOR_CONTEXT with ref.
        No AI request or file write in this handler; stale/unauthorized requests terminate.
        """
        unfinished("EVENTS")

    def editor_model(self, message: Message) -> None:
        """TODO EVENTS: read owned editor work -> AIService.propose_editor -> retain candidate
        and base revision -> queue EDITOR_CANDIDATE. Provider failure is explicit, not replayed.
        """
        unfinished("EVENTS")

    def editor_candidate(self, message: Message) -> None:
        """TODO EVENTS: EditorService.retain_proposal -> authorized proposal result -> cleanup.
        No auto-accept/save/publish. Later EDITOR_REVIEW is a new explicit user command.
        """
        unfinished("EVENTS")

    def turn_requested(self, message: Message) -> None:
        """TODO EVENTS: authenticate -> durable request admission/dedup -> GameplayService.prepare
        -> capture provider config -> retain private TurnWork -> queue TURN_CONTEXT. Serialize
        one in-flight operation per session; no SQL transaction held while awaiting the bus.
        """
        unfinished("EVENTS")

    def director_model(self, message: Message) -> None:
        """TODO EVENTS: retrieve private TurnWork -> KnowledgePolicy.director_context ->
        AIService.plan_turn -> retain typed proposal -> queue TURN_PLAN. No raw planner prose
        or private facts in event payload; failures queue TURN_FAILED with sanitized references.
        """
        unfinished("EVENTS")

    def validate_turn(self, message: Message) -> None:
        """TODO EVENTS: validate_and_project -> authorize_disclosures -> accepted_history ->
        player_view. Store separate NarrationWork (PlayerView + captured config), then queue
        TURN_VALIDATED. Invalid proposals leave accepted state untouched and queue TURN_FAILED.
        """
        unfinished("EVENTS")

    def narrator_model(self, message: Message) -> None:
        """TODO EVENTS: fetch NarrationWork only -> AIService.narrate -> retain bounded text ->
        queue NARRATION. Never fetch full TurnWork/DirectorContext or pass privileged free text.
        """
        unfinished("EVENTS")

    def commit_turn(self, message: Message) -> None:
        """TODO EVENTS: load authorized candidate/text -> GameplayService.commit with revision
        check. Atomic state + transcript + receipt + durable notice first. Then publish
        TURN_COMMITTED containing only CommittedTurnNotice IDs. Commit failure -> TURN_FAILED;
        restart after commit republishes notification, never replays provider call.
        """
        unfinished("EVENTS")

    def result_consumer(self, message: Message) -> None:
        """TODO EVENTS: deduplicate completion, retrieve authorized accepted public result,
        complete caller receipt, acknowledge this consumer, release private work. Do not wait
        for reporting. Result-delivery failure after commit must not label gameplay failed.
        """
        unfinished("EVENTS")

    def report_consumer(self, message: Message) -> None:
        """TODO REPORTS/EVENTS: independent subscriber -> consume_committed_turn(notice),
        acknowledge only after idempotent aggregate/marker update. Leave notice pending on error.
        No player transcript/private-world payload in public reporting or subscriber trace.
        """
        unfinished("REPORTS")

    def failure_consumer(self, message: Message) -> None:
        """TODO EVENTS: durable rejected/failed attempt, uncertain-provider-outcome flag and
        linked retry reference; preserve accepted state, expose safe code, clean private work.
        Reporting reads these attempt records, not just TURN_COMMITTED. Never count TODO stubs
        as real failed gameplay measurements; failure-handler failure must not loop events.
        """
        unfinished("EVENTS")

    def retry(self, message: Message) -> None:
        """TODO EVENTS: authenticate -> GameplayService.retry -> new linked durable attempt;
        if previous committed, return receipt; otherwise queue TURN_REQUEST explicitly.
        Stale late completion is fenced. Never blindly resubmit unknown paid work on restart.
        """
        unfinished("EVENTS")

    def register(self) -> None:
        registrations = {
            Topic.REGISTER: ("accounts", self.account),
            Topic.LOGIN: ("accounts", self.account),
            Topic.LOGOUT: ("accounts", self.account),
            Topic.CREATE_CAMPAIGN: ("campaigns", self.campaign),
            Topic.SAVE_DRAFT: ("campaigns", self.campaign),
            Topic.PUBLISH: ("campaigns", self.campaign),
            Topic.SAVE_CARD: ("profiles", self.profile),
            Topic.ACTIVATE_CARD: ("profiles", self.profile),
            Topic.DELETE_CARD: ("profiles", self.profile),
            Topic.START_SESSION: ("sessions", self.start_session),
            Topic.UPDATE: ("updates", self.update_session),
            Topic.EDITOR_REVIEW: ("editor", self.review_editor),
            Topic.EDITOR_REQUEST: ("editor-context", self.editor_requested),
            Topic.EDITOR_CONTEXT: ("editor-model", self.editor_model),
            Topic.EDITOR_CANDIDATE: ("editor-proposal", self.editor_candidate),
            Topic.TURN_REQUEST: ("gameplay-admission", self.turn_requested),
            Topic.TURN_CONTEXT: ("director-model", self.director_model),
            Topic.TURN_PLAN: ("validation", self.validate_turn),
            Topic.TURN_VALIDATED: ("narrator-model", self.narrator_model),
            Topic.NARRATION: ("persistence", self.commit_turn),
            Topic.TURN_COMMITTED: ("result-consumer", self.result_consumer),
            Topic.TURN_FAILED: ("attempt-history", self.failure_consumer),
            Topic.RETRY: ("retry-admission", self.retry),
        }
        for topic, (name, handler) in registrations.items():
            self.bus.subscribe(topic, name, handler)
        self.bus.subscribe(Topic.TURN_COMMITTED, "report-consumer", self.report_consumer)
