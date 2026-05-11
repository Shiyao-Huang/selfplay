from __future__ import annotations

from .agents import MockOptimizerAgent, MockTaskAgent, score_output
from .models import AgentGenome, EvaluationRecord, OedmCycleResult
from .storage import GenomeStore


class OedmLoop:
    """Observe → Evaluate → Decide → Modify 的最小闭环。"""

    def __init__(self, store: GenomeStore) -> None:
        self.store = store
        self.optimizer = MockOptimizerAgent()

    def seed(self) -> AgentGenome:
        genome = self.store.latest_genome() or AgentGenome()
        self.store.save_genome(genome)
        return genome

    def run_once(self, task: str, cycle: int = 1) -> OedmCycleResult:
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
