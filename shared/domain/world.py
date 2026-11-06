from ..commands import CreateCampaign, PublishCampaign, SaveDraft
from ..errors import unfinished
from ..models.common import Issue
from ..models.world import CampaignContent, CampaignDraft, CatalogEntry
from ..ports import CampaignRepository


class WorldService:
    def __init__(self, repository: CampaignRepository) -> None:
        self.repository = repository

    def create(self, owner_id: str, command: CreateCampaign) -> CampaignDraft:
        """TODO WORLD: create a private incomplete draft. Creation is not publication."""
        unfinished("WORLD")

    def save(self, owner_id: str, command: SaveDraft) -> CampaignDraft:
        """TODO WORLD: ownership/revision and safe typed-shape checks; incomplete is saveable.
        Preserve caller edits on conflict. Do not auto-publish, call AI, or rewrite sessions.
        """
        unfinished("WORLD")

    def readiness(self, content: CampaignContent) -> tuple[Issue, ...]:
        """TODO WORLD: setup, preset PC/start, referential/state validity, explicit access,
        valid closed conditions/stat bands/templates. No AI quality-score gate.
        """
        unfinished("WORLD")

    def publish(self, owner_id: str, command: PublishCampaign) -> CatalogEntry:
        """TODO WORLD: load owned draft, readiness, atomic immutable published revision.
        Existing sessions remain pinned; return public catalog DTO only.
        """
        unfinished("WORLD")
