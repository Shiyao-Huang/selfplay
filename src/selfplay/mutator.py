from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import DEFAULT_MAX_PROMPT_LENGTH, AgentImage, EvalResult, compress_prompt


class Mutator(Protocol):
    """基于评估结果修改 AgentImage 的抽象接口。"""

    async def mutate(self, image: AgentImage, eval_result: EvalResult) -> AgentImage | None:
        """Return None when no modification is needed."""
        ...


@dataclass
class RuleBasedMutator:
    """Zero-dependency prompt rewriter driven by EvalResult, not raw output rules."""

    threshold: float = 0.9
    max_prompt_length: int = DEFAULT_MAX_PROMPT_LENGTH
    max_focus_items: int = 3
    max_total_items: int = 6

    async def mutate(self, image: AgentImage, eval_result: EvalResult) -> AgentImage | None:
        if eval_result.score >= self.threshold:
            return None
        if not eval_result.weaknesses and not eval_result.suggestion:
            return None
        new_prompt = self.rewrite_prompt(image.prompt, eval_result)
        if new_prompt == compress_prompt(image.prompt, self.max_prompt_length):
            return None
        gain = 0.12 * min(self.max_focus_items, max(1, len(eval_result.weaknesses)))
        score_after = round(min(1.0, eval_result.score + gain), 2)
        rationale = "modify prompt from eval_result: " + eval_result.summary()
        child = image.mutated_prompt(new_prompt, score_after, rationale, self.max_prompt_length)
        child.memory.evaluation_history.append(
            {
                "score_before": eval_result.score,
                "score_after": score_after,
                "weaknesses": eval_result.weaknesses,
                "suggestion": eval_result.suggestion,
                "decision": rationale,
            }
        )
        return child

    def rewrite_prompt(self, prompt: str, eval_result: EvalResult) -> str:
        marker = "进化约束："
        base = compress_prompt(prompt, self.max_prompt_length)
        lines = [part.strip() for part in base.split("。") if part.strip()]
        existing: list[str] = []
        kept: list[str] = []
        tail = "保持短结论和证据，随后补充本轮评估指出的改进项"
        for line in lines:
            if line.startswith(marker):
                body = line.replace(marker, "", 1).replace("下一次输出必须改善：", "")
                existing.extend(item.strip() for item in body.split("；") if item.strip())
            elif line != tail:
                kept.append(line)
        # Phase 2.2: use structured failed feature labels when available.
        if eval_result.features:
            failed_labels = [f.label for f in eval_result.features if not f.passed]
            focus = failed_labels[:self.max_focus_items]
        else:
            focus = list(eval_result.weaknesses[:self.max_focus_items])
        for item in eval_result.suggestion.split("；"):
            if item and item not in focus and len(focus) < self.max_focus_items:
                focus.append(item)
        merged = list(dict.fromkeys(item.strip() for item in existing + focus if item.strip()))
        guidance = "；".join(merged[-self.max_total_items:])
        if not guidance:
            return compress_prompt(prompt, self.max_prompt_length)
        kept.append(f"{marker}下一次输出必须改善：{guidance}")
        kept.append(tail)
        return compress_prompt("。".join(kept) + "。", self.max_prompt_length)


@dataclass
class PromptMutator:
    """Optional LLM prompt optimizer skeleton."""

    fallback: RuleBasedMutator

    async def mutate(self, image: AgentImage, eval_result: EvalResult) -> AgentImage | None:
        # Phase 1 keeps mock mode zero-dependency. Real LLM rewrite can replace this method.
        return await self.fallback.mutate(image, eval_result)
