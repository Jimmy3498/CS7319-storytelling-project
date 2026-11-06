from ..commands import RequestEditorProposal, ReviewEditorProposal
from ..errors import unfinished
from ..models.world import CampaignContent, EditorBuffer, EditorProposal
from ..ports import EditorProposalRepository


class EditorService:
    def __init__(self, repository: EditorProposalRepository) -> None:
        self.repository = repository

    def prepare(self, owner_id: str, command: RequestEditorProposal) -> EditorBuffer:
        """TODO EDITOR: authorize campaign ownership; capture unsaved buffer + local revision.
        Selected records scope the proposal; credential records are never editing targets.
        """
        unfinished("EDITOR")

    def retain_proposal(
        self, owner_id: str, buffer: EditorBuffer, candidate: CampaignContent, summary: str
    ) -> EditorProposal:
        """TODO EDITOR: parse exact schema, validate bounded candidate, retain base revisions.
        Retain for review; preserve the buffer until acceptance.
        """
        unfinished("EDITOR")

    def review(self, owner_id: str, command: ReviewEditorProposal) -> EditorBuffer:
        """TODO EDITOR: reject stale buffer/persisted revision; accept updates buffer only.
        Return unchanged buffer on reject. SaveDraft persists the accepted buffer.
        """
        unfinished("EDITOR")

    def edit_record(self, buffer: EditorBuffer, candidate: CampaignContent) -> EditorBuffer:
        """TODO EDITOR: common manual create/edit/remove path for world records, relations,
        numeric stats, public/private text, rules, stat bands and milestones; increment local
        buffer revision. Block dangling references or show draft errors; never bypass save.
        """
        unfinished("EDITOR")
