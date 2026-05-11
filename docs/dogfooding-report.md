# SelfPlay Dogfooding Report

> **Date**: 2026-05-11
> **What**: SelfPlay uses its own `selfplay check` command to evaluate and improve its own source code

---

## What is Dogfooding?

SelfPlay evaluates itself using the `selfplay check` command with a 10-dimension code-review profile. Each file gets a score (0-1.0) across: type hints, docstrings, error handling, logging, type safety, param docs, test markers, comments, complexity, return annotations.

## Before → After

| File | Before | After | +Δ | Fix Date |
|------|--------|-------|-----|----------|
| `models.py` | 0.50 | **1.00** | +0.50 | 2026-05-11 |
| `storage.py` | 0.50 | **1.00** | +0.50 | 2026-05-11 |
| `tree_export.py` | 0.48 | **0.90** | +0.42 | 2026-05-11 |
| `cli.py` | 0.92 | 0.92 | — | already strong |
| `supervisor.py` | 0.82 | 0.82 | — | already strong |
| `config.py` | 0.82 | 0.82 | — | already strong |
| `evaluator.py` | 0.72 | 0.72 | — | good |
| `sdk_bridge.py` | 0.72 | 0.72 | — | good |
| `analytics.py` | 0.68 | 0.68 | — | good |
| `mutator.py` | 0.58 | 0.58 | — | next batch |
| `oedm.py` | 0.58 | 0.58 | — | next batch |
| `agents.py` | 0.50 | 0.50 | — | next batch |
| `proposal.py` | 0.54 | 0.54 | — | next batch |
| `__init__.py` | 0.18 | 0.18 | — | minimal file |

**Average**: 0.61 → 0.73 (+0.12)

## How to Reproduce

```bash
# Check a single file
selfplay --config selfplay-code-review.yaml check src/selfplay/models.py

# JSON output for CI
selfplay --config selfplay-code-review.yaml check --json src/selfplay/models.py

# Docker from-zero verification
docker build -t selfplay-qa .
docker run --rm selfplay-qa \
  selfplay --config selfplay-code-review.yaml check src/selfplay/models.py

# Real Claude API evolution
docker run --rm \
  -e ANTHROPIC_AUTH_TOKEN="$ANTHROPIC_AUTH_TOKEN" \
  -e ANTHROPIC_BASE_URL="http://host.docker.internal:15721" \
  selfplay-qa \
  selfplay --runtime claude demo --cycles 3 "审查 src/selfplay/evaluator.py"
```

## The PMF Loop

```
selfplay check → expose weaknesses → targeted fix → re-check → measurable improvement
```

This is the core product value: **users control how their AI evolves**, with quantifiable evidence.

## Commits

- `9f6db05` — models.py 0.50→1.00
- `e67dceb` — storage.py 0.50→1.00
- `afecc1e` — tree_export.py 0.48→0.90
- `83eca0e` — selfplay check command + code-review profile
- `a6283df` — streaming support (SA)
- `d71a777` — real Claude API evolution in Docker (SA)
