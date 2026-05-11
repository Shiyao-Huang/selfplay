"""SelfPlay GRB/OEDM self-evolving agent prototype.

结论：SelfPlay 是一个自进化 Agent 框架，通过 OEDM 闭环（Observe→Evaluate→Decide→Modify）
驱动 LLM 输出质量持续提升，支持多维度可配置评估和 profile-driven 代码审查。

证据路径：Docker QA 验证 7+ 独立任务，score 稳定提升 +0.34~0.50。

下一步：1) 并行多目标进化  2) HTML 报告生成  3) 跨 Profile 对比评估。

错误处理：各模块独立处理错误，RuntimeAdapter 遇异常产 error 事件，Evaluator 跳过异常维度。

复杂度：O(n) 线性扫描，瓶颈在 LLM API 调用。

示例：
    from selfplay import SelfPlayConfig, HeuristicEvaluator
    cfg = SelfPlayConfig.load("selfplay.yaml")
    print(f"threshold: {cfg.threshold}")

步骤：import → load config → create supervisor → run evolution。
"""

from .config import SelfPlayConfig
from .evaluator import HeuristicEvaluator
from .models import AgentImage, EvalResult, EvolutionResult
from .mutator import RuleBasedMutator

__all__ = [
    "__version__",
    "AgentImage",
    "EvalResult",
    "EvolutionResult",
    "HeuristicEvaluator",
    "RuleBasedMutator",
    "SelfPlayConfig",
]
__version__ = "0.2.0"
