from __future__ import annotations

from dataclasses import dataclass

from .evaluator import score_output as _score_output
from .models import AgentGenome, TaskResult


@dataclass
class MockTaskAgent:
    """Task Layer：用 Genome instructions 生成可评分结果。"""

    genome: AgentGenome

    def execute(self, task: str) -> TaskResult:
        output = f"{self.genome.instructions}\n任务：{task}\n结论：先完成最小闭环，再接真实 SDK。"
        score = score_output(output)
        return TaskResult(task=task, output=output, score=score)


@dataclass
class MockOptimizerAgent:
    """Meta/Arch Layer：评估结果，并以保守方式修改 Genome。"""

    min_delta: float = 0.05

    def improve(self, genome: AgentGenome, result: TaskResult) -> tuple[str, AgentGenome]:
        additions: list[str] = []
        if "证据" not in result.output:
            additions.append("每次输出必须包含证据或可复现实验路径。")
        if "下一步" not in result.output:
            additions.append("最后给出下一步行动。")
        if not additions:
            additions.append("保持当前策略，并继续缩短反馈周期。")
        new_text = genome.instructions.rstrip() + " " + " ".join(additions)
        decision = "modify instructions: " + " / ".join(additions)
        return decision, genome.mutated(new_text)


def score_output(text: str) -> float:
    """Deprecated: use selfplay.evaluator.HeuristicEvaluator instead."""
    return _score_output(text)
