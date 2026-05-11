# SelfPlay 架构图 — Mermaid 可视化 + PDCA 迭代基线

**版本**: Phase 2.2 完成 (2026-05-11)
**作者**: Solution Architect
**用途**: 架构可视化基线 → 驱动下一轮 PDCA 迭代

---

## 1. 系统全景架构

```mermaid
graph TB
    subgraph CLI["🖥 CLI 入口 (cli.py)"]
        CMD[selfplay run/demo/status/history/tree/tui]
    end

    subgraph Config["⚙ 配置层 (config.py)"]
        YAML[selfplay.yaml]
        DIMS[EvaluationDimension<br/>id/label/keywords/weight/type]
    end

    subgraph Supervisor["🧬 OEDM 主循环 (supervisor.py)"]
        SEED[seed AgentImage]
        RUN[run_cycle / _run_cycle_with_retries]
        EVAL_M[evaluate_and_mutate]
        EVOLVE[run_evolution<br/>多 cycle 进化]
    end

    subgraph Runtime["▶ 运行时适配层 (sdk_bridge.py)"]
        MOCK[MockRuntimeAdapter]
        CLAUDE[ClaudeRuntimeAdapter]
        CODEX[CodexRuntimeAdapter<br/>占位]
        EVENT[RuntimeEvent<br/>kind/content/runtime/metadata]
    end

    subgraph Evaluator["👁 评估层 (evaluator.py)"]
        HEUR[HeuristicEvaluator<br/>+ DEFAULT_DIMENSIONS ×8]
        LLM[ClaudeEvaluator<br/>skeleton]
        COMP[CompositeEvaluator<br/>heuristic + optional LLM]
        FB[FeatureBreakdown<br/>id/label/passed/score/evidence]
    end

    subgraph Mutator["🧬 变异层 (mutator.py)"]
        RULE[RuleBasedMutator<br/>threshold/focus_items/rewrite]
        PM[PromptMutator<br/>LLM rewrite skeleton]
    end

    subgraph Models["📦 数据模型 (models.py)"]
        AI[AgentImage<br/>prompt/tools/permissions/memory/eval]
        AG[AgentGenome<br/>instructions/version/parent]
        ER[EvalResult<br/>score/weaknesses/features]
        TR[TaskResult / EvaluationRecord]
    end

    subgraph Storage["💾 持久层 (storage.py)"]
        DB[(SQLite<br/>genomes / agent_images<br/>evaluations / runtime_events)]
    end

    CMD --> SEED
    CMD --> EVOLVE
    YAML --> DIMS
    DIMS --> HEUR

    SEED --> RUN
    EVOLVE --> RUN
    RUN --> MOCK
    RUN --> CLAUDE
    RUN --> CODEX
    MOCK --> EVENT
    CLAUDE --> EVENT
    CODEX --> EVENT

    EVENT --> COMP
    COMP --> HEUR
    COMP --> LLM
    HEUR --> FB
    HEUR --> ER
    LLM --> ER

    ER --> RULE
    ER --> PM
    RULE --> AI
    PM --> AI

    AI --> DB
    AG --> DB
    ER --> DB
    TR --> DB
    EVENT --> DB
```

## 2. OEDM 闭环流程

```mermaid
flowchart LR
    G["🎯 Goal<br/>(用户任务)"] --> O["👁 Observe<br/>RuntimeAdapter.run()"]
    O --> E["📊 Evaluate<br/>CompositeEvaluator.evaluate()"]
    E --> D{"⚡ Decide<br/>score ≥ threshold?"}
    D -->|"Yes"| P["✅ Persist<br/>no mutation"]
    D -->|"No"| M["🧬 Modify<br/>RuleBasedMutator.mutate()"]
    M --> R{"🔄 Re-evaluate<br/>preview_output()"}
    R -->|"improved"| P
    R -->|"rejected"| A["❌ Retry<br/>aggressive simplification"]
    A --> R
    P --> NEXT["➡️ Next Cycle<br/>或 stop"]

    style G fill:#e1f5fe
    style O fill:#fff3e0
    style E fill:#e8f5e9
    style D fill:#fce4ec
    style M fill:#f3e5f5
    style P fill:#e0f7fa
    style NEXT fill:#e1f5fe
```

## 3. 数据模型关系

```mermaid
erDiagram
    AgentGenome ||--o{ AgentImage : "to_agent_image"
    AgentImage ||--o{ AgentImage : "mutated_prompt (parent→child)"
    AgentImage ||--|| EvalState : "has"
    AgentImage ||--|| MemoryState : "has"
    AgentImage ||--|| PermissionConfig : "has"
    AgentImage }o--o{ ToolConfig : "has"
    EvalResult ||--o{ FeatureBreakdown : "features"
    EvaluationDimension ||--o{ FeatureBreakdown : "produces"

    AgentImage {
        string id PK
        int version
        string prompt
        string runtime_adapter
        string parent_id FK
        string created_at
    }

    EvalState {
        float score
        string rationale
        string last_goal
    }

    MemoryState {
        list notes
        list evaluation_history
        dict context
    }

    FeatureBreakdown {
        string id
        string label
        bool passed
        float score
        float effective_weight
        string evidence
    }

    EvaluationRecord {
        int cycle
        string stage
        float score_before
        float score_after
        string note
    }
```

## 4. Phase 2.1/2.2 变更热点

```mermaid
graph LR
    subgraph P21["Phase 2.1 ✅"]
        C1[config.py<br/>+EvaluationDimension<br/>+_parse_dimensions]
        C2[models.py<br/>+FeatureBreakdown<br/>+EvalResult.features]
        C3[evaluator.py<br/>+DEFAULT_DIMENSIONS<br/>+_check_dimension<br/>weight normalization]
    end

    subgraph P22["Phase 2.2 ✅"]
        C4[storage.py<br/>+features_json column<br/>idempotent ALTER TABLE]
        C5[supervisor.py<br/>+_eval_to_dict<br/>features passthrough]
        C6[cli.py<br/>+features in --json output]
        C7[mutator.py<br/>+structured failed labels<br/>from features]
    end

    C1 --> C3
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> C6
    C3 --> C7

    style P21 fill:#e8f5e9
    style P22 fill:#e3f2fd
```

## 5. Docker QA 能力矩阵状态

```mermaid
graph TD
    subgraph PASS["✅ 已通过 (18/18)"]
        SP1["SP-01: 构建与启动"]
        SP2["SP-02: seed + 默认 prompt"]
        SP3["SP-03: OEDM 单 cycle"]
        SP4["SP-04: 多 cycle 进化"]
        SP5["SP-05: 持久化 + 版本链"]
        SP6["SP-06: threshold 提前停止"]
        SP7["SP-07: CLI status"]
        SP8["SP-08: CLI history"]
        SP9["SP-09: CLI tree"]
        SP10["SP-10: 错误恢复"]
        SP11["SP-11: Config-driven evaluator"]
        SP12["SP-12: history --json features"]
        SP13["SP-13: 向后兼容"]
        SP14["SP-14: 默认 parity"]
        SP15["SP-15: 自定义配置"]
        SP16["SP-16: Docker from-zero QA"]
        SP17["SP-17: Mutator structured"]
        SP18["SP-18: CLI --json features"]
    end

    style PASS fill:#e8f5e9
```

## 6. PDCA 迭代分析 — 下一步机会

### 6.1 当前 Gap 识别

```mermaid
graph LR
    subgraph GAPS["🎯 迭代机会"]
        GAP1["Phase 2.3: 多 profiles<br/>+ Claude 校准"]
        GAP2["Web UI / TUI 实时监控"]
        GAP3["自进化维度<br/>dimensions 自我优化"]
        GAP4["多 Agent 协作<br/>Codex sandbox"]
        GAP5["国际化 id→guidance map"]
        GAP6["发布后 evidence gate<br/>48h PDCA 复盘"]
    end

    subgraph STRENGTH["💪 已有能力"]
        S1["OEDM 闭环"]
        S2["Config-driven evaluator"]
        S3["Feature breakdown"]
        S4["Docker QA 18/18"]
        S5["Bach SOP evidence"]
    end

    STRENGTH -->|迭代基线| GAPS

    style GAPS fill:#fff3e0
    style STRENGTH fill:#e8f5e9
```

### 6.2 PDCA 循环规划

```mermaid
flowchart TB
    subgraph PLAN["📋 PLAN"]
        P1["定义 Phase 2.3 scope"]
        P2["设定可量化目标"]
        P3["设计 Docker QA 新 capability"]
    end

    subgraph DO["🔨 DO"]
        D1["实现多 profiles"]
        D2["Claude evaluator 校准"]
        D3["TUI 实时监控"]
    end

    subgraph CHECK["✅ CHECK"]
        C1["Docker QA from-zero"]
        C2["Score trajectory 对比"]
        C3["Evidence gate 复盘"]
    end

    subgraph ACT["🎯 ACT"]
        A1["收敛到 threshold"]
        A2["发布新版本"]
        A3["更新 capability matrix"]
    end

    PLAN --> DO --> CHECK --> ACT
    ACT -->|"下一轮"| PLAN

    style PLAN fill:#e1f5fe
    style DO fill:#fff3e0
    style CHECK fill:#e8f5e9
    style ACT fill:#f3e5f5
```

## 7. 关键架构决策记录 (ADR)

| ADR | 决策 | 理由 | 状态 |
|-----|------|------|------|
| ADR-1 | SQLite 单文件持久 | 零部署依赖，CLI 友好 | ✅ 稳定 |
| ADR-2 | Protocol-based 抽象 | Runtime/Evaluator/Mutator 可插拔 | ✅ 稳定 |
| ADR-3 | Config-driven dimensions | Phase 1→2 核心杠杆点 | ✅ Phase 2.1 |
| ADR-4 | FeatureBreakdown 结构化 | 证据驱动变异，不再靠字符串 | ✅ Phase 2.2 |
| ADR-5 | PyYAML optional | mock 模式零依赖 | ✅ Phase 2.1 |
| ADR-6 | Per-cycle retry + aggressive simplification | 突破 D5 单点阻塞 | ✅ Phase 2.2 |
| ADR-7 | Codex adapter 占位 | 等 sandbox 成熟 | 🔜 Phase 2.3+ |

---

**下一步**: 用户决定 Phase 2.3 scope 或发布优先级。此文档作为架构可视化基线，支持 Bach SOP evidence-driven PDCA。
