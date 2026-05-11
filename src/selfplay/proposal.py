"""SelfPlay 维度提案与审批流：Strange Loop 自进化机制。

结论：Agent 可基于观察到的弱点自动提出新评估维度，经人类审批后合入活跃 Profile，
实现评估标准的自进化闭环。

证据路径：ProposalStore 基于 JSON 文件持久化，submit/review/list_pending 三步操作
均有对应的单元测试验证状态流转正确性。

下一步：1) 支持批量审批  2) 增加提案理由的 LLM 自动评分。

错误处理：JSON 解析失败时 _load() 返回空列表而非抛异常；review() 找不到提案时返回 None。

复杂度：文件 I/O O(p) p=提案数；内存操作均为线性扫描，适合中小规模使用。

示例：
    store = ProposalStore("data/proposals.json")
    store.submit(DimensionProposal(id="dim_1", label="可读性", rationale="输出需包含结论"))
    store.review("dim_1", approved=True)
    merge_approved_into_profile(profile, store.list_all())

步骤：1) Agent 提交提案 → 2) 人类审批/驳回 → 3) 合入 Profile → 4) 下一轮进化使用新维度。
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import EvaluationDimension, EvaluationProfile

logger = logging.getLogger(__name__)


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
            data = json.loads(self.path.read_text(encoding="utf-8"))
            assert isinstance(data, list), f"Expected list, got {type(data).__name__}"
            return data
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, proposals: list[dict[str, Any]]) -> None:
        self.path.write_text(
            json.dumps(proposals, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def submit(self, proposal: DimensionProposal) -> str:
        """Submit a new proposal. Returns the proposal id."""
        if not proposal.id or not isinstance(proposal.id, str):
            raise ValueError("proposal.id must be a non-empty string")
        proposals = self._load()
        proposals.append(proposal.to_dict())
        self._save(proposals)
        return proposal.id

    def review(self, proposal_id: str, approved: bool, note: str = "") -> DimensionProposal | None:
        """Approve or reject a pending proposal."""
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
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
