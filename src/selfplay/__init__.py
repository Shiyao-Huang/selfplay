"""SelfPlay GRB/OEDM self-evolving agent prototype."""

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
