"""Caller-authorized result DTOs. No raw runtime world or credential capture in player results."""

from dataclasses import dataclass

from .gameplay import AcceptedTurn


@dataclass(frozen=True)
class TurnResultView:
    turn: AcceptedTurn
    reporting_pending: bool | None  # None means not rechecked, not a measured failure.


@dataclass(frozen=True)
class CampaignSummary:
    id: str
    title: str
    draft_revision: int
    published_version_id: str | None


@dataclass(frozen=True)
class UpdatePreviewView:
    session_id: str
    old_version_id: str
    target_version_id: str
    can_adopt: bool
    conflict_codes: tuple[
        str, ...
    ]  # controlled categories, never private names or raw MergeConflict text.
