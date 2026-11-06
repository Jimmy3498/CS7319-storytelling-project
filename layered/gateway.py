from dataclasses import replace

from shared.commands import COMMAND_TYPES, Command
from shared.errors import ApplicationError, ErrorCode
from shared.gateway import OperationReceipt, OperationStatus
from shared.models.common import RequestContext
from shared.operation_status import OperationStatusStore
from shared.queries import Query

from .application import LayeredApplication


class LayeredGateway:
    architecture = "Layered"

    def __init__(self, application: LayeredApplication) -> None:
        self.application = application
        self.statuses = OperationStatusStore()

    def submit(
        self, context: RequestContext, command: Command, request_id: str
    ) -> OperationReceipt:
        if type(command) not in COMMAND_TYPES:
            raise ApplicationError(ErrorCode.INVALID, "Unknown command type")
        receipt, fresh = self.statuses.begin(context, request_id, command)
        if not fresh:
            return receipt
        self.statuses.update(receipt.operation_id, OperationStatus.RUNNING, "Executing layer calls")
        try:
            result = self.application.execute(
                replace(context, request_id=request_id), command, receipt.operation_id
            )
            return self.statuses.update(
                receipt.operation_id,
                OperationStatus.COMPLETED,
                "Application operation completed",
                result,
            )
        except Exception as error:
            return self.statuses.fail(receipt.operation_id, error)

    def poll(self, context: RequestContext, operation_id: str) -> OperationReceipt:
        return self.statuses.read(context, operation_id)

    def query(self, context: RequestContext, query: Query) -> object:
        return self.application.services.queries.read(context, query)

    def close(self) -> None:
        pass  # No worker exists in the Layered host.
