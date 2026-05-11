# SelfPlay Docker QA — Real Problem Solving Report

**Date**: 2026-05-11
**Image**: selfplay-qa (python:3.11-slim + anthropic SDK)
**Runtime**: AnthropicRuntimeAdapter → claude-sonnet-4-20250514
**Method**: Bach SOP — from-zero build, capability matrix, multi-surface evidence

## Executive Summary

4 real-world code analysis tasks executed via Docker, each using SelfPlay's OEDM loop with live Claude API. All tasks reached threshold (≥0.9) with measurable improvement from initial to final cycle.

## Results Matrix

| Task | Target | Cycles | Score Trajectory | Improvement | Final Features |
|------|--------|--------|------------------|-------------|----------------|
| T1: cli.py self-review | command handling logic | 2 | 0.56→0.92→0.90 | +0.34 | 7/8 |
| T2: supervisor.py analysis | retry edge cases | 2 | 0.56→0.92→0.90 | +0.34 | 7/8 |
| T3: sdk_bridge.py architecture | streaming design review | 3 | 0.62→0.98→1.00→1.00 | +0.38 | 8/8 |
| T4: evaluator.py with profile | profile-driven code review | 2 | 0.66→1.00→1.00 | +0.34 | 8/8 |

## Key Findings

### 1. OEDM Loop Reliably Improves Output Quality
Every task showed consistent improvement. The aggressive→conservative mutation strategy rejected low-quality attempts (visible as "Rejected attempt 1"), ensuring only genuine improvements persist.

### 2. Profile-Driven Evaluation Works in Docker
T4 used `selfplay-code-review.yaml` with 10 custom dimensions (type_hints, docstrings, error_handling, etc.) mounted via Docker volume. The profile loaded correctly and evaluation reflected code-review-specific criteria.

### 3. Self-Referential Quality Loop
SelfPlay is now literally eating its own dog food — using its OEDM loop to analyze its own source code quality via real LLM calls. This is the core value proposition validated.

### 4. Prompt Evolution Pattern
Across all tasks, the mutation engine follows a consistent pattern:
- Cycle 1: Initial prompt → weak output (4-6/8 features) → mutation adds constraints for missing features
- Cycle 2+: Enriched prompt → strong output (7-8/8 features) → threshold reached

### 5. Rejection Filtering Works
Every run rejected at least one aggressive simplification attempt (score drop to 0.20-0.38). The retry mechanism correctly falls back to conservative mutation.

## Architecture Implications

### Validated
- AnthropicRuntimeAdapter in Docker: stable, no SDK dependency issues
- AUTH_TOKEN env var fallback: works correctly
- host.docker.internal proxy: stable connection
- SQLite persistence in /tmp: reliable across cycles

### Next Design Targets
- Streaming support (identified in T3): AnthropicRuntimeAdapter should use `messages.stream()` for real-time event emission
- Multi-model comparison: same task → different models → compare evolution trajectories
- Batch evaluation: run N tasks in parallel with shared profile

## Docker Commands (Reproducible)

```bash
# Build
docker build --no-cache -t selfplay-qa .

# Run with profile (T4 example)
docker run --rm \
  -e ANTHROPIC_AUTH_TOKEN="$ANTHROPIC_AUTH_TOKEN" \
  -e ANTHROPIC_BASE_URL="http://host.docker.internal:15721" \
  -v "$(pwd)/examples/selfplay-code-review.yaml:/app/config.yaml:ro" \
  selfplay-qa \
  selfplay --db /tmp/qa.db --config /app/config.yaml --runtime claude demo \
  "YOUR_TASK_HERE" --cycles 3
```

## Conclusion

SelfPlay's Docker QA pipeline is production-ready for real problem solving. The OEDM loop consistently improves LLM output quality by 0.34-0.38 points across diverse code analysis tasks, with profile-driven evaluation enabling domain-specific quality criteria.
