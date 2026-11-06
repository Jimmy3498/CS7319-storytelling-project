from dataclasses import dataclass


@dataclass(frozen=True)
class MilestoneCount:
    marker_id: str
    definition_fingerprint: str
    label: str
    playthrough_count: int
    distinct_account_count: int
    eligible_playthroughs: int
    eligible_accounts: int


@dataclass(frozen=True)
class CampaignReport:
    campaign_id: str
    published_version_id: str | None
    started_playthroughs: int
    accepted_turns: int
    rejected_turns: int
    failed_turns: int
    last_activity: str | None
    projection_as_of: str | None
    milestones: tuple[MilestoneCount, ...]
