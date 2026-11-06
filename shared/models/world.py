from dataclasses import dataclass

from .common import Access, Condition


@dataclass(frozen=True)
class TextRecord:
    id: str
    title: str
    text: str
    access: Access
    # None means no automatic public release, not freely disclosable.
    reveal_when: Condition | None = None
    stance: str = "authored_fact"  # authored_fact, belief, claim; validation is WORLD/PRIVACY.
    holder_id: str | None = None


@dataclass(frozen=True)
class NumericStat:
    id: str
    name: str
    value: float
    minimum: float
    maximum: float
    access: Access


@dataclass(frozen=True)
class StatBand:
    stat_id: str
    minimum: float
    maximum: float
    text: str


@dataclass(frozen=True)
class Character:
    id: str
    name: str
    playable: bool
    location_id: str
    appearance: TextRecord
    expression_style: TextRecord
    personality: TextRecord
    personal_history: TextRecord
    knowledge: tuple[TextRecord, ...]
    stats: tuple[NumericStat, ...]


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    description: TextRecord
    connected_location_ids: tuple[str, ...]


@dataclass(frozen=True)
class ItemTemplate:
    id: str
    name: str
    description: TextRecord
    spawn_when: Condition | None  # None: not runtime-spawnable.
    max_instances_per_session: int


@dataclass(frozen=True)
class ItemInstance:
    id: str
    template_id: str
    # Exactly one holder/location must be set; these are known IDs, not arbitrary paths.
    holder_id: str | None
    location_id: str | None
    access: Access
    discover_when: Condition | None = None


@dataclass(frozen=True)
class Relationship:
    id: str
    source_id: str
    target_id: str
    label: str
    description: TextRecord
    stats: tuple[NumericStat, ...]


@dataclass(frozen=True)
class FlagDefinition:
    id: str
    label: str
    initial: bool
    set_when: Condition | None
    access: Access


@dataclass(frozen=True)
class MilestoneDefinition:
    id: str
    label: str
    condition: Condition
    # Derived from normalized definition; do not pool changed meanings across versions.
    definition_fingerprint: str


@dataclass(frozen=True)
class WorldDefinition:
    canon: tuple[TextRecord, ...]
    characters: tuple[Character, ...]
    locations: tuple[Location, ...]
    item_templates: tuple[ItemTemplate, ...]
    items: tuple[ItemInstance, ...]
    relationships: tuple[Relationship, ...]
    flags: tuple[FlagDefinition, ...]
    narrative_rules: tuple[TextRecord, ...]
    stat_bands: tuple[StatBand, ...]
    milestones: tuple[MilestoneDefinition, ...]


@dataclass(frozen=True)
class CampaignContent:
    title: str
    summary: str
    background: TextRecord
    opening: TextRecord
    world: WorldDefinition


@dataclass(frozen=True)
class CampaignDraft:
    id: str
    owner_id: str
    revision: int
    content: CampaignContent


@dataclass(frozen=True)
class PublishedCampaign:
    id: str
    campaign_id: str
    owner_id: str
    version: int
    content: CampaignContent


@dataclass(frozen=True)
class CatalogEntry:
    """Explicit public DTO. Catalog never returns the complete world document."""

    campaign_id: str
    published_version_id: str
    title: str
    summary: str
    version: int
    playable_character_names: tuple[str, ...]


@dataclass(frozen=True)
class EditorBuffer:
    campaign_id: str
    persisted_revision: int
    local_revision: int
    content: CampaignContent


@dataclass(frozen=True)
class EditorProposal:
    id: str
    campaign_id: str
    base_persisted_revision: int
    base_buffer_revision: int
    summary: str
    candidate: CampaignContent
