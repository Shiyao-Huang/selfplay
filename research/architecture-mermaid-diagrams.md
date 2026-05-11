# SelfPlay 架构与迭代 Mermaid 图集

> **目标**：为 PDCA 迭代提供可视化架构参考，辅助团队对齐 + Docker QA + 产品迭代
> **日期**：2026-05-11
> **作者**：Researcher
> **用途**：README 配图 / 团队对齐 / PDCA 看板

---

## 1. SelfPlay 系统架构

```mermaid
graph TB
    subgraph CLI["CLI Interface"]
        CMD_RUN["selfplay run"]
        CMD_DEMO["selfplay demo"]
        CMD_HIST["selfplay history"]
        CMD_TREE["selfplay tree"]
        CMD_TUI["selfplay tui"]
    end

    subgraph CORE["OEDM Supervisor"]
        O[Observe<br/>观察执行结果]
        E[Evaluate<br/>多维度评估]
        D[Decide<br/>决定改进方案]
        M[Modify<br/>修改 Genome]
        O --> E --> D --> M
        M -.->|next cycle| O
    end

    subgraph EVAL["Config-driven Evaluator"]
        DIM["8 Dimensions<br/>correctness | quality<br/>robustness | efficiency<br/>safety | examples<br/>structure | next_step"]
        FB["FeatureBreakdown<br/>per-dimension score<br/>+ passed + evidence"]
        DIM --> FB
    end

    subgraph RUNTIME["Runtime Adapters"]
        MOCK["Mock Runtime<br/>零依赖演示"]
        CLAUDE["Claude Runtime<br/>Anthropic SDK"]
        CODEX["Codex Runtime<br/>沙箱隔离"]
    end

    subgraph STORAGE["Genome Store"]
        SQLITE["SQLite"]
        VERSION["Version Chain<br/>v1 → v2 → v3"]
        FEATURES["features_json<br/>per-cycle breakdown"]
        SQLITE --> VERSION
        SQLITE --> FEATURES
    end

    CLI --> CORE
    CORE --> EVAL
    CORE --> RUNTIME
    CORE --> STORAGE
    EVAL -->|EvalResult| CORE
```

---

## 2. OEDM 闭环流程

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Supervisor
    participant Evaluator
    participant Mutator
    participant Store

    User->>CLI: selfplay run "任务"
    CLI->>Supervisor: 启动 OEDM 循环

    loop Cycle 1..N
        Supervisor->>Supervisor: Observe — 执行任务
        Supervisor->>Evaluator: Evaluate — 多维度评估
        Evaluator-->>Supervisor: EvalResult(score, features, weaknesses)

        alt score >= threshold
            Supervisor->>Supervisor: 达标，跳过修改
        else score < threshold
            Supervisor->>Mutator: Decide — 基于 failed features 生成 mutation
            Mutator-->>Supervisor: 新 Genome 候选

            alt 新 score > 旧 score
                Supervisor->>Store: Modify — 保存新 Genome (v→v+1)
                Note over Store: features_json 持久化
            else 新 score <= 旧 score
                Note over Supervisor: ❌ REJECTED — 回退，重试
                Supervisor->>Mutator: 生成替代 mutation
            end
        end
    end

    Supervisor-->>CLI: 最终结果 + 进化摘要
    CLI-->>User: 进化树 + 分数趋势
```

---

## 3. Docker QA SOP 流程

```mermaid
flowchart TD
    START[("🚀 Docker QA 开始")] --> BUILD["docker compose up --build<br/>from-zero build"]
    BUILD --> PASS1{build 成功?}
    PASS1 -->|No| FIX_BUILD["修复 Dockerfile<br/>记录证据"]
    FIX_BUILD --> BUILD

    PASS1 -->|Yes| SP01["SP-01: selfplay demo<br/>3 轮进化, score 上升"]
    SP01 --> SP11["SP-11: config-driven evaluator<br/>custom dimensions"]
    SP11 --> SP12["SP-12: history features<br/>持久化验证"]
    SP12 --> SP13["SP-13: 向后兼容<br/>无 config = Phase 1 行为"]
    SP13 --> SP14["SP-14: 默认 parity<br/>score 轨迹一致"]
    SP14 --> SP15["SP-15: 自定义配置<br/>权重归一化"]

    SP15 --> EVIDENCE{"每项有<br/>command + stdout +<br/>exit code + verdict?"}
    EVIDENCE -->|No| MISSING["补充 evidence<br/>禁止 mock 证据"]
    MISSING --> EVIDENCE

    EVIDENCE -->|Yes| REPORT["落盘 QA 报告<br/>docs/docker-qa-report-*.md"]
    REPORT --> DONE("✅ Docker QA PASS")

    style DONE fill:#4CAF50,color:white
    style FIX_BUILD fill:#FF9800,color:white
    style MISSING fill:#FF9800,color:white
```

---

## 4. 发布 PDCA 迭代循环

```mermaid
flowchart LR
    subgraph PLAN["📋 PLAN"]
        P1["历史输入需求账本<br/>README 承诺<br/>用户反馈<br/>规格要求"]
        P2["Mom Test 访谈<br/>Q1-Q10<br/>三轮追问"]
        P3["排序主要矛盾<br/>按杠杆排序<br/>→ TODO"]
        P1 --> P2 --> P3
    end

    subgraph DO["🔧 DO"]
        D1["Phase 实现<br/>SA 编码<br/>Builder QA watch"]
        D2["Docker QA<br/>from-zero build<br/>SP-01~SP-15"]
        D3["Researcher<br/>竞品调研<br/>文案打磨"]
        D1 --> D2 --> D3
    end

    subgraph CHECK["✅ CHECK"]
        C1["Builder 独立复测<br/>本地 + Docker"]
        C2["Evidence Gate<br/>command/stdout/<br/>exit code/verdict"]
        C3["互动数据收集<br/>Evidence Tracker"]
        C1 --> C2 --> C3
    end

    subgraph ACT["🔄 ACT"]
        A1["修复项 + 验证证据"]
        A2["访谈结论归档"]
        A3["下一轮更好问题<br/>+ 文案 v(N+1)"]
        A1 --> A2 --> A3
    end

    PLAN --> DO --> CHECK --> ACT -->|"循环"| PLAN
```

---

## 5. 发布后 48h 增长飞轮

```mermaid
flowchart TB
    T0["T+0<br/>Show HN 发布<br/>英文首发"] --> T2H["T+2h<br/>Reddit r/LocalLLaMA<br/>r/SideProject"]
    T2H --> T12H["T+12h<br/>V2EX + 即刻<br/>带 HN 链接引流"]
    T12H --> T24H["T+24h<br/>掘金横评长文<br/>多平台互引"]

    T24H --> FEEDBACK["T+48h<br/>社区反馈汇总<br/>GitHub Issue"]
    FEEDBACK --> ITERATE["下一轮 PDCA<br/>文案 v2 → v3<br/>功能优化"]
    ITERATE -->|"持续循环"| T0

    subgraph METRICS["关键指标"]
        M1["Stars: 100→300+"]
        M2["V2EX 回复: 20→50+"]
        M3["掘金点赞: 50→200+"]
        M4["Issues/PR: 3→10+"]
    end

    FEEDBACK -.-> METRICS

    style T0 fill:#2196F3,color:white
    style T12H fill:#4CAF50,color:white
    style T24H fill:#FF9800,color:white
    style ITERATE fill:#9C27B0,color:white
```

---

## 6. SelfPlay 竞品定位图

```mermaid
quadrantChart
    title AI Agent 工具定位图 (2026)
    x-axis "低差异化" --> "高差异化"
    y-axis "低实用性" --> "高实用性"
    quadrant-1 "明星产品"
    quadrant-2 "创新者"
    quadrant-3 "淘汰区"
    quadrant-4 "实用工具"
    "Cursor": [0.3, 0.85]
    "aider": [0.35, 0.75]
    "Claude Code": [0.25, 0.8]
    "AutoGPT": [0.6, 0.3]
    "Darwin GM": [0.8, 0.4]
    "HyperAgents": [0.75, 0.35]
    "SelfPlay 🧬": [0.85, 0.7]
```

---

## 使用指南

| 图 | 用途 | 放置位置 |
|---|------|---------|
| §1 系统架构 | README 架构节、开发者文档 | README.md 架构节 |
| §2 OEDM 流程序列图 | 技术博客、开发者理解原理 | blog/技术博客 |
| §3 Docker QA 流程 | Docker QA SOP 文档 | docs/docker-qa-sop.md |
| §4 PDCA 迭代循环 | 团队对齐、复盘模板 | docs/pdca-template.md |
| §5 增长飞轮 | 发布策略文档 | research/ 发布策略 |
| §6 竞品定位图 | 投资人/社区展示 | README 或 landing page |

---

*图集完成。可直接嵌入 GitHub README（mermaid 原生支持）。*
