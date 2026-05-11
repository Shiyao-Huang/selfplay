# Phase 1 实现规格书

> **Solution Architect** | 2026-05-10
> 前置：架构 v1.0 (`docs/architecture.md`) + Phase 0 代码审查
> 目标：将 Phase 0 demo 升级为**可交付的开源 v0.1.0**，核心是让自进化闭环**真实可信**

---

## 一句话版本

Phase 0 的"自进化"是假的（硬编码关键词检查），Phase 1 要让它变成真的：LLM 评估 + 结构化 mutation + 多轮进化 + 可配置。

## 架构缺口诊断（审查全部 8 个源文件后的发现）

### 缺口 1：自进化是假的（P0 阻塞）

**现状：**
- `agents.py:40-48` — `score_output()` 是 4 条正则检查（"结论"/"证据"/"下一步"/长度）
- `supervisor.py:69-95` — `reflect_and_mutate()` 硬编码 3 条 mutation 规则
- 结果：每次运行都"发现"同样的"缺陷"，"进化"是确定性表演

**影响：** README 承诺的"每轮比上一轮更好"是谎言。用户一旦看代码就失去信任。

**解决方案：** 引入 `Evaluator` 抽象层

```python
# src/selfplay/evaluator.py

class Evaluator(Protocol):
    """评估 Agent 输出质量的抽象接口。"""
    async def evaluate(self, task: str, output: str, image: AgentImage) -> EvalResult:
        ...

@dataclass
class EvalResult:
    score: float          # 0.0 ~ 1.0
    strengths: list[str]  # 做得好的点
    weaknesses: list[str] # 需要改进的点
    suggestion: str       # 具体改进建议（给 Mutator 用）
```

三种实现：
1. **HeuristicEvaluator** — 当前的 `score_output()` 重构，作为 fallback
2. **ClaudeEvaluator** — 调用 Claude API 评估输出质量，返回结构化评分
3. **CompositeEvaluator** — 先 heuristic 快筛，低分时才调 LLM（省钱）

### 缺口 2：单轮进化，README 承诺 3 轮（P0 阻塞）

**现状：**
- `cli.py:192` — `run_cycle()` 只跑 1 个 cycle
- README demo 截图显示 3 轮进化（Cycle 1/3, 2/3, 3/3）

**解决方案：** CLI 添加 `--cycles N` 参数

```python
# cli.py 修改
run.add_argument("--cycles", type=int, default=3, help="OEDM evolution cycles")
demo.add_argument("--cycles", type=int, default=3)

# supervisor.py 新增
async def run_evolution(self, goal: str, cycles: int = 3, runtime_adapter: str = "mock") -> EvolutionResult:
    """运行多轮进化，每轮基于上一轮的结果改进。"""
    results = []
    image = self.seed(runtime_adapter)
    for i in range(cycles):
        result = await self.run_cycle(goal, cycle=i+1, runtime_adapter=runtime_adapter)
        results.append(result)
        if result.evaluation.score_after >= self.threshold:
            break
    return EvolutionResult(cycles=results, total_improvement=...)
```

### 缺口 3：Mutation 是 append-only，prompt 会膨胀（P1）

**现状：**
- `supervisor.py:85` — `candidate_prompt = image.prompt.rstrip() + " " + " ".join(additions)`
- 每次 mutation 只追加，从不删减/替换，prompt 持续膨胀

**解决方案：** 引入 `Mutator` 抽象层

```python
# src/selfplay/mutator.py

class Mutator(Protocol):
    """基于评估结果修改 AgentImage 的抽象接口。"""
    async def mutate(self, image: AgentImage, eval_result: EvalResult) -> AgentImage | None:
        """返回 None 表示不修改（评估已达标）。"""
        ...

class PromptMutator:
    """基于 LLM 的 prompt 优化器。"""
    async def mutate(self, image: AgentImage, eval_result: EvalResult) -> AgentImage | None:
        # 调用 LLM 重写 prompt，而非简单追加
        # 包含 prompt 长度上限保护
        ...

class RuleBasedMutator:
    """Phase 0 兼容的规则 mutation（重构自 reflect_and_mutate）。"""
    ...
```

关键约束：
- prompt 最大长度 2000 字符（防止膨胀）
- mutation 必须通过 `eval_result.suggestion` 驱动，不硬编码规则
- 若 LLM 不可用，降级到 RuleBasedMutator

### 缺口 4：配置文件创建了但没读取（P1）

**现状：**
- `cli.py:149-151` — `selfplay init` 创建 `selfplay.yaml`
- `cli.py:139-204` — 所有命令都从 argparse 参数读取，从未读 YAML

**解决方案：** 添加配置加载层

```python
# src/selfplay/config.py

@dataclass
class SelfPlayConfig:
    runtime: str = "mock"
    threshold: float = 0.9
    database: str = "data/selfplay.sqlite"
    cycles: int = 3
    max_prompt_length: int = 2000

    @classmethod
    def load(cls, path: str = "selfplay.yaml") -> "SelfPlayConfig":
        """读取 YAML 配置，合并 CLI 参数（CLI 优先）。"""
        ...

    @classmethod
    def default(cls) -> "SelfPlayConfig":
        return cls()
```

### 缺口 5：ClaudeRuntimeAdapter 依赖不存在的 SDK 包（P2）

**现状：**
- `sdk_bridge.py:49-53` — `_ensure_local_claude_sdk_path()` 尝试从本地 `sources/` 目录加载
- `sdk_bridge.py:76` — `from claude_agent_sdk import ...` 包名不存在于 PyPI
- 实际 Claude Agent SDK 的 Python 包名可能是 `anthropic` 或其他

**解决方案：** Phase 1 优先让 mock 模式完美工作。Claude adapter 作为 opt-in：
- pyproject.toml 中 `[sdk]` extra 保持可选
- adapter 中加明确的 install 提示
- 文档说明如何连接真实 LLM

---

## 新增文件清单

| 文件 | 职责 | 优先级 |
|------|------|--------|
| `src/selfplay/evaluator.py` | Evaluator 抽象 + HeuristicEvaluator + ClaudeEvaluator | P0 |
| `src/selfplay/mutator.py` | Mutator 抽象 + RuleBasedMutator + PromptMutator | P0 |
| `src/selfplay/config.py` | YAML 配置加载 + CLI 参数合并 | P1 |
| `src/selfplay/__init__.py` | 补全 `__version__`、公开 API | P1 |

## 修改文件清单

| 文件 | 修改内容 | 优先级 |
|------|----------|--------|
| `supervisor.py` | 新增 `run_evolution()` 多轮进化；`reflect_and_mutate()` 改用 Evaluator+Mutator | P0 |
| `cli.py` | 添加 `--cycles` 参数；demo 默认 3 轮；输出多轮进化摘要 | P0 |
| `models.py` | 新增 `EvalResult`、`EvolutionResult` 数据类 | P0 |
| `agents.py` | `score_output()` 标记 deprecated，指向 evaluator.py | P1 |
| `pyproject.toml` | 版本升级 0.1.0 → 0.2.0；`[sdk]` extra 更新 | P1 |

## 不改的文件

| 文件 | 原因 |
|------|------|
| `storage.py` | 接口干净，无需改动 |
| `sdk_bridge.py` | Mock adapter 足够；Claude adapter 等真实 SDK 发布再更新 |
| `apps/tui/` | Phase 1 先完善 CLI demo 体验，TUI 升级放 Phase 2 |
| `README.md` | 当前 README 已正确描述 Phase 1 目标行为，等实现后再微调 |

---

## 关键设计决策

### D1：Evaluator vs Mutator 分离

**决策：** 评估和修改分为两个独立抽象。

**原因：**
- 评估是只读的（不改变状态），修改是写操作（改变 prompt）
- 评估可以独立测试和 mock
- 未来可以组合不同 Evaluator + Mutator 策略（策略模式）
- 符合 OEDM 四阶段：Observe+Evaluate = Evaluator，Decide+Modify = Mutator

### D2：Mock 模式必须独立可用

**决策：** `pip install selfplay && selfplay demo` 必须零依赖可用。

**原因：**
- 这是爆款传播的关键路径
- 用户第一次接触必须 30 秒内有正面体验
- LLM 依赖只在 `--runtime claude` 时需要

### D3：HeuristicEvaluator 的"进化"必须是真实的

**决策：** 即使 mock 模式，也要让每轮产生可观测的不同结果。

**具体设计：**
- HeuristicEvaluator 基于输出中的具体特征评分（不是固定模式）
- RuleBasedMutator 的规则来自 eval_result.weaknesses，不是硬编码
- 每轮进化必须产生不同的 prompt 和不同的评分
- 进化历史可查询（`selfplay history` 能看到真实的分数变化）

### D4：Prompt 长度保护

**决策：** prompt 最大 2000 字符，超出时触发压缩而非截断。

**原因：** append-only mutation 导致 prompt 膨胀 → LLM context 浪费 → 质量下降

### D5：Per-cycle retry（被拒绝的 mutation 展示）

**决策：** `run_evolution()` 的每个 cycle 支持最多 2 次 mutation 尝试。第一次失败（分数下降）时，展示 "❌ Rejected" 并自动尝试不同策略。两次都失败则保留当前版本。

**原因：** 用户反馈研究（`research/user-feedback-insights.md`）表明，展示"被拒绝的修改"能显著增强安全可信度叙事。用户对自改进 Agent 的最大担忧是失控，显式展示回退行为直接回应这一担忧。

**实现：** `RuleBasedMutator` 维护一个 mutation 策略列表（非随机），每次尝试按顺序取下一个策略。第一次尝试激进策略（可能失败），第二次尝试保守策略（更可能成功）。

---

## Demo 体验设计（Phase 1 目标）

用户执行 `selfplay demo` 应该看到：

```
$ selfplay demo "写一个快速排序"

🧬 SelfPlay v0.2.0 — Self-evolving Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Cycle 1/3
├── 🎯 Goal: 写一个快速排序
├── ▶ Run (mock) — 使用 Genome v1
├── 👁 Observe — 1 runtime event
├── 📈 Score — 0.40 (缺少错误处理，缺少复杂度分析)
├── 🧬 Mutate — +错误处理边界检查
└── 💾 Persist — v1 → v2

🔄 Cycle 2/3
├── 🎯 Goal: 写一个快速排序
├── ▶ Run (mock) — 使用 Genome v2 (已改进)
├── 👁 Observe — 1 runtime event
├── 📈 Score — 0.75
├── 🧬 Attempt 1 — +激进优化策略
├── ❌ Rejected — score dropped to 0.68, rollback to v2
├── 🧬 Attempt 2 — +时间复杂度分析 +示例
├── 📈 Score — 0.90 ↑
└── 💾 Persist — v2 → v3

🔄 Cycle 3/3
├── 🎯 Goal: 写一个快速排序
├── ▶ Run (mock) — 使用 Genome v3
├── 👁 Observe — 1 runtime event
├── 📈 Score — 0.95 ↑ (全面达标)
├── ✅ Threshold reached — stopping early
└── 💾 Persist — v3 (final)

📊 Evolution Summary
├── v1: 0.40 → v2: 0.75 (+88%) → v3: 0.95 (+27%)
├── Total improvement: +138%
└── Best prompt: "回答要具体，先给短结论，再给证据。每次输出必须包含...

Try: selfplay history | selfplay tree | selfplay tui
```

---

## 实现顺序（建议 Builder 工作流）

### Step 1：数据模型（30 min）
- `models.py` 添加 `EvalResult`、`EvolutionResult`
- 确保 `AgentImage.mutated_prompt()` 支持替换式修改（不只是追加）

### Step 2：Evaluator（1 hour）
- 新建 `evaluator.py`
- 实现 `HeuristicEvaluator`（从 `agents.py:score_output()` 重构）
- 写 `ClaudeEvaluator` 骨架（LLM 不可用时抛出明确错误）

### Step 3：Mutator（1 hour）
- 新建 `mutator.py`
- 实现 `RuleBasedMutator`（从 `supervisor.py:reflect_and_mutate()` 重构）
- 写 `PromptMutator` 骨架

### Step 4：Supervisor 重构（1 hour）
- `run_cycle()` 使用 Evaluator + Mutator
- 新增 `run_evolution()` 多轮循环
- 删除 `reflect_and_mutate()` 硬编码逻辑

### Step 5：CLI 升级（30 min）
- 添加 `--cycles` 参数
- demo 默认 3 轮
- 输出多轮进化摘要

### Step 6：配置 + 清理（30 min）
- 新建 `config.py`
- CLI 读取 YAML + argparse 合并
- 版本升级

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| HeuristicEvaluator 进化不够真实 | 高 | 用户不信服 | RuleBasedMutator 基于 weaknesses 动态生成规则，不是硬编码 |
| Claude SDK 包名/API 变化 | 中 | claude adapter 不可用 | Phase 1 优先 mock 模式，claude 作为 opt-in |
| Prompt 膨胀导致 LLM 质量下降 | 中 | 进化后期效果变差 | 2000 字符上限 + 压缩策略 |
| 多轮进化耗时 | 低 | demo 体验差 | mock 模式每轮 <100ms，claude 模式添加进度条 |

---

## 成功标准

1. ✅ `selfplay demo` 运行 3 轮进化，每轮分数确实不同
2. ✅ `selfplay history` 显示真实的分数变化曲线
3. ✅ mock 模式零依赖可用（`pip install selfplay` 即可）
4. ✅ 代码中不存在硬编码的 mutation 规则（全部来自 Evaluator 输出）
5. ✅ prompt 长度有上限保护
6. ✅ `--runtime claude` 可选工作（有明确错误提示如果 SDK 不可用）
