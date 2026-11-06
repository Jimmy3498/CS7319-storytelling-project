from shared.domain.services import Services
from shared.errors import unfinished

from .bus import InProcessBus


class CompletionRecovery:
    def __init__(self, services: Services, bus: InProcessBus) -> None:
        self.services, self.bus = services, bus

    def recover(self) -> None:
        """TODO EVENTS/PERSISTENCE: query durable pending committed notices; publish IDs
        with stable event IDs; each result/report consumer deduplicates and acknowledges.
        Mark pre-commit interrupted/unknown provider attempts explicitly; never replay paid
        model requests automatically. This scaffold's queue/status store is not durable.
        """
        unfinished("EVENTS")
