# SelfPlay Mermaid PDCA / Docker QA Mirror

> User directive: use `mermaid-architect` thinking to assist iteration, Docker QA research, and PDCA loops toward a world-class product.
>
> Note: `/Users/swmt/.cc-switch/skills/mermaid-architect/SKILL.md` was not available in this runtime, so this file is a fallback Mermaid architecture mirror.

## 1. Product PDCA Loop

```mermaid
flowchart LR
  A[Historical inputs\nteam logs + user messages + research] --> B[Requirement ledger]
  B --> C[Mom Test interviews\nSA / Builder / Researcher / Master]
  C --> D[Rank leverage points]
  D --> E[Implement small slice]
  E --> F[Docker QA evidence gate]
  F --> G{PASS?}
  G -- no --> H[Create TODO from evidence]
  H --> D
  G -- yes --> I[Update docs / README / launch assets]
  I --> J[Release or next phase]
  J --> A
```

## 2. Docker QA Evidence Gate

```mermaid
flowchart TD
  S[Start QA profile] --> P[Preflight\nresource + git/files + env]
  P --> B[From-zero build\nno stale image]
  B --> C[CLI smoke\nversion / demo / json]
  C --> D[Feature evidence\ndemo --json features]
  D --> E[Persistence evidence\nhistory --json + SQLite]
  E --> T[Tests\nunit + targeted regression]
  T --> R[Report on disk\ncommand + stdout + exit + verdict]
  R --> V{All evidence present?}
  V -- yes --> PASS[PASS]
  V -- no --> FAIL[REJECT\nNo evidence, no PASS]
```

## 3. Evaluator Evolution Architecture

```mermaid
flowchart LR
  CFG[selfplay.yaml\nevaluation.dimensions] --> EV[ConfigDrivenEvaluator]
  EV --> FB[FeatureBreakdown\nid label passed score evidence]
  FB --> ER[EvalResult\noverall + features + weaknesses]
  ER --> MU[Mutator\nfailed feature guidance]
  MU --> IMG[New AgentImage]
  IMG --> RUN[Next OEDM cycle]
  RUN --> EV

  FB --> HIST[history --json]
  FB --> DB[(SQLite features_json)]
  FB --> QA[Docker QA SP-11..15]
```

## 4. Launch PDCA Mirror

```mermaid
flowchart TD
  R[Research\nHN + V2EX + Juejin + Jike] --> A[Assets\nREADME + Chinese v2 copy + screenshots]
  A --> L[Launch waves\nT+0 EN / T+12 CN / T+24 longform]
  L --> M[Evidence tracker\n1h 12h 24h 48h]
  M --> Q[Qualitative comments\nobjections + highest-upvoted]
  Q --> N[Next copy version]
  N --> A
```

## Operating rule

Every major claim must point to one of: Docker command output, JSON output, SQLite/history evidence, source code line, or launch evidence tracker row. If it cannot be traced, it is a hypothesis, not a PASS.
