# SelfPlay Docker QA Report — 2026-05-11

- **Date**: 2026-05-11
- **Git status**: no git repo (working directory)
- **Docker profile**: from-zero build
- **Image**: `selfplay-dev:latest` — `sha256:5382557453a5`, 177MB, created 2026-05-11 00:01:24 CST
- **Platform**: Python 3.11.15, pytest 9.0.3, linux/amd64
- **Requirement ledger**: see docs/docker-qa-sop.md §5

## Capability Matrix — Verdicts

| ID | Capability | Command | Verdict | Exit Code | Evidence |
|---|-----------|---------|---------|-----------|----------|
| DQ-01 | Docker build | `docker build -t selfplay-dev:latest .` | **PASS** | 0 | Image sha256:5382557453a5, 177MB |
| DQ-02 | Version | `docker run --rm selfplay-dev:latest selfplay --version` | **PASS** | 0 | stdout: `selfplay 0.2.0` |
| DQ-03 | Demo 3 cycles | `docker run --rm selfplay-dev:latest selfplay demo "Docker self-evolution smoke test"` | **PASS** | 0 | stdout: `Cycle 1/3`, `Cycle 2/3`, `Cycle 3/3` |
| DQ-04 | Score improvement | same as DQ-03 | **PASS** | 0 | stdout: `v1:0.42→0.47 → v2:0.52→0.88 → v3:0.90→0.90`, `Total improvement: +0.48` |
| DQ-05 | Threshold reached | same as DQ-03 | **PASS** | 0 | stdout: `no mutation: threshold reached` in Cycle 3 |
| DQ-06 | Mutation works | same as DQ-03 | **PASS** | 0 | stdout: Cycle 1 `aggressive simplification attempt`, Cycle 2 `modify prompt from eval_result` |
| DQ-07 | Rejected mutation | same as DQ-03 | **PASS** | 0 | stdout: Cycle 2 `❌ Rejected (attempt 1) score 0.38 < current 0.52` |
| DQ-08 | Persistence/history | `selfplay --db ... history` | **PASS** | 0 | 3 records: cycle 1 (0.42→0.47), cycle 2 (0.52→0.88), cycle 3 (0.90→0.90) |
| DQ-09 | AgentImage tree | `selfplay --db ... tree` | **PASS** | 0 | 3 images: root→v1→v2→v3 parent chain |
| DQ-10 | Unit tests | `docker run --rm selfplay-dev:latest python -m pytest tests/ -v` | **PASS** | 0 | `3 passed in 0.25s` |
| DQ-11 | Clean exit | `docker run --rm selfplay-dev:latest selfplay demo ...` | **PASS** | 0 | container exit code 0 |
| DQ-12 | No crash | grep Traceback in demo output | **PASS** | 0 | no Python traceback in any output |
| DQ-13 | JSON output | `selfplay demo --json ... \| python3 -m json.tool` | **PASS** | 0 | `JSON_VALID=true` |

## Summary

```
PASS: 13  |  FAIL: 0  |  SKIP: 0
```

## Score Trajectory

```
Cycle 1: 0.42 → 0.47 (aggressive simplification attempt)
Cycle 2: 0.52 → 0.88 (modify prompt from eval_result: weaknesses=缺少短结论;缺少复杂度;缺少示例)
Cycle 3: 0.90 → 0.90 (no mutation: threshold reached)
Total improvement: +0.48
```

## Mom Test Findings

### SA (Solution Architect)
- **Q3**: Mock deterministic keyword-matching makes "rejected mutations" a logical contradiction. Must actively manufacture degradation to demonstrate rejection. Design-level tension, not a bug.
- **Q5**: Highest leverage = Evaluator 8 regex checks from hardcoded → config.yaml data-driven. Prerequisite for Phase 2 MAP-Elites.

## Final Verdict

**PASS** — All 13 capability checks pass with command-level evidence. Bach SOP PDCA loop followed: historical input → requirement ledger → Mom Test interview → Docker from-zero verification → evidence report.
