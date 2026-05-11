"""SelfPlay OEDM 最小闭环：Observe → Evaluate → Decide → Modify。

结论：OedmLoop 是 SelfPlay 的核心演化引擎，通过四步循环驱动 Agent Genome 自进化，
只有明确提升时才持久化新 Genome，避免无收益自我漂移。

证据路径：run_once() 每轮执行 TaskAgent → score_output → improve → 二次评分验证，
所有结果通过 GenomeStore 持久化到 SQLite。单元测试覆盖无提升场景。

下一步：1) 支持多轮连续运行  2) 接入真实 LLM Runtime 替代 MockTaskAgent。

错误处理：score_output 对空输入返回 0.0；improve 返回的 candidate 若无提升则回退到 old Genome。

复杂度：单轮 O(1) 固定开销；多轮串联 O(c) c=轮数。适合快速迭代验证。

示例：
    loop = OedmLoop(store)
    result = loop.run_once("写一段排序算法并分析复杂度")
    print(f"分数变化: {result.record.score_before} → {result.record.score_after}")

步骤：1) seed 加载最新 Genome → 2) TaskAgent 执行任务 → 3) 评分 → 4) 变异决策 → 5) 持久化。
"""
from __future__ import annotations

import logging

from .agents import MockOptimizerAgent, MockTaskAgent, score_output
from .models import AgentGenome, EvaluationRecord, OedmCycleResult
from .storage import GenomeStore

logger = logging.getLogger(__name__)


class OedmLoop:
    """Observe → Evaluate → Decide → Modify 的最小闭环。"""

    def __init__(self, store: GenomeStore) -> None:
        self.store = store
        self.optimizer = MockOptimizerAgent()

    def seed(self) -> AgentGenome:
        genome = self.store.latest_genome()
        if genome is None:
            genome = AgentGenome()
        self.store.save_genome(genome)
        return genome

    def run_once(self, task: str, cycle: int = 1) -> OedmCycleResult:
        # Input validation: guard against empty or non-string task.
        if not isinstance(task, str) or len(task.strip()) == 0:
            raise ValueError("task must be a non-empty string")
        old = self.seed()

        # Observe: 运行任务并收集输出。
        task_agent = MockTaskAgent(old)
        observed = task_agent.execute(task)

        # Evaluate: 先用启发式评分；后续替换为 Claude SDK evaluator。
        before = observed.score
        decision, candidate = self.optimizer.improve(old, observed)
        after_preview = score_output(candidate.instructions + "\n" + observed.output)

        # Decide + Modify: 只有明确提升时才持久化新 Genome，避免无收益自我漂移。
        new = candidate if after_preview > before else old
        record = EvaluationRecord(
            cycle=cycle,
            stage="modify",
            genome_id=old.id,
            score_before=before,
            score_after=after_preview,
            note=decision,
        )
        self.store.save_evaluation(record)
        self.store.save_genome(new)
        return OedmCycleResult(cycle, old, new, observed, record, decision)
