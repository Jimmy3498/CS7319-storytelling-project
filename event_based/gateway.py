from dataclasses import replace
from uuid import uuid4

from shared.commands import Command
from shared.domain.services import Services
from shared.errors import ApplicationError, ErrorCode
from shared.gateway import OperationReceipt
from shared.models.common import RequestContext
from shared.operation_status import OperationStatusStore
from shared.queries import Query

from .bus import InProcessBus
from .handlers import ComponentHandlers
from .messages import COMMAND_TOPICS, Message, Topic


class EventGateway:
    architecture = "Event-Based"

    def __init__(self, services: Services, start_worker: bool = True) -> None:
        self.services = services
        self.statuses = OperationStatusStore()
        self.subscriber_failures: list[tuple[str, str]] = []
        self.bus = InProcessBus(self._failed)
        self.handlers = ComponentHandlers(services, self.bus, self.statuses)
        self.handlers.register()
        if start_worker:
            self.bus.start()

    def _failed(self, message: Message, component: str, error: Exception) -> None:
        if message.topic == Topic.TURN_COMMITTED:
            # A downstream subscriber is not allowed to relabel committed gameplay as failed.
            self.subscriber_failures.append((component, message.operation_id))
            return
        self.statuses.fail(message.operation_id, error)

    def submit(
        self, context: RequestContext, command: Command, request_id: str
    ) -> OperationReceipt:
        topic = COMMAND_TOPICS.get(type(command))
        if topic is None:
            raise ApplicationError(ErrorCode.INVALID, "Unknown command type")
        receipt, fresh = self.statuses.begin(context, request_id, command)
        if fresh:
            self.bus.publish(
                Message(
                    str(uuid4()),
                    receipt.operation_id,
                    context.correlation_id,
                    None,
                    topic,
                    replace(context, request_id=request_id),
                    command=command,
                )
            )
        return receipt  # No inline handler or provider execution.

    def poll(self, context: RequestContext, operation_id: str) -> OperationReceipt:
        return self.statuses.read(context, operation_id)

    def query(self, context: RequestContext, query: Query) -> object:
        # Read-only projections need not make round trips through the mutation bus.
        return self.services.queries.read(context, query)

    def close(self) -> None:
        self.bus.close()
