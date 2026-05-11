"""Self-evolving dimension proposal and approval flow.

An Agent can propose new evaluation dimensions based on observed weaknesses.
Proposals are stored on disk for human review. Approved proposals are merged
into the active evaluation profile. Rejected proposals are recorded for audit.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import EvaluationDimension, EvaluationProfile


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DimensionProposal:
    """A proposed new evaluation dimension from an agent."""

    id: str
    label: str
    rationale: str
    keywords: list[str] = field(default_factory=list)
    pattern: str = ""
    weight: float = 0.10
    type: str = "keyword"
    min_length: int = 80
    proposed_by: str = ""
    created_at: str = field(default_factory=utc_now)
    status: str = "pending"  # "pending" | "approved" | "rejected"
    reviewed_at: str | None = None
    review_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProposalStore:
    """File-based store for dimension proposals."""

    def __init__(self, path: str | Path = "data/proposals.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, proposals: list[dict[str, Any]]) -> None:
        self.path.write_text(
            json.dumps(proposals, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def submit(self, proposal: DimensionProposal) -> str:
        """Submit a new proposal. Returns the proposal id."""
        proposals = self._load()
        proposals.append(proposal.to_dict())
        self._save(proposals)
        return proposal.id

    def review(self, proposal_id: str, approved: bool, note: str = "") -> DimensionProposal | None:
        """Approve or reject a pending proposal."""
        proposals = self._load()
        for p in proposals:
            if p["id"] == proposal_id and p["status"] == "pending":
                p["status"] = "approved" if approved else "rejected"
                p["reviewed_at"] = utc_now()
                p["review_note"] = note
                self._save(proposals)
                return DimensionProposal(**p)
        return None

    def list_pending(self) -> list[DimensionProposal]:
        return [DimensionProposal(**p) for p in self._load() if p["status"] == "pending"]

    def list_all(self) -> list[DimensionProposal]:
        return [DimensionProposal(**p) for p in self._load()]


def proposal_to_dimension(proposal: DimensionProposal) -> EvaluationDimension:
    """Convert an approved proposal into an EvaluationDimension."""
    return EvaluationDimension(
        id=proposal.id,
        label=proposal.label,
        pattern=proposal.pattern,
        keywords=proposal.keywords,
        weight=proposal.weight,
        type=proposal.type,
        min_length=proposal.min_length,
    )


def merge_approved_into_profile(
    profile: EvaluationProfile,
    proposals: list[DimensionProposal],
) -> EvaluationProfile:
    """Merge approved proposals into a profile as new dimensions."""
    approved = [p for p in proposals if p.status == "approved"]
    if not approved:
        return profile
    existing_ids = {d.id for d in profile.dimensions}
    new_dims = []
    for p in approved:
        if p.id not in existing_ids:
            new_dims.append(proposal_to_dimension(p))
    return EvaluationProfile(
        id=profile.id,
        version=profile.version + 1,
        dimensions=profile.dimensions + new_dims,
    )
