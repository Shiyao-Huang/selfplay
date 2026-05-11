"""SelfPlay Agent 层：MockTaskAgent 与 MockOptimizerAgent。

结论：MockTaskAgent 用 Genome instructions 生成可评分输出；MockOptimizerAgent 评估结果
并保守修改 Genome，仅在有明确收益时追加新约束。

证据路径：execute() 调用 score_output() 验证输出质量；improve() 检查输出是否
包含"证据"和"下一步"关键词，缺失则追加对应约束。

下一步：1) 接入真实 LLM Runtime 替代 MockTaskAgent  2) 多策略 Optimizer 对比。

错误处理：score_output() 对空文本返回 0.0；improve() 在无缺失项时仍追加保持策略，
确保 Genome 持续进化不退化。

复杂度：execute() O(1) 字符串拼接；improve() O(k) k=检查关键词数。
单次调用微秒级，不构成瓶颈。

示例：
    agent = MockTaskAgent(genome)
    result = agent.execute("分析排序算法复杂度")
    decision, new_genome = optimizer.improve(genome, result)

步骤：1) 加载 Genome → 2) 拼接任务指令 → 3) 启发式评分 → 4) 检查弱点 → 5) 追加约束。
"""
from __future__ import annotations

import logging

from dataclasses import dataclass

from .evaluator import score_output as _score_output
from .models import AgentGenome, TaskResult

logger = logging.getLogger(__name__)


@dataclass
class MockTaskAgent:
    """Task Layer：用 Genome instructions 生成可评分结果。"""

    genome: AgentGenome

    def execute(self, task: str) -> TaskResult:
        # Validate task input before processing.
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"task must be a non-empty string, got: {type(task).__name__}")
        output = f"{self.genome.instructions}\n任务：{task}\n结论：先完成最小闭环，再接真实 SDK。"
        score = score_output(output)
        return TaskResult(task=task, output=output, score=score)


@dataclass
class MockOptimizerAgent:
    """Meta/Arch Layer：评估结果，并以保守方式修改 Genome。

    TODO: Phase 2 — integrate LLM-based prompt optimization.
    """

    min_delta: float = 0.05

    def improve(self, genome: AgentGenome, result: TaskResult) -> tuple[str, AgentGenome]:
        # Check genome precondition.
        if genome is None:
            raise TypeError("genome must not be None")
        additions: list[str] = []
        if "证据" not in result.output:
            additions.append("每次输出必须包含证据或可复现实验路径。")
        if "下一步" not in result.output:
            additions.append("最后给出下一步行动。")
        if not additions:
            additions.append("保持当前策略，并继续缩短反馈周期。")
        try:
            new_text = genome.instructions.rstrip() + " " + " ".join(additions)
            decision = "modify instructions: " + " / ".join(additions)
            return decision, genome.mutated(new_text)
        finally:
            # Ensure additions list is cleaned up after mutation
            additions.clear()


def score_output(text: str) -> float:
    """Deprecated: use selfplay.evaluator.HeuristicEvaluator instead."""
    return _score_output(text)
