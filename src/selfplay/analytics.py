"""Evolution analytics: compute metrics from evaluation history."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .storage import GenomeStore


@dataclass
class ConvergenceMetrics:
    """How quickly does the agent reach threshold?"""
    cycles_to_threshold: int | None  # None = never reached
    total_cycles: int
    total_improvement: float
    improvement_rate: float  # avg improvement per cycle
    early_stop_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MutationMetrics:
    """How effective are mutations?"""
    total_mutations: int
    accepted_mutations: int
    rejected_mutations: int
    acceptance_rate: float  # accepted / total
    avg_score_gain_per_mutation: float
    avg_score_loss_per_rejection: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DimensionTrend:
    """Improvement trend for a single evaluation dimension."""
    dimension_id: str
    label: str
    pass_rate: float  # fraction of cycles where this dim passed
    avg_score_contribution: float
    trend: str  # "improving" | "stable" | "declining"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvolutionAnalytics:
    """Full analytics snapshot for an evolution run."""
    convergence: ConvergenceMetrics
    mutations: MutationMetrics
    dimension_trends: list[DimensionTrend] = field(default_factory=list)
    score_trajectory: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "convergence": self.convergence.to_dict(),
            "mutations": self.mutations.to_dict(),
            "dimension_trends": [d.to_dict() for d in self.dimension_trends],
            "score_trajectory": self.score_trajectory,
        }


def compute_analytics(store: GenomeStore, limit: int = 100) -> EvolutionAnalytics:
    """Compute analytics from the evaluation history in the store."""
    records = store.recent_evaluations(limit)

    if not records:
        return EvolutionAnalytics(
            convergence=ConvergenceMetrics(
                cycles_to_threshold=None, total_cycles=0,
                total_improvement=0.0, improvement_rate=0.0, early_stop_count=0,
            ),
            mutations=MutationMetrics(
                total_mutations=0, accepted_mutations=0, rejected_mutations=0,
                acceptance_rate=0.0, avg_score_gain_per_mutation=0.0,
                avg_score_loss_per_rejection=0.0,
            ),
        )

    # Convergence metrics
    total_cycles = len(records)
    scores_before = [r["score_before"] for r in records]
    scores_after = [r["score_after"] for r in records if r.get("score_after") is not None]
    all_scores = [s for s in scores_before + scores_after if s is not None]

    first_score = scores_before[0] if scores_before else 0.0
    last_score = scores_after[-1] if scores_after else (scores_before[-1] if scores_before else 0.0)
    total_improvement = round(last_score - first_score, 4)
    improvement_rate = round(total_improvement / max(1, total_cycles), 4)

    # Find threshold crossing
    threshold = 0.9
    cycles_to_threshold = None
    early_stop_count = 0
    for i, r in enumerate(records):
        sb = r.get("score_before", 0)
        if sb >= threshold:
            cycles_to_threshold = i + 1
            early_stop_count += 1

    convergence = ConvergenceMetrics(
        cycles_to_threshold=cycles_to_threshold,
        total_cycles=total_cycles,
        total_improvement=total_improvement,
        improvement_rate=improvement_rate,
        early_stop_count=early_stop_count,
    )

    # Mutation metrics
    stages = [r.get("stage", "") for r in records]
    total_mutations = stages.count("modify")
    accepted = total_mutations  # "modify" stage = mutation was applied
    rejected = total_cycles - accepted  # "evaluate" stage = no mutation
    acceptance_rate = round(accepted / max(1, total_cycles), 4)

    # Score gains/losses
    gains: list[float] = []
    losses: list[float] = []
    for r in records:
        sb = r.get("score_before", 0)
        sa = r.get("score_after")
        if sa is not None and sb is not None:
            delta = sa - sb
            if r.get("stage") == "modify" and delta > 0:
                gains.append(delta)
            elif r.get("stage") == "evaluate" and sa < threshold:
                pass  # no mutation applied

    avg_gain = round(sum(gains) / max(1, len(gains)), 4) if gains else 0.0
    avg_loss = round(sum(losses) / max(1, len(losses)), 4) if losses else 0.0

    mutations = MutationMetrics(
        total_mutations=total_mutations,
        accepted_mutations=accepted,
        rejected_mutations=rejected,
        acceptance_rate=acceptance_rate,
        avg_score_gain_per_mutation=avg_gain,
        avg_score_loss_per_rejection=avg_loss,
    )

    # Dimension trends
    dim_stats: dict[str, dict[str, Any]] = {}
    for r in records:
        features = r.get("features", [])
        if not isinstance(features, list):
            continue
        for f in features:
            if not isinstance(f, dict):
                continue
            fid = f.get("id", "")
            if not fid:
                continue
            if fid not in dim_stats:
                dim_stats[fid] = {
                    "id": fid,
                    "label": f.get("label", fid),
                    "passed_count": 0,
                    "total_count": 0,
                    "score_contributions": [],
                }
            dim_stats[fid]["total_count"] += 1
            if f.get("passed"):
                dim_stats[fid]["passed_count"] += 1
            sc = f.get("score", 0.0)
            dim_stats[fid]["score_contributions"].append(sc)

    dim_trends: list[DimensionTrend] = []
    for fid, stats in dim_stats.items():
        total = max(1, stats["total_count"])
        pass_rate = round(stats["passed_count"] / total, 4)
        scores_list = stats["score_contributions"]
        avg_sc = round(sum(scores_list) / max(1, len(scores_list)), 4)

        # Determine trend: compare first half vs second half
        mid = len(scores_list) // 2
        if mid > 0 and len(scores_list) >= 2:
            first_half_avg = sum(scores_list[:mid]) / mid
            second_half_avg = sum(scores_list[mid:]) / max(1, len(scores_list) - mid)
            if second_half_avg > first_half_avg + 0.01:
                trend = "improving"
            elif second_half_avg < first_half_avg - 0.01:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        dim_trends.append(DimensionTrend(
            dimension_id=fid,
            label=stats["label"],
            pass_rate=pass_rate,
            avg_score_contribution=avg_sc,
            trend=trend,
        ))

    # Score trajectory
    trajectory: list[float] = []
    for r in records:
        sa = r.get("score_after")
        trajectory.append(sa if sa is not None else r.get("score_before", 0.0))

    return EvolutionAnalytics(
        convergence=convergence,
        mutations=mutations,
        dimension_trends=dim_trends,
        score_trajectory=trajectory,
    )


def suggest_dimensions(
    store: GenomeStore,
    analytics: EvolutionAnalytics | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Auto-suggest new evaluation dimensions based on weakness patterns.

    This is the Strange Loop core: the system proposes new evaluation criteria
    based on what it consistently fails at, creating a self-referential improvement
    loop where the evaluation standard itself evolves.
    """
    if analytics is None:
        analytics = compute_analytics(store, limit=limit)

    suggestions: list[dict[str, Any]] = []

    # Strategy 1: Declining dimensions need remediation
    for d in analytics.dimension_trends:
        if d.trend == "declining" and d.pass_rate < 0.5:
            suggestions.append({
                "id": f"{d.dimension_id}_remediation",
                "label": f"{d.label}（强化）",
                "keywords": [],
                "pattern": "",
                "weight": 0.05,
                "type": "keyword",
                "rationale": (
                    f"Dimension '{d.label}' declining (pass_rate={d.pass_rate:.0%}). "
                    f"Propose remediation sub-dimension to focus evolution."
                ),
                "source": "strange_loop:declining_dimension",
            })

    # Strategy 2: Persistent zero-pass dimensions
    for d in analytics.dimension_trends:
        if d.pass_rate == 0.0 and d.trend == "stable":
            suggestions.append({
                "id": f"{d.dimension_id}_alternative",
                "label": f"{d.label}（替代检测）",
                "keywords": [],
                "pattern": "",
                "weight": d.avg_score_contribution or 0.05,
                "type": "keyword",
                "rationale": (
                    f"Dimension '{d.label}' never passes. "
                    f"Current keywords/pattern may not match mock output. "
                    f"Suggest alternative detection strategy."
                ),
                "source": "strange_loop:zero_pass_dimension",
            })

    # Strategy 3: Low convergence suggests missing dimensions
    if analytics.convergence.cycles_to_threshold is None and analytics.convergence.total_cycles >= 5:
        suggestions.append({
            "id": "convergence_driver",
            "label": "收敛驱动器",
            "keywords": ["收敛", "达标", "threshold"],
            "pattern": "",
            "weight": 0.10,
            "type": "keyword",
            "rationale": (
                f"System never reached threshold in {analytics.convergence.total_cycles} cycles. "
                f"Propose convergence-focused dimension to drive evolution direction."
            ),
            "source": "strange_loop:low_convergence",
        })

    return suggestions
