from ..errors import unfinished
from ..models.ai import DirectorContext, PlayerView, ProviderCapture
from ..models.gameplay import TurnProposal
from ..models.world import CampaignContent, EditorBuffer
from ..ports import ProviderTransport


class AIService:
    def __init__(self, transport: ProviderTransport) -> None:
        self.transport = transport

    def propose_editor(
        self,
        buffer: EditorBuffer,
        instruction: str,
        selected_ids: tuple[str, ...],
        capture: ProviderCapture,
    ) -> tuple[CampaignContent, str]:
        """TODO PROVIDER/EDITOR: owner-scoped editor context, bounded response schema;
        return candidate and summary, never write a file or execute arbitrary tools.
        """
        unfinished("PROVIDER")

    def plan_turn(self, context: DirectorContext, capture: ProviderCapture) -> TurnProposal:
        """TODO PROVIDER: bounded structured effects and fact IDs; no unrestricted free-text
        'publicProjection' handed to narrator. Unknown fields/types reject; no paid auto-retry.
        """
        unfinished("PROVIDER")

    def narrate(self, view: PlayerView, capture: ProviderCapture) -> str:
        """TODO PROVIDER: render PlayerView in its own context/history.
        Exclude DirectorContext, raw planner text and privileged snapshots.
        """
        unfinished("PROVIDER")
