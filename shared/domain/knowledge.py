from ..errors import unfinished
from ..models.ai import DirectorContext, PlayerView
from ..models.gameplay import AcceptedTurn, SessionSnapshot, TurnProposal


class KnowledgePolicy:
    def director_context(self, session: SessionSnapshot, player_input: str) -> DirectorContext:
        """TODO PRIVACY: construct explicit privileged planning context; no credential data.
        Use this session's history; exclude editor and global chat histories.
        """
        unfinished("PRIVACY")

    def authorize_disclosures(
        self, before: SessionSnapshot, candidate: SessionSnapshot, proposal: TurnProposal
    ) -> SessionSnapshot:
        """TODO PRIVACY: authorize disclosure through authored reveal conditions and recipients.
        Deny missing policy/labels. Preserve belief and claim attribution.
        """
        unfinished("PRIVACY")

    def player_view(
        self, session: SessionSnapshot, history: tuple[AcceptedTurn, ...], player_input: str
    ) -> PlayerView:
        """TODO PRIVACY: admit only available public/PC-held/explicitly disclosed records.
        Apply location/discovery scope, including for the campaign author's playthrough.
        Exclude raw planner prose, full snapshots, other actors' private data and other sessions.
        """
        unfinished("PRIVACY")
