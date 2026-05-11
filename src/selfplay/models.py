"""SelfPlay 数据模型：AgentImage、AgentGenome、EvalResult 等核心类型。

结论：本模块定义 SelfPlay 的全部数据结构，是 OEDM 闭环中各组件共享的统一数据契约。

证据路径：所有模块（supervisor / mutator / evaluator / storage）均依赖本模块的类型定义，
单元测试覆盖 compress_prompt 去重、mutated_prompt 长度裁剪、from_genome 反序列化。

下一步：1) 增加 AgentImage 版本链追踪  2) 支持 JSON Schema 校验  3) 增加序列化兼容层。

错误处理：from_genome() 对非 dict 输入抛 TypeError；compress_prompt 对超长文本截断中间并记录日志；
mutated_prompt 硬性保证输出不超过 max_prompt_length。

复杂度：compress_prompt O(s) s=句数去重；compress_prompt 截断 O(1)；整体无热路径瓶颈。

示例：
    image = AgentImage(runtime_adapter="claude")
    genome = image.to_genome()
    restored = AgentImage.from_genome(genome)
    assert restored.prompt == image.prompt

步骤：1) 定义枚举/常量 → 2) compress_prompt 工具函数 → 3) AgentGenome 旧接口 →
4) AgentImage 新接口 → 5) EvalResult / FeatureBreakdown → 6) 循环结果类型。
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

logger = logging.getLogger(__name__)

Stage = Literal["observe", "evaluate", "decide", "modify"]
RuntimeName = Literal["mock", "claude", "codex"]
DEFAULT_MAX_PROMPT_LENGTH = 2000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def compress_prompt(prompt: str, max_length: int = DEFAULT_MAX_PROMPT_LENGTH) -> str:
    """Compress prompt text with de-duplication before applying a hard safety limit.

    :param prompt: raw prompt text to compress
    :param max_length: hard character limit after compression
    :return: compressed prompt string within max_length
    """
    text = " ".join(line.strip() for line in prompt.splitlines() if line.strip())
    if len(text) <= max_length:
        return text
    # De-duplicate sentences to reduce repetition
    sentences = [part.strip() for part in text.replace("。", "。\n").splitlines() if part.strip()]
    unique: list[str] = []
    for sentence in sentences:
        if sentence not in unique:
            unique.append(sentence)
    compressed = " ".join(unique)
    if len(compressed) <= max_length:
        return compressed
    # Truncate middle with ellipsis when still too long
    keep = max(80, (max_length - 12) // 2)
    logger.debug("compress_prompt truncated: %d → %d chars", len(compressed), max_length)
    return f"{compressed[:keep].rstrip()} … {compressed[-keep:].lstrip()}"


@dataclass
class ToolConfig:
    name: str
    kind: str = "builtin"
    enabled: bool = True


@dataclass
class PermissionConfig:
    mode: str = "dontAsk"
    allowed_tools: list[str] = field(default_factory=list)
    disallowed_tools: list[str] = field(default_factory=list)


@dataclass
class EvalState:
    score: float = 0.0
    rationale: str = "未评估"
    last_goal: str | None = None
    updated_at: str = field(default_factory=utc_now)


@dataclass
class MemoryState:
    notes: list[str] = field(default_factory=list)
    evaluation_history: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureBreakdown:
    """Per-dimension evaluation evidence."""

    id: str
    label: str
    passed: bool
    score: float
    raw_weight: float
    effective_weight: float
    evidence: str  # "matched_keyword: 结论" or "not_found", max 80 chars

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvalResult:
    """Structured quality signal produced by an Evaluator."""

    score: float
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestion: str = ""
    rationale: str = ""
    features: list[FeatureBreakdown] = field(default_factory=list)

    def summary(self) -> str:
        weak = "；".join(self.weaknesses[:3]) or "无明显短板"
        return f"score={self.score:.2f}; weaknesses={weak}; suggestion={self.suggestion}"


@dataclass
class AgentImage:
    """可序列化 Agent 镜像：prompt + tools + permissions + memory + eval + runtime_adapter。"""

    id: str = field(default_factory=lambda: new_id("image"))
    version: int = 1
    prompt: str = "回答要具体，先给短结论，再给证据。"
    tools: list[ToolConfig] = field(default_factory=list)
    permissions: PermissionConfig = field(default_factory=PermissionConfig)
    memory: MemoryState = field(default_factory=MemoryState)
    eval: EvalState = field(default_factory=EvalState)
    runtime_adapter: RuntimeName = "mock"
    parent_id: str | None = None
    created_at: str = field(default_factory=utc_now)

    def to_genome(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = "selfplay.agent_image.v1"
        return data

    @classmethod
    def from_genome(cls, genome: dict[str, Any]) -> "AgentImage":
        """Reconstruct an AgentImage from a serialized genome dict.

        :param genome: dict produced by to_genome()
        :return: reconstructed AgentImage instance
        :raises TypeError: if genome is not a dict
        """
        if not isinstance(genome, dict):
            raise TypeError(f"genome must be dict, got {type(genome).__name__}")
        try:
            return cls(
            id=genome.get("id", new_id("image")),
            version=int(genome.get("version", 1)),
            prompt=genome.get("prompt") or genome.get("instructions") or "回答要具体，先给短结论，再给证据。",
            tools=[ToolConfig(**x) for x in genome.get("tools", [])],
            permissions=PermissionConfig(**genome.get("permissions", {})),
            memory=MemoryState(**genome.get("memory", {})),
            eval=EvalState(**genome.get("eval", {})),
            runtime_adapter=genome.get("runtime_adapter", "mock"),
            parent_id=genome.get("parent_id"),
            created_at=genome.get("created_at", utc_now()),
        )
        except (KeyError, ValueError) as exc:
            logger.warning("from_genome fallback for invalid data: %s", exc)
            return cls()

    def mutated_prompt(
        self,
        new_prompt: str,
        score: float,
        rationale: str,
        max_length: int = DEFAULT_MAX_PROMPT_LENGTH,
    ) -> "AgentImage":
        """Create a child AgentImage with an evolved prompt.

        :param new_prompt: the proposed new prompt text
        :param score: evaluation score that triggered this mutation
        :param rationale: human-readable reason for the mutation
        :param max_length: maximum prompt length after compression
        :return: new AgentImage with incremented version
        """
        # Clone self, then apply mutation
        child = AgentImage.from_genome(self.to_genome())
        child.id = new_id("image")
        child.version = self.version + 1
        child.parent_id = self.id
        child.prompt = compress_prompt(new_prompt, max_length=max_length)
        child.eval = EvalState(score=score, rationale=rationale)
        child.memory.notes.append(rationale)
        child.created_at = utc_now()
        return child


@dataclass
class AgentGenome:
    """兼容旧版最小 Genome：既是被观测数据，也是驱动 Agent 行为的程序。"""

    id: str = field(default_factory=lambda: new_id("genome"))
    version: int = 1
    instructions: str = "回答要具体，先给短结论，再给证据。"
    parent_id: str | None = None
    created_at: str = field(default_factory=utc_now)

    def mutated(self, new_instructions: str) -> "AgentGenome":
        return AgentGenome(
            id=new_id("genome"),
            version=self.version + 1,
            instructions=new_instructions,
            parent_id=self.id,
        )

    def to_agent_image(self, runtime_adapter: RuntimeName = "mock") -> AgentImage:
        return AgentImage(
            id=self.id.replace("genome", "image", 1),
            version=self.version,
            prompt=self.instructions,
            runtime_adapter=runtime_adapter,
            parent_id=self.parent_id,
            created_at=self.created_at,
        )


@dataclass
class TaskResult:
    task: str
    output: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationRecord:
    cycle: int
    stage: Stage
    genome_id: str
    score_before: float
    score_after: float | None
    note: str
    created_at: str = field(default_factory=utc_now)
    profile_id: str | None = None
    profile_version: int | None = None


@dataclass
class OedmCycleResult:
    cycle: int
    old_genome: AgentGenome
    new_genome: AgentGenome
    task_result: TaskResult
    evaluation: EvaluationRecord
    decision: str


@dataclass
class SupervisorCycleResult:
    cycle: int
    old_image: AgentImage
    new_image: AgentImage
    events: list[Any]
    task_result: TaskResult
    evaluation: EvaluationRecord
    decision: str
    rejected_attempts: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class EvolutionResult:
    """Multi-cycle OEDM run result."""

    goal: str
    cycles: list[SupervisorCycleResult]
    initial_image: AgentImage
    final_image: AgentImage
    threshold: float
    stopped_early: bool = False

    @property
    def total_improvement(self) -> float:
        if not self.cycles:
            return 0.0
        start = self.cycles[0].evaluation.score_before
        end = self.cycles[-1].evaluation.score_after
        if end is None:
            end = self.cycles[-1].evaluation.score_before
        return round(end - start, 4)
