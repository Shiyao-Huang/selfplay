from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol

from .config import EvaluationDimension
from .models import AgentImage, EvalResult, FeatureBreakdown


class Evaluator(Protocol):
    """评估 Agent 输出质量的抽象接口。"""

    async def evaluate(self, task: str, output: str, image: AgentImage) -> EvalResult:
        ...


# Default dimensions matching Phase 1 hardcoded checks (exact parity).
DEFAULT_DIMENSIONS: list[EvaluationDimension] = [
    EvaluationDimension(id="conclusion", label="有短结论", pattern="结论|一句话|summary|conclusion", weight=0.16),
    EvaluationDimension(id="evidence", label="有证据路径", keywords=["证据", "路径", "验证", "evidence"], weight=0.16),
    EvaluationDimension(id="next_step", label="有下一步", keywords=["下一步", "next"], weight=0.12),
    EvaluationDimension(id="error_handling", label="覆盖错误处理", keywords=["错误", "边界", "异常", "edge"], weight=0.14),
    EvaluationDimension(id="performance", label="覆盖复杂度/性能", keywords=["复杂度", "性能", "performance"], weight=0.12),
    EvaluationDimension(id="examples", label="包含示例", keywords=["示例", "样例", "example"], weight=0.10),
    EvaluationDimension(id="structure", label="结构清晰", keywords=["步骤", "结构", "分层"], weight=0.10),
    EvaluationDimension(id="length", label="信息量足够", type="length", min_length=80, weight=0.10),
]


def _check_dimension(dim: EvaluationDimension, text: str, output: str) -> FeatureBreakdown:
    """Evaluate a single dimension and return breakdown."""
    matched = False
    evidence = "not_found"

    if dim.type == "length":
        passed = len(output) >= dim.min_length
        evidence = f"length={len(output)}" if passed else f"length={len(output)} < {dim.min_length}"
    else:
        # Check pattern first, then keywords — both can contribute
        if dim.pattern:
            match = re.search(dim.pattern, text, re.IGNORECASE)
            if match:
                matched = True
                evidence = f"matched_pattern: {match.group()[:60]}"
        if not matched and dim.keywords:
            for kw in dim.keywords:
                if kw.lower() in text.lower():
                    matched = True
                    evidence = f"matched_keyword: {kw}"
                    break
        if not matched and not dim.pattern and not dim.keywords:
            evidence = "no_pattern_or_keywords"

    passed = matched if dim.type != "length" else len(output) >= dim.min_length
    return FeatureBreakdown(
        id=dim.id,
        label=dim.label,
        passed=passed,
        score=0.0,  # filled by caller after normalization
        raw_weight=dim.weight,
        effective_weight=0.0,  # filled by caller after normalization
        evidence=evidence[:80],
    )


@dataclass
class HeuristicEvaluator:
    """Zero-dependency evaluator used by mock mode and tests."""

    min_length: int = 80
    dimensions: list[EvaluationDimension] | None = None

    async def evaluate(self, task: str, output: str, image: AgentImage) -> EvalResult:
        return self.evaluate_text(task, output)

    def evaluate_text(self, task: str, output: str) -> EvalResult:
        dims = self.dimensions if self.dimensions else DEFAULT_DIMENSIONS
        text = f"{task}\n{output}"

        # Compute per-feature breakdowns.
        breakdowns = [_check_dimension(d, text, output) for d in dims]

        # Normalize weights across enabled dimensions.
        total_weight = sum(b.raw_weight for b in breakdowns)
        if total_weight > 0:
            for b in breakdowns:
                b.effective_weight = round(b.raw_weight / total_weight, 4)
                b.score = round(b.effective_weight, 4) if b.passed else 0.0

        score = round(sum(b.score for b in breakdowns), 2)
        score = min(score, 1.0)

        strengths: list[str] = []
        weaknesses: list[str] = []
        for b in breakdowns:
            (strengths if b.passed else weaknesses).append(b.label)

        suggestion = "；".join(
            [f"缺少{b.label}" for b in breakdowns if not b.passed][:3]
        ) or "保持当前策略，并缩短反馈周期。"

        return EvalResult(
            score=score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestion=suggestion,
            rationale="heuristic feature coverage",
            features=breakdowns,
        )


def score_output(text: str) -> float:
    """Deprecated compatibility helper; prefer HeuristicEvaluator.evaluate()."""
    return HeuristicEvaluator().evaluate_text("", text).score


@dataclass
class ClaudeEvaluator:
    """Optional LLM evaluator skeleton. Requires a real Claude SDK installation."""

    model_hint: str = "claude"

    async def evaluate(self, task: str, output: str, image: AgentImage) -> EvalResult:
        try:
            from claude_agent_sdk import ClaudeAgentOptions, query  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "ClaudeEvaluator requires the optional Claude Agent SDK. "
                "Install a verified Claude SDK package/API and keep "
                "selfplay[sdk] optional deps enabled."
            ) from exc
        prompt = (
            "Evaluate this agent output as JSON with keys score, strengths, "
            "weaknesses, suggestion. Score must be 0.0-1.0.\n"
            f"Task: {task}\nAgent prompt: {image.prompt}\nOutput:\n{output}"
        )
        options = ClaudeAgentOptions(
            system_prompt="You are a strict structured evaluator.",
            max_turns=1,
        )
        chunks: list[str] = []
        async for message in query(prompt=prompt, options=options):  # pragma: no cover
            if type(message).__name__ == "AssistantMessage":
                for block in getattr(message, "content", []) or []:
                    text = getattr(block, "text", None)
                    if text:
                        chunks.append(str(text))
        try:
            data = json.loads("\n".join(chunks))
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("ClaudeEvaluator did not return valid JSON") from exc
        return EvalResult(
            score=float(data.get("score", 0.0)),
            strengths=list(data.get("strengths", [])),
            weaknesses=list(data.get("weaknesses", [])),
            suggestion=str(data.get("suggestion", "")),
            rationale="claude structured evaluator",
        )


@dataclass
class CompositeEvaluator:
    """Heuristic first; optionally ask LLM only for weak outputs."""

    heuristic: Evaluator
    llm: Evaluator | None = None
    llm_threshold: float = 0.65
    enable_llm: bool = False

    async def evaluate(self, task: str, output: str, image: AgentImage) -> EvalResult:
        first = await self.heuristic.evaluate(task, output, image)
        if not self.enable_llm or self.llm is None or first.score >= self.llm_threshold:
            return first
        try:
            return await self.llm.evaluate(task, output, image)
        except Exception as exc:
            first.rationale = f"{first.rationale}; llm fallback unavailable: {exc}"
            return first
