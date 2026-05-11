# SelfPlay Architecture Diagrams (Mermaid)

> **Version**: Phase 2.2 (implemented + verified)
> **Date**: 2026-05-11
> **Source**: docs/architecture.md + src/selfplay/ code

---

## 1. System Overview

```mermaid
graph TB
    subgraph CLI["CLI Interface"]
        DEMO["selfplay demo"]
        RUN["selfplay run"]
        HISTORY["selfplay history"]
        TREE["selfplay tree"]
        INIT["selfplay init"]
        TUI["selfplay tui"]
    end

    subgraph SUPERVISOR["OEDM Supervisor"]
        O["Observe"]
        E["Evaluate"]
        D["Decide"]
        M["Modify"]
        O --> E --> D --> M
        M -.->|next cycle| O
    end

    subgraph EVALUATOR["Config-Driven Evaluator"]
        CONFIG["selfplay.yaml<br/>evaluation.dimensions"]
        DIMS["8 Default Dimensions<br/>or custom config"]
        BREAKDOWN["FeatureBreakdown<br/>per-dimension evidence"]
        CONFIG --> DIMS --> BREAKDOWN
    end

    subgraph RUNTIMES["Runtime Adapters"]
        MOCK["Mock<br/>zero-dep demo"]
        CLAUDE["Claude SDK<br/>production"]
        CODEX["Codex SDK<br/>sandbox"]
    end

    subgraph STORAGE["Genome Store (SQLite)"]
        DB[("SQLite")]
        IMAGES["AgentImages<br/>version chain"]
        EVALS["Evaluations<br/>features_json"]
        EVENTS["Runtime Events"]
    end

    CLI --> SUPERVISOR
    SUPERVISOR --> EVALUATOR
    SUPERVISOR --> RUNTIMES
    SUPERVISOR --> STORAGE
    EVALUATOR -->|EvalResult.features| STORAGE
```

## 2. OEDM Loop (Config-Driven)

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Supervisor
    participant Adapter as Runtime Adapter
    participant Evaluator as ConfigDrivenEvaluator
    participant Mutator as RuleBasedMutator
    participant Store as GenomeStore

    User->>CLI: selfplay demo "task"
    CLI->>Supervisor: run_evolution(task, cycles=3)

    loop Each Cycle
        Supervisor->>Adapter: run(image, goal)
        Adapter-->>Supervisor: RuntimeEvents

        Note over Supervisor: Observe
        Supervisor->>Supervisor: extract_result(events)

        Note over Supervisor: Evaluate
        Supervisor->>Evaluator: evaluate(task, output, image)
        Evaluator->>Evaluator: _check_dimension() × 8
        Evaluator-->>Supervisor: EvalResult {score, features[], weaknesses}

        Note over Supervisor: Decide + Modify
        alt score >= threshold
            Supervisor-->>Store: threshold reached
        else score < threshold
            Supervisor->>Mutator: mutate(image, eval_result)

            alt Attempt 1 (aggressive)
                Mutator->>Mutator: aggressive simplification
                Mutator->>Evaluator: preview re-eval
                alt preview_score < current
                    Note over Mutator: ❌ Rejected
                else preview_score >= current
                    Note over Mutator: ✅ Accepted
                end
            else Attempt 2 (conservative)
                Mutator->>Mutator: rewrite from failed features
                Mutator->>Evaluator: preview re-eval
                Note over Mutator: ✅ Accepted if improved
            end

            Mutator-->>Supervisor: new_image or None
        end

        Supervisor->>Store: save_evaluation(record, features)
        Supervisor->>Store: save_agent_image(new_image)
    end

    Supervisor-->>CLI: EvolutionResult
    CLI-->>User: JSON or formatted output
```

## 3. Config-Driven Evaluator Detail

```mermaid
graph LR
    subgraph Config["selfplay.yaml"]
        Y1["evaluation.dimensions:"]
        Y2["  - id: conclusion"]
        Y3["  - id: evidence"]
        Y4["  - id: next_step"]
        Y5["  - ... 8 total"]
    end

    subgraph Default["DEFAULT_DIMENSIONS"]
        D1["conclusion (0.16)"]
        D2["evidence (0.16)"]
        D3["error_handling (0.14)"]
        D4["next_step (0.12)"]
        D5["performance (0.12)"]
        D6["examples (0.10)"]
        D7["structure (0.10)"]
        D8["length (0.10)"]
    end

    subgraph Check["_check_dimension()"]
        C1{{type=keyword?}}
        C2["keyword search"]
        C3{{type=pattern?}}
        C4["regex search"]
        C5{{type=length?}}
        C6["len(output) >= min"]
        C1 -->|yes| C2
        C1 -->|no| C3
        C3 -->|yes| C4
        C3 -->|no| C5
    end

    subgraph Result["FeatureBreakdown"]
        R1["id: str"]
        R2["label: str"]
        R3["passed: bool"]
        R4["score: float"]
        R5["raw_weight → effective_weight"]
        R6["evidence: str (≤80 chars)"]
    end

    Config -->|pyyaml| Check
    Default -->|no config| Check
    Check --> Result

    subgraph Normalize["Weight Normalization"]
        N1["effective_weight =<br/>raw_weight / sum(enabled weights)"]
    end
    Result --> Normalize
```

## 4. Genome / AgentImage Version Chain

```mermaid
graph TD
    subgraph Evolution["SelfPlay Evolution Tree"]
        V1["v1 (0.42)<br/>basic prompt"]
        V2["v2 (0.68)<br/>+error handling +null checks"]
        V3["v3 (0.95)<br/>+input validation +optimization"]

        V1 -->|mutated_prompt| V2
        V2 -->|mutated_prompt| V3

        V1 -.->|aggressive attempt rejected| R1["❌ score 0.38"]
        V2 -.->|conservative accepted| V3
    end

    subgraph Image["AgentImage Fields"]
        F1["id: image-xxxx"]
        F2["version: 1 → 2 → 3"]
        F3["prompt: compressed"]
        F4["parent_id: chain"]
        F5["eval.score: trajectory"]
        F6["runtime_adapter: mock"]
    end

    V1 --> Image
```

## 5. Data Flow: Docker QA Verification

```mermaid
graph LR
    subgraph Input["User Input"]
        TASK["task string"]
        CFG["config.yaml (optional)"]
    end

    subgraph Process["OEDM Process"]
        SEED["seed AgentImage"]
        CYCLE["3 cycles × OEDM"]
        EVAL["evaluate_text()"]
        MUTATE["mutate()"]
        SAVE["save to SQLite"]
    end

    subgraph Output["Output Surfaces"]
        CLI_OUT["CLI formatted"]
        JSON_OUT["demo --json"]
        DB_OUT["SQLite persistence"]
        TREE_OUT["selfplay tree"]
        HIST_OUT["selfplay history --json"]
    end

    Input --> Process
    Process --> Output

    EVAL -->|"EvalResult.features<br/>8 × FeatureBreakdown"| JSON_OUT
    SAVE -->|"features_json column"| DB_OUT
    DB_OUT -->|"recent_evaluations()"| HIST_OUT
```

## 6. Phase Roadmap (Implemented)

```mermaid
gantt
    title SelfPlay Phase Progress
    dateFormat YYYY-MM-DD
    axisFormat %m/%d

    section Phase 1
    OEDM Loop + CLI + Docker          :done, p1, 2026-05-09, 2d
    Docker QA 13/13 PASS              :done, p1qa, 2026-05-10, 1d

    section Phase 2.1
    Config-Driven Evaluator            :done, p21, 2026-05-11, 1d
    FeatureBreakdown + weight norm     :done, p21b, 2026-05-11, 1d
    SP-11/13/14/15 Docker QA           :done, p21qa, 2026-05-11, 1d

    section Phase 2.2
    Storage features_json              :done, p22, 2026-05-11, 1d
    CLI demo --json features           :done, p22b, 2026-05-11, 1d
    Mutator structured mutation        :done, p22c, 2026-05-11, 1d
    SP-12 Docker QA                    :done, p22qa, 2026-05-11, 1d

    section Phase 2.3
    Multi evaluation profiles          :p23a, 2026-05-12, 3d
    Claude evaluator calibration       :p23b, 2026-05-13, 3d
    Self-evolving dimensions           :p23c, 2026-05-15, 5d

    section Phase 3
    MAP-Elites multi-quality archive   :p3, 2026-05-18, 7d
    Elo + population evolution         :p3b, 2026-05-20, 7d
```
