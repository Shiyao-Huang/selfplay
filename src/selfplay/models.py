from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

Stage = Literal["observe", "evaluate", "decide", "modify"]
RuntimeName = Literal["mock", "claude", "codex"]
DEFAULT_MAX_PROMPT_LENGTH = 2000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def compress_prompt(prompt: str, max_length: int = DEFAULT_MAX_PROMPT_LENGTH) -> str:
    """Compress prompt text with de-duplication before applying a hard safety limit."""
    text = " ".join(line.strip() for line in prompt.splitlines() if line.strip())
    if len(text) <= max_length:
        return text
    sentences = [part.strip() for part in text.replace("。", "。\n").splitlines() if part.strip()]
    unique: list[str] = []
    for sentence in sentences:
        if sentence not in unique:
            unique.append(sentence)
    compressed = " ".join(unique)
    if len(compressed) <= max_length:
        return compressed
    keep = max(80, (max_length - 12) // 2)
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

    def mutated_prompt(
        self,
        new_prompt: str,
        score: float,
        rationale: str,
        max_length: int = DEFAULT_MAX_PROMPT_LENGTH,
    ) -> "AgentImage":
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
