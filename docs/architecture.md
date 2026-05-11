# 自指闭环系统架构方案

> **Solution Architect v1.0（最终版）** | 2026-05-09
> 理论基础：Escher-Loop、Gödel Agent、Meta HyperAgents、Darwin Gödel Machine
> 整合：Researcher 理论报告（OEDM/三层架构）+ Scout 形式化（(R,ρ,f)/自指分级）+ Scout/Codex SDK 调研
> 核心洞察：SDK-neutral supervisor + runtime adapter 模式

---

## 一句话版本

构建 SDK-neutral 的自指闭环系统，通过 OEDM 四阶段循环（Observe→Evaluate→Decide→Modify）让 Agent 持续自我进化，Claude/Codex 作为可替换的 runtime adapter。

## 三句话版本

1. 系统采用 **SDK-neutral supervisor** 架构——闭环逻辑（OEDM）不绑定任何特定 SDK，Claude Agent SDK 和 Codex Agent SDK 作为可替换的 runtime adapter 插件。
2. 自指核心是 Genome（三元组 R=表示）的双重性——既是数据（被评估）又是程序（指导行为），通过 (R, ρ, f) 形式化闭环实现递归自我改进。
3. AgentImage = prompt + tools + permissions + memory + eval + runtime_adapter，统一事件模型驱动 Task/Meta/Arch 三层纠缠层级。

## 五句话版本

1. **理论根基**：综合 Gödel 不完备定理（Genome=Gödel编码）、Hofstadter Strange Loop（纠缠层级）、Von Neumann 自复制（构造器+蓝图+控制器）、控制论反馈（OEDM 最小闭环），形成统一的自指 Agent 理论框架。
2. **SDK-neutral 架构**：闭环逻辑不绑定 SDK——Supervisor 定义统一事件模型（ThreadStarted/TurnStarted/ToolEnded/Message/Diff/Usage/TurnCompleted），Claude Agent SDK（Python query()/ClaudeSDKClient）和 Codex SDK（Thread/Turn/app-server）作为可替换的 runtime adapter。
3. **OEDM + (R,ρ,f)**：Observe+Evaluate = ρ（系统→表示映射），Decide+Modify = f（改进函数），R = Genome（自描述表示），`f ∘ ρ ∘ f ∘ ρ ∘ ... → System*` 实现递归改进收敛。
4. **双群体进化**：借鉴 Escher-Loop 的 Task Agent 群体 + Optimizer Agent 群体，用 Elo 排名和 MAP-Elites 驱动选择；借鉴 Darwin GM 进化树保留版本历史和回退能力。
5. **AgentImage 抽象**：`AgentImage = prompt + tools + permissions + memory + eval + runtime_adapter`，每个 Agent 是一个可序列化的镜像，支持跨 runtime 迁移和版本化管理。

---

## 1. 整体架构

### 1.1 三层 + 六层混合架构图

```
┌─────────────────────────────────────────────────────┐
│                   Interface Layer                     │
│           CLI TUI (Textual) │ Web (Next.js)           │
├─────────────────────────────────────────────────────┤
│               Self-Referential Core                   │
│                                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────┐ │
│  │  Arch Layer   │  │  Meta Layer   │  │Task Layer│ │
│  │ (修改架构)     │  │ (反思评估)     │  │(执行任务) │ │
│  │ 读写 Genome   │  │ OEDM 循环     │  │构造器角色  │ │
│  │ Von Neumann C │  │ LLM 柔性证明  │  │Von Neumann│ │
│  └───────┬───────┘  └───────┬───────┘  └────┬─────┘ │
│          │    Strange Loop (纠缠层级)    │          │
│          └────────────┬───────────────────┘          │
│                       ▼                              │
│               ┌───────────────┐                      │
│               │   Genome /    │ ◄── 双重性入口       │
│               │  Self-Model   │     数据=程序        │
│               └───────┬───────┘                      │
│                       ▼                              │
│               ┌───────────────┐                      │
│               │  OEDM Loop    │                      │
│               │ Observe →     │                      │
│               │ Evaluate →    │                      │
│               │ Decide →      │                      │
│               │ Modify        │                      │
│               └───────────────┘                      │
├─────────────────────────────────────────────────────┤
│          Agent Runtime Layer                          │
│  Claude Agent SDK (primary) │ Codex SDK (sandbox)    │
├─────────────────────────────────────────────────────┤
│          Communication Layer                          │
│              tRPC (TypeScript)                        │
├─────────────────────────────────────────────────────┤
│          Tool Integration Layer                       │
│  gitnexus │ codeflow │ gstack │ superpower            │
│              (MCP Protocol)                           │
├─────────────────────────────────────────────────────┤
│          Data & State Layer                           │
│  SQLite │ Genome Store │ Elo │ MAP-Elites │ 进化树   │
└─────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 说明 | 理论来源 |
|------|------|---------|
| **自指优先** | 系统的每个组件都能被系统自身修改——Genome 是一等公民 | Gödel 编码 |
| **OEDM 最小闭环** | Observe→Evaluate→Decide→Modify，四阶段构成最小反馈环 | 控制论反馈 + Researcher 统一抽象 |
| **纠缠层级** | 三层（Task/Meta/Arch）互相穿透，非严格分离 | Hofstadter Strange Loop |
| **双重性入口** | Genome 同时是数据（被评估）和程序（指导行为），读写 Genome = 打开自指 | Gödel + Von Neumann |
| **柔性证明** | 用 LLM 评估替代形式化证明，经验验证 + 进化选择 | Gödel Agent + Darwin GM |
| **渐进式复杂度** | 从最小 OEDM 循环开始，逐步叠加 Elo、MAP-Elites、双群体 | Escher-Loop |
| **磁盘即真理** | 所有状态变更必须持久化到磁盘才算完成 | Mom Test P1 |

---

## 2. 自指闭环设计（核心）

### 2.1 OEDM 最小闭环

基于 Researcher 理论报告的跨领域统一抽象，所有自指系统的共性结构：

```
           ┌──────────────────────┐
           │                      │
           ▼                      │
    ┌──────────┐           ┌──────────┐
    │  观测    │ ────────→ │  评估    │
    │ Observe  │           │ Evaluate │
    └──────────┘           └──────────┘
           │                      │
           │                      ▼
    ┌──────────┐           ┌──────────┐
    │  修改    │ ←──────── │  决策    │
    │ Modify   │           │ Decide   │
    └──────────┘           └──────────┘
           │
           └──→ 作用于系统 ──→ 被观测 ──→ ...
```

**四阶段定义：**

1. **Observe（观测）**：Agent 观察自身执行结果、环境反馈、评估历史
2. **Evaluate（评估）**：LLM 作为"柔性证明器"，评估执行质量与目标差距
3. **Decide（决策）**：基于评估结果，决定需要修改什么（instructions? tools? hooks?）
4. **Modify（修改）**：修改 Genome 中对应的字段，生成新版本

**理论根基**：
- 计算层面：Y combinator `Y = λf.(λx.f(x x))(λx.f(x x))` — 最小自指计算结构
- 逻辑层面：Gödel 句 `G ↔ ¬Prov(G)` — 最小自指逻辑结构
- 形式化层面：三元组 `(R, ρ, f)` — R=表示(Genome)，ρ=映射(Observe+Evaluate)，f=改进(Decide+Modify)
- 工程层面：OEDM 四阶段 — 最小可行自指循环

> **OEDM 与 (R, ρ, f) 的对应**：
> - Observe + Evaluate = ρ（系统→表示的映射，评估当前状态）
> - Decide + Modify = f（表示→改进系统的函数，执行改进）
> - R = Genome（系统的自描述表示）
> - 循环：`f ∘ ρ ∘ f ∘ ρ ∘ ... → System*`（递归改进收敛）

### 2.2 Genome：双重性入口

> **核心洞察（Researcher 报告）**：自指系统的核心是一个双重性（Duality）——
> 某物同时扮演两个角色（数据/程序、被观测/观测者、描述/被描述）。
> Genome 就是这个双重性的具象化：它既是被评估的数据，又是指导行为的程序。

Genome 是 Agent 的"DNA"，定义了其全部可优化行为。对应 Von Neumann 自复制自动机的蓝图（Blueprint）。

```typescript
interface AgentGenome {
  id: string;
  version: number;

  // 指令层：Agent 的核心行为指令
  instructions: string;

  // 工具层：可用的工具集合及参数
  toolSet: ToolConfig[];

  // Hook 链：PreToolUse / PostToolUse / Stop 等钩子
  hookChain: HookConfig[];

  // 评估历史：过去 N 次评估结果
  evaluationHistory: EvaluationRecord[];

  // Elo 分数：动态排名
  eloRating: number;

  // 变异策略：Optimizer 如何修改此 Genome
  mutationStrategy: MutationConfig;

  // 父代信息：追踪进化谱系
  parentGenomeIds: string[];

  // 创建时间戳
  createdAt: string;
}
```

### 2.3 Escher-Loop 双群体机制

```python
# 伪代码：双群体自指优化循环

class EscherLoop:
    def __init__(self):
        self.task_agents: Population      # Task Agent 群体
        self.optimizer_agents: Population  # Optimizer Agent 群体
        self.elo = EloRatingSystem()
        self.archive = MAPElitesArchive()  # 多维质量档案

    async def run_generation(self):
        # 1. 为每个 Task Agent 分配任务
        for task_agent in self.task_agents:
            task = self.sample_task()  # 按 Softmax 采样
            result = await task_agent.execute(task)

            # 2. Optimizer Agent 评估结果
            optimizer = self.sample_optimizer()  # 按 Elo 排名加权采样
            evaluation = await optimizer.evaluate(task, result)

            # 3. 更新 Elo 排名
            self.elo.update(task_agent, evaluation.score)
            self.elo.update(optimizer, evaluation.quality)

            # 4. Optimizer 生成改进的 Genome
            if evaluation.should_optimize:
                new_genome = await optimizer.optimize(task_agent.genome)
                self.archive.store(new_genome)

        # 5. 自指：Optimizer 也被优化
        #   - 评估 Optimizer 的优化效果（通过 Task Agent 的改进幅度衡量）
        #   - 最好的 Optimizer 成为新的基准
        self.evolve_optimizers()
```

### 2.4 三层架构与自指实现路径

**三层架构（基于 Researcher 的 Task↔Meta↔Arch 映射）：**

```
┌────────────────────────────────────────────────┐
│  Arch Layer（修改架构层）                        │
│  - 读写并修改 Agent 的 Genome 结构本身           │
│  - 对应 Von Neumann 控制器 C                    │
│  - OEDM：Decide + Modify                        │
├────────────────────────────────────────────────┤
│  Meta Layer（反思评估层）                        │
│  - 评估 Task Layer 执行质量                     │
│  - 反思策略，生成改进建议                        │
│  - 对应 Gödel Machine 的证明搜索器              │
│  - OEDM：Observe + Evaluate                     │
├────────────────────────────────────────────────┤
│  Task Layer（任务执行层）                        │
│  - 执行具体任务（代码生成、分析等）               │
│  - 对应 Von Neumann 构造器 A                    │
│  - 受 Genome 中的 instructions 指导              │
└────────────────────────────────────────────────┘
```

**自指的实现路径（渐进式）：**

**Level 0 — 单 Agent OEDM 循环**（1 天）
- 单个 Agent 执行任务后触发 OEDM 闭环
- `PostToolUse` Hook = Observe 阶段
- LLM self-critique = Evaluate 阶段
- 修改自身 instructions = Decide + Modify 阶段
- **验证目标：Agent 能否通过自省改善表现？**

**Level 1 — 三层分离 + Genome 读写**（3-5 天）
- Task Agent / Meta Agent / Arch Agent 角色分离
- Genome 作为共享的自描述文件（YAML/JSON）
- Arch Agent 读写 Genome 实现 Modify
- SQLite 持久化 Genome 版本链（参考 Darwin GM 进化树）
- **验证目标：三层分离是否比单 Agent 更有效？**

**Level 2 — 双群体 + Elo + 进化树**（1-2 周）
- 扩展为 Task Agent 群体和 Meta Agent 群体
- Elo 动态排名 + Softmax 采样匹配
- 进化树保留所有版本，支持回退（Darwin GM 模式）
- **验证目标：群体进化是否优于单线改进？**

**Level 3 — MAP-Elites + 完整自指**（2-4 周）
- MAP-Elites 多维质量档案（按任务类型/复杂度/质量多维分类）
- Arch Agent 自身也接受 OEDM 循环（Meta-Meta Layer）
- Genome 变异策略由上层动态决定
- **验证目标：自指能否产生涌现性的改进？**

### 2.5 Agent SDK 自指能力评估

基于 Scout 调研报告，当前 Agent SDK 的自指能力分级：

| 自指层次 | 描述 | Claude Agent SDK | Codex Agent SDK |
|----------|------|-----------------|-----------------|
| **L0: Prompt 自省** | Agent 能读取/修改自身 prompt | ✅ CLAUDE.md | ✅ Instructions |
| **L1: 工具使用反射** | Agent 能调用自身执行的工具 | ✅ Sub-agent / Skills | ⚠️ Handoffs |
| **L2: 代码自修改** | Agent 能修改自身实现代码 | ⚠️ 需 Hook + 外部写入 | ❌ 设计限制 |
| **L3: 架构自改进** | Agent 能重新设计自身架构 | ❌ 理论阶段 | ❌ |
| **L4: 完全自举** | Agent 从零自建完整自身 | ❌ 不可能(Theorem 11.3) | ❌ |

**工程约束**：
- LLM 修改深度限制 ~2-3 层递归（HyperAgents 实测）
- 不可类比编译器 bootstrap——编译器是确定性系统，LLM 是概率性的
- L4 完全自举被 Spivack Theorem 11.3 证明为不可能

**务实策略**：系统目标定在 **L0-L2**（Prompt 自省 + 工具反射 + 有限代码自修改），通过 OEDM 循环在 L1 层面持续改进，L2 仅在沙箱中尝试。

### 2.6 Reflexion 模式：语言自省的务实路径

除代码自修改外，Reflexion（NeurIPS 2023）提供了一条更稳定的自指路径：

```
行动 → 观察结果 → 语言自省 → 更新策略 → 行动
```

- 不修改代码，而是修改行为策略（自然语言描述）
- 策略存储在 Genome 的 `instructions` 字段
- 比 L2 代码自修改更稳定，但改进上限更低
- **建议作为 Phase 0-1 的默认模式，Phase 2+ 再尝试 L2**

---

## 3. 通讯层选型分析

### 3.1 方案对比

| 维度 | tRPC | gRPC | WebSocket |
|------|------|------|-----------|
| **类型安全** | ✅ 端到端 TS 类型 | ✅ Protobuf schema | ❌ 无 schema |
| **开发效率** | ✅✅ 零胶水代码 | ⚠️ 需要 proto 生成 | ⚠️ 手动序列化 |
| **CLI 适配** | ✅ 原生支持 | ⚠️ 需要 grpcurl | ✅ 通用 |
| **Web 适配** | ✅ 原生支持 | ⚠️ 需要 grpc-web | ✅ 原生 |
| **流式传输** | ✅ Subscription | ✅ Server streaming | ✅ 原生 |
| **Agent SDK 集成** | ✅ Python/TS 均可 | ✅ 多语言 | ✅ 通用 |
| **复杂度** | 低 | 中 | 低 |
| **性能** | 良好（HTTP/2） | 极高（HTTP/2 + 二进制） | 良好 |

### 3.2 选型结论：tRPC

**理由：**

1. **TypeScript-native**：Claude Agent SDK 同时支持 TS 和 Python，tRPC 的 TS-first 策略与 SDK 的 TS API 天然契合
2. **端到端类型安全**：Agent 间调用的请求/响应类型在编译期就能保证一致，减少运行时错误
3. **零胶水**：不需要 Protobuf 定义、不需要代码生成，直接用 TS interface 定义契约
4. **CLI + Web 通用**：同一个 tRPC Router 同时服务 CLI TUI 和 Web 界面
5. **流式支持**：tRPC Subscription 支持 Agent 执行过程的实时流式推送

**架构：**

```typescript
// tRPC Router 定义 Agent 间通讯契约
const agentRouter = router({
  // Task Agent 注册能力
  registerTask: procedure
    .input(z.object({ genomeId: z.string(), capabilities: z.string[]() }))
    .mutation(async ({ input }) => { /* ... */ }),

  // Optimizer 请求评估
  requestEvaluation: procedure
    .input(z.object({ taskId: z.string(), result: z.unknown() }))
    .query(async ({ input }) => { /* ... */ }),

  // Genome 更新通知（Subscription）
  onGenomeUpdate: procedure
    .input(z.object({ agentId: z.string() }))
    .subscription(({ input }) => { /* ... */ }),

  // 实时执行流
  onExecutionStream: procedure
    .input(z.object({ taskId: z.string() }))
    .subscription(({ input }) => { /* ... */ }),
});
```

**Python 侧接入：**
Claude Agent SDK 的 Python 运行时通过 HTTP 调用 tRPC Server，使用 `trpc-client` 或直接 REST 调用（tRPC 底层是 HTTP）。

---

## 4. 界面层设计

### 4.1 CLI TUI（优先级 P0）

**技术选型：Textual (Python)**

选择 Textual 而非 Ink 的理由：
- Claude Agent SDK 的 Python API 更成熟（`query()` async API）
- Textual 提供丰富的 TUI 组件（表格、图表、进度条、日志面板）
- 与 Claude Agent SDK Python 运行时在同一进程内，零序列化开销

**TUI 布局设计：**

```
┌──────────────────────────────────────────────────────────┐
│ SelfPlay Monitor                          [Gen:12 Elo:342]│
├──────────────────────┬───────────────────────────────────┤
│ Task Agents          │ Optimizer Agents                  │
│ ┌──────────────────┐ │ ┌─────────────────────────────┐   │
│ │ Agent-A  ████░░  │ │ │ Opt-Alpha  Elo: 1250  ▲2   │   │
│ │ Agent-B  ██████  │ │ │ Opt-Beta   Elo: 1180  ▼1   │   │
│ │ Agent-C  ██░░░░  │ │ │ Opt-Gamma  Elo: 1100  ─    │   │
│ └──────────────────┘ │ └─────────────────────────────┘   │
├──────────────────────┴───────────────────────────────────┤
│ Evolution Log                                            │
│ [12:34:01] Agent-A genome v5 → v6 (optimized by Alpha)  │
│ [12:34:02] Task "refactor auth" score: 0.87 (↑0.12)     │
│ [12:34:03] Alpha self-evaluation: Elo 1250 → 1250       │
│ [12:34:04] MAP-Elites archive: 23/50 niches filled      │
├──────────────────────────────────────────────────────────┤
│ > Enter command (status/evolve/inspect <agent>/quit)     │
└──────────────────────────────────────────────────────────┘
```

**核心功能：**
- 实时显示 Agent 群体状态、Elo 排名、进化代数
- 查看任意 Agent 的 Genome 详情
- 手动触发进化/评估
- 查看进化日志和评估历史
- 执行流实时推送

### 4.2 Web 界面（优先级 P1）

**技术方案：Next.js + tRPC Client**

- 复用 tRPC Router，无需额外 API 层
- 实时更新通过 tRPC Subscription / SSE
- 可视化：进化树谱系图、Elo 曲线、MAP-Elites 热力图
- Phase 2 实现，不阻塞 MVP

---

## 5. Agent 编排

### 5.1 SDK-neutral Supervisor 架构

> **Scout SDK 调研的核心洞察**：不要把闭环绑死在某个 SDK 内部。
> 应建一个 SDK-neutral supervisor，Claude/Codex 作为可替换的 runtime adapter。

**闭环定义：`Goal → Run → Observe → Score → Reflect → Mutate → Next Run`**

```
┌──────────────────────────────────────────────────────┐
│              OEDM Supervisor（SDK-neutral）            │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │              统一事件模型                        │  │
│  │  ThreadStarted / TurnStarted / ToolStarted     │  │
│  │  ToolEnded / Message / Usage / Diff            │  │
│  │  TurnCompleted / Error                         │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │              统一状态镜像                        │  │
│  │  prompt + tool_trace + diff + token_usage      │  │
│  │  score + failure_reason + next_strategy         │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────┐        ┌──────────────┐           │
│  │ Claude       │        │ Codex        │           │
│  │ Runtime      │        │ Runtime      │           │
│  │ Adapter      │        │ Adapter      │           │
│  └──────┬───────┘        └──────┬───────┘           │
│         │                       │                    │
│    query()              Thread/Turn                  │
│    ClaudeSDKClient      app-server                   │
│    MCP + Hooks          JSON-RPC v2                  │
│    SessionStore         ContextManager               │
└──────────────────────────────────────────────────────┘
```

### 5.2 AgentImage 抽象

```python
@dataclass
class AgentImage:
    """可序列化的 Agent 镜像 — 跨 runtime 迁移"""
    prompt: str                    # 系统指令 (= Genome.instructions)
    tools: list[ToolConfig]        # 可用工具集
    permissions: PermissionConfig  # 权限配置
    memory: MemoryState            # 评估历史 + 上下文
    eval: EvalRecord               # 最新评估结果
    runtime_adapter: str           # "claude" | "codex"

    # 序列化/反序列化
    def to_genome(self) -> dict: ...
    @classmethod
    def from_genome(cls, genome: dict) -> "AgentImage": ...
```

### 5.3 Claude Agent SDK（主 Runtime Adapter）

```python
from claude_agent_sdk import query, ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk import tool, create_sdk_mcp_server

# 自指评分工具（注册为 MCP）
@tool('score_state', '评估 OEDM 闭环状态', {'state': str})
async def score_state(args):
    return {'content': [{'type': 'text', 'text': 'score=0.82'}]}

# 自定义 MCP Server
server = create_sdk_mcp_server('selfref-tools', tools=[score_state])

# Task Agent
async def run_task_agent(agent_image: AgentImage, task: str):
    opts = ClaudeAgentOptions(
        system_prompt=agent_image.prompt,
        tools=agent_image.tools,
        mcp_servers={'selfref': server},
        allowed_tools=['mcp__selfref__score_state'],
        permission_mode="auto",
        max_turns=20,
        hooks={
            "PostToolUse": reflection_hook,   # Observe 阶段
            "Stop": evaluation_trigger_hook,   # 触发 Evaluate
        },
    )
    async for msg in query(prompt=task, options=opts):
        yield msg  # 流式输出统一事件

# Meta Agent（评估 + 反思）
async def run_meta_agent(task_result, genome):
    opts = ClaudeAgentOptions(
        system_prompt=f"你是评估器。根据以下结果评估质量并建议改进：\n{genome}",
        tools=["read", "write", "edit"],
        max_turns=5,
    )
    async for msg in query(prompt=f"评估此结果：{task_result}", options=opts):
        yield msg
```

### 5.4 Codex Agent SDK（沙箱 Runtime Adapter）

```python
# Codex 沙箱执行 — 用于高风险操作和代码验证
from codex_app_server import Codex

async def run_sandbox(agent_image: AgentImage, task: str):
    with Codex() as codex:
        thread = codex.thread_start(model='gpt-5.4', cwd='.')
        result = thread.run(task)
        return result.final_response, result.usage
```

### 5.5 Runtime Adapter 对比

| 设计点 | Claude Agent SDK | Codex SDK |
|--------|-----------------|-----------|
| **抽象中心** | query()/ClaudeSDKClient + Claude Code CLI | Thread/Turn + codex app-server |
| **运行方式** | SDK 启动 CLI 子进程，stream-json 协议 | TS: spawn codex exec；Py: stdio JSON-RPC |
| **上下文** | get_context_usage() 暴露 token/category | ContextManager 内部管理，compact 策略 |
| **工具扩展** | in-process MCP + hooks + permission callback | Codex config/MCP + 内建工具 |
| **子 agent** | AgentDefinition 公开 SDK 参数 | core 有 multi-agent，公开 SDK 偏 thread/fork |
| **自指适配** | 评分/反思工具做 MCP + hooks | 完整编码执行器嵌入 daemon |
| **成熟度** | ⭐⭐⭐ 生产级 | ⭐⭐ 实验性（绑定 app-server v2） |
| **建议角色** | **主 runtime**（评估/反思/自修改） | **辅助 runtime**（沙箱验证/隔离执行） |
| 场景 | Runtime Adapter | 理由 |
|------|----------------|------|
| 任务执行（Task Layer） | Claude adapter | query() + hooks 成熟 |
| 代码沙箱验证 | Codex adapter | 隔离执行、安全验证 |
| 评估反思（Meta Layer） | Claude adapter | MCP 自定义评分工具 |
| 架构修改（Arch Layer） | Claude adapter | 读写 Genome |
| 外部工具调用 | Claude adapter (MCP) | MCP 协议统一接入 |

### 5.6 OEDM Supervisor 主循环

```python
class OEDMSupervisor:
    """SDK-neutral 自指闭环：Goal → Run → Observe → Score → Reflect → Mutate"""

    def __init__(self):
        self.runtime_adapters = {
            "claude": ClaudeRuntimeAdapter(),
            "codex": CodexRuntimeAdapter(),
        }
        self.genome_store = GenomeStore()
        self.event_bus = EventBus()  # 统一事件模型

    async def run_cycle(self, agent_image: AgentImage, goal: str):
        # ── Goal ──
        task = self.sample_task(goal)

        # ── Run（通过 runtime adapter） ──
        adapter = self.runtime_adapters[agent_image.runtime_adapter]
        events = []
        async for event in adapter.run(agent_image, task):
            events.append(event)
            await self.event_bus.publish(event)  # 统一事件推送

        # ── Observe（观察执行结果） ──
        result = self.extract_result(events)
        usage = self.extract_usage(events)

        # ── Score（LLM 柔性证明器评估） ──
        score = await self.score(result, agent_image.genome)

        # ── Reflect（反思 + 决策） ──
        if score.value >= self.threshold:
            return result  # 达标，无需修改

        reflection = await self.reflect(score, result, agent_image.genome)

        # ── Mutate（修改 Genome） ──
        new_genome = await self.mutate(agent_image.genome, reflection)
        new_genome.version += 1
        new_genome.parent_ids.append(agent_image.genome.id)

        # 持久化（磁盘即真理）
        await self.genome_store.save(new_genome)

        # ── 自指：Supervisor 自身也接受 OEDM ──
        await self.meta_oedm.run(
            agent_image=self.meta_image,
            goal=f"评估上次优化效果: delta={score.improvement}",
        )

        # ── Next Run ──
        return await self.run_cycle(
            agent_image.with_genome(new_genome), goal
        )
```

---

## 6. 工具集成层

### 6.1 MCP 协议接入

所有外部工具通过 **MCP (Model Context Protocol)** 统一接入，Claude Agent SDK 原生支持 MCP Server 连接。

```
┌─────────────────────────────────┐
│     Claude Agent SDK Runtime     │
│                                  │
│  ┌───────────────────────────┐  │
│  │    MCP Client Manager     │  │
│  │  ┌──────┐ ┌──────┐       │  │
│  │  │MCP-C1│ │MCP-C2│ ...   │  │
│  │  └──┬───┘ └──┬───┘       │  │
│  └─────┼────────┼───────────┘  │
└────────┼────────┼──────────────┘
         │        │
    ┌────▼──┐ ┌──▼─────┐
    │gitnexus│ │codeflow │  ... (各工具的 MCP Server)
    └───────┘ └────────┘
```

### 6.2 各工具接入方案

**gitnexus** — Git 操作增强
- MCP Server 封装 git 操作（diff、blame、log、branch 管理）
- Agent 通过 `gitnexus_diff`、`gitnexus_blame` 等工具调用
- 用于代码变更分析和进化追踪

**codeflow** — 代码流管理
- MCP Server 封装代码流操作（PR、review、merge）
- Agent 通过 `codeflow_create_pr`、`codeflow_review` 等工具调用
- 用于 Task Agent 的代码提交和审查

**gstack** — 技术栈管理
- MCP Server 封装依赖管理（安装、升级、兼容性检查）
- Agent 通过 `gstack_check`、`gstack_upgrade` 等工具调用
- 用于环境维护

**superpower** — 增强 Git 能力
- MCP Server 封装高级 Git 操作（rebase 策略、conflict 解决、cherry-pick）
- Agent 通过 `superpower_rebase`、`superpower_resolve` 等工具调用
- 用于复杂代码管理场景

---

## 7. 数据模型与状态管理

### 7.1 存储方案

**SQLite（本地）** — 所有持久化状态

| 表 | 用途 |
|----|------|
| `genomes` | Agent Genome 版本化存储 |
| `evaluations` | 评估记录（score, evaluator, timestamp） |
| `elo_ratings` | Elo 动态排名 |
| `evolution_history` | 进化事件日志 |
| `map_elites_archive` | MAP-Elites 多维质量档案 |
| `tasks` | 任务队列与执行记录 |

### 7.2 状态管理核心流程

```
Agent 执行 → 结果写入 evaluations
         → Elo 更新
         → Genome 版本 +1 并写入 genomes
         → MAP-Elites 归档更新
         → evolution_history 记录事件
         → 磁盘持久化（必须完成才算成功）
```

### 7.3 并发控制

- Genome 修改使用乐观锁（version 字段）
- 文件所有权检查：写入前验证最后修改时间
- tRPC 的 mutation 操作串行化执行

---

## 8. 实施路线图

### Phase 0：最小可运行闭环（1-2 天）

```
Task Agent ──execute──► Result ──evaluate──► Optimizer
    ▲                                        │
    └──────── genome update ──────────────────┘
```

- 单个 Task Agent + 单个 Optimizer Agent
- Genome 仅包含 instructions 字段
- SQLite 存储，CLI 输出日志
- **验证：Optimizer 能否通过修改 instructions 改进 Task Agent 表现**

### Phase 1：双群体 + Elo（3-5 天）

- 多个 Task Agent 和 Optimizer Agent
- Elo 动态排名系统
- Softmax 采样匹配对手
- Textual TUI 显示实时状态

### Phase 2：MAP-Elites + 自指（1-2 周）

- MAP-Elites 多维质量档案
- Optimizer 自身被优化（真正的自指）
- Genome 完整字段（tools, hooks, mutation strategy）
- Web 界面可视化

### Phase 3：工具集成 + 生产化（2-4 周）

- gitnexus/codeflow/gstack/superpower MCP 接入
- Codex SDK 沙箱集成
- 权限管理和安全控制
- 完整的进化谱系追踪

---

## 9. 风险与待验证假设

| 风险 | 影响 | 缓解策略 |
|------|------|---------|
| LLM 不擅长修改自身 prompt | 自指闭环失败 | Level 0 先验证单 Agent OEDM 效果 |
| Elo 排名收敛过快 | 多样性丢失 | 引入 exploration bonus |
| Genome 变异导致 Agent 崩溃 | 系统不稳定 | Codex 沙箱隔离 + 变异前验证 |
| 上下文窗口限制 | 复杂 Genome 超出限制 | Genome 分层压缩，仅加载必要部分 |
| tRPC Python 生态不如 TS | Python Agent 集成成本高 | tRPC 底层是 HTTP，Python 直接 REST 调用 |
| Gödel 不完备性限制 | Agent 永远无法完全理解自身 | 接受不完备性，用柔性证明 + 多样性冗余 |
| 自修改破坏核心不变量 | 系统退化 | 参考 Darwin GM 进化树，支持回退 |

---

## 10. Von Neumann 映射与团队分工

### 10.1 Von Neumann 自复制自动机映射

| Von Neumann 组件 | 系统对应 | Agent SDK 实现 |
|-----------------|---------|---------------|
| **构造器 A** | Task Layer（执行任务） | Claude Agent SDK `query()` |
| **复制器 B** | Genome 传播机制 | Genome 序列化 + SQLite 存储 |
| **蓝图 I** | Genome（Agent 自描述） | YAML/JSON 配置文件 |
| **控制器 C** | Arch Layer（编排修改） | Orchestrator + OEDM 循环 |

### 10.2 团队分工映射

| 角色 | 对应层次 | 职责 |
|------|---------|------|
| **Researcher** | 理论层 | GRB/自指/OEDM 理论研究，产出研究报告 ✅ 已完成 |
| **Scout** | 技术层 | SDK 机制调研（Claude/Codex API、Hook、MCP） |
| **Solution Architect** | 架构层 | 综合理论+技术，设计系统架构（本文档） |
| **Builder** | 实现层 | 根据架构搭建原型，实现最小 OEDM 闭环 |

### 10.3 Codex + Claude 混合模式

| 场景 | Runtime | 角色 |
|------|---------|------|
| 任务执行（Task Layer） | Claude Agent SDK | 构造器：执行任务、生成代码 |
| 代码沙箱验证 | Codex Agent SDK | 隔离执行、安全验证 |
| 评估反思（Meta Layer） | Claude Agent SDK | 证明器：OEDM 的 Evaluate/Decide |
| 架构修改（Arch Layer） | Claude Agent SDK | 控制器：读写 Genome |
| 外部工具调用 | Claude Agent SDK (MCP) | 通过 MCP 协议调用 gitnexus 等 |

---

## 附录 A：关键术语对照

| 英文 | 中文 | 说明 |
|------|------|------|
| Self-referential | 自指 | 系统能引用和修改自身 |
| Closed loop | 闭环 | 反馈循环，输出作为新输入 |
| Genome | 基因组 | Agent 的可优化配置集合 |
| Elo rating | Elo 排名 | 动态竞技排名系统 |
| MAP-Elites | 多维质量档案 | 按多维特征保持高质量解 |
| Population | 群体 | 一组同类型 Agent |
| Mutation | 变异 | 对 Genome 的修改操作 |

## 附录 B：参考论文与资料

### 理论基础
1. **Escher-Loop**: "Self-Referential Optimization of Agent Populations" (arXiv 2604.23472)
2. **Gödel Agent**: "A Self-Evolving Framework for Recursive Self-Improvement" (ICLR 2025)
3. **Darwin Gödel Machine**: "Open-Ended Evolution of Self-Improving Agents" (arXiv 2505.22954)
4. **Meta HyperAgents**: "HyperAgents: Self-referential self-improving agents" (Meta AI Research, 2025)
5. **Gödel Machine**: Schmidhuber, "Fully Self-Referential Optimal Universal Self-improvers" (2003)
6. **Hofstadter**: *Gödel, Escher, Bach* (1979), *I Am a Strange Loop* (2007)
7. **Von Neumann**: *Theory of Self-Reproducing Automata* (1966)
8. **Wiener**: *Cybernetics* (1948) | **Ashby**: *Design for a Brain* (1952)

### 技术文档
9. **Claude Agent SDK**: https://docs.anthropic.com/en/docs/agent-sdk
10. **Codex Agent SDK**: https://openai.com/index/codex/
11. **Researcher 理论报告**: `research/GRB-self-reference-theory-report.md`
