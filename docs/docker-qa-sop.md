# SelfPlay Docker QA SOP

**Version**: 1.1
**Last updated**: 2026-05-11
**Based on**: bach-orchestra Docker QA SOP + agent-self-evolution SOP + docker-qa-from-zero-best-practice-sop

> 核心口径（bach 铁律）：开发不是"写完再解释"，而是 **访谈提炼需求 → requirement ledger → Docker 中复现实验 → 只按证据修复 → replay 验证**。mock 只算 smoke，不可冒充真实 runtime 通过。

## 0. Pass Definition

A Docker QA run passes only when ALL of these are true:

1. Docker build completes from zero without cached layers.
2. `selfplay --version` returns the expected version inside the container.
3. `selfplay demo` completes 3 cycles in mock mode with score improvement > 0.
4. `pytest tests/` passes all tests inside the container.
5. `selfplay history` and `selfplay tree` produce valid output after a demo run.
6. No error events in the demo output.
7. Total improvement across cycles is > 0 (self-evolution is working).
8. Container exits cleanly (no crash, no orphan processes).
9. Requirement ledger exists with historical input trace.
10. Each capability has at least 2 types of evidence (CLI output + log/db/code).

Getting exit code 0 is not enough. Evidence must show the OEDM loop works.

## 1. PDCA Loop (from bach SOP)

```text
Read history/team messages
→ Requirement ledger
→ Mom Test interviews (3-round probing)
→ Rank gaps → acceptance matrix
→ Change code/docs
→ Docker verification (from-zero build)
→ pass/reject verdict per capability
→ replay failed row
→ commit/handoff
```

禁止跳过 ledger 直接改代码；禁止只用健康检查声明通过。

## 2. Capability Matrix

| # | Capability | Check | Evidence | Pass Gate |
|---|-----------|-------|----------|-----------|
| DQ-01 | Docker build | `docker build` succeeds | image SHA in output | Python 3.11 image, env 不泄密 |
| DQ-02 | Version check | `selfplay --version` = expected | stdout capture | matches pyproject.toml |
| DQ-03 | Demo smoke | `selfplay demo` runs 3 cycles | cycle count in output | 3 cycles visible |
| DQ-04 | Score improvement | total_improvement > 0 | last line of summary | +X.XX > 0 |
| DQ-05 | Threshold reached | at least 1 cycle shows "threshold reached" | decision field | convergence demonstrated |
| DQ-06 | Mutation works | at least 1 cycle shows mutation | "Mutate" line | prompt actually changed |
| DQ-07 | Rejected mutation | D5: at least 1 rejected attempt visible | "Rejected" line present | retry mechanism works |
| DQ-08 | Persistence | `selfplay history` shows records | non-empty output | SQLite round-trip |
| DQ-09 | AgentImage tree | `selfplay tree` shows parent chain | parent→child arrows | lineage traceable |
| DQ-10 | Unit tests | `pytest tests/` all pass | 3/3 passed | no regressions |
| DQ-11 | Clean exit | container exits with code 0 | `echo $?` after run | no crash |
| DQ-12 | No crash | no Python traceback in output | grep traceback | clean runtime |
| DQ-13 | JSON output | `selfplay demo --json` produces valid JSON | python3 json.tool | API-ready serialization |
| SP-16 | Profile loading | `selfplay demo --profile <name>` loads profile | correct dims from YAML | multi-profile works |
| SP-17 | Runtime fallback | missing PyYAML falls back to defaults | DEFAULT_DIMENSIONS used | no crash without pyyaml |
| SP-18 | LLM fallback | Claude API unavailble falls back to heuristic | heuristic eval runs | graceful degradation |
| SP-19 | Anchor evidence | external anchor scoring integrated | evidence path recorded | real eval calibration |
| SP-20 | Dimension approval | propose-dimension + review-proposal workflow | proposal stored + approved | Strange Loop origin |
| SP-21 | Profile versioning | profile_id + profile_version in records | history shows profile metadata | versioning traceable |
| SP-22 | Regression parity | default demo scores match Phase 2.2 | 0.42→0.47→0.52→0.88→0.90 | backward compatible |

## 3. Execution Steps

### 3.1 From-Zero Build

```bash
# Remove old image to force full rebuild
docker rmi selfplay-dev:latest 2>/dev/null || true

# Build from scratch (no cache)
docker build --no-cache -t selfplay-dev:latest .
```

### 3.2 Version Verification

```bash
docker run --rm selfplay-dev:latest selfplay --version
# Expected: selfplay 0.2.0
```

### 3.3 Demo Smoke Test

```bash
docker run --rm selfplay-dev:latest selfplay demo "Docker self-evolution smoke test" 2>&1 | tee /tmp/selfplay-qa-demo.txt
```

### 3.4 Unit Tests

```bash
docker run --rm selfplay-dev:latest python -m pytest tests/ -v
# Expected: 3 passed
```

### 3.5 Persistence + History

```bash
docker run --rm -v selfplay-qa-data:/workspace/selfplay/data \
  selfplay-dev:latest sh -c '
    selfplay demo "persistence test" > /dev/null 2>&1 &&
    selfplay history &&
    echo "---" &&
    selfplay tree
  '
```

### 3.6 JSON Output

```bash
docker run --rm selfplay-dev:latest selfplay demo --json "JSON output test" 2>&1 | python3 -m json.tool > /dev/null
```

### 3.7 docker-compose Verification

```bash
cp .env.example .env
docker compose up --build 2>&1 | tee /tmp/selfplay-qa-compose.txt
grep -q "Evolution Summary" /tmp/selfplay-qa-compose.txt && echo "PASS" || echo "FAIL"
```

### 3.8 One-Command QA

```bash
./qa-docker.sh
# 11 automated checks: build, version, demo, improvement, threshold, mutation,
# rejected, tests, exit, crash, JSON
```

## 4. Interview-Driven Development (Mom Test, from bach SOP)

### 4.1 Agent Interview Questions

对每个被访谈 agent 追问事实，不问观点：

1. 最近一次你想完成什么任务？
2. 你当时先看了哪里？
3. 哪一步让你停下来、猜测或重复确认？
4. 你绕过系统用了什么外部办法？
5. 如果只能修一个点，哪个点能让下一轮少花最多时间？

### 4.2 Three-Round Probing

Each QA run must answer at three levels:

**Round 1 (Surface)**: Does the demo output look correct? Any errors?
**Round 2 (Mechanism)**: Does evaluator correctly identify weaknesses? Does mutator change prompt?
**Round 3 (Essential)**: Is self-evolution real (driven by eval_result.weaknesses)? Would 10+ cycles converge?

### 4.3 Mom Test Findings (2026-05-11)

**SA Interview:**
- Q3: Mock's deterministic keyword-matching makes "rejected mutations" a logical contradiction — must actively manufacture degradation.
- Q5: Evaluator's 8 regex checks → data-driven (config.yaml). One YAML array replaces 8 if-else.

**Builder Interview:**
- Q3: System optimizes evaluator keywords, not real user satisfaction. Rejection credibility is in supervisor re-eval, not mutator itself.
- Q5: Config-driven evaluator + per-feature evidence ledger. Failed dimension IDs drive structured mutation.

**Researcher Interview:**
- Q3: Cursor $0 marketing → $2B ARR overturned "need精心营销" assumption. Evolution tree screenshots = natural shareable content (emergent insight).
- Q5: Reposition from "self-improving AI" → "watch your AI get smarter" (Tamagotchi hook). README reverse: experience first, theory later.

**Master Interview:**
- Q3: Builder silent completion caused false replace (code nearly lost). start_task lock conflicts (3x). Supervisor auto-spawn waste.
- Q5: Agents must send confirmation after file writes. Replace must check disk output first.

**Three-way convergence**: SA + Builder + Master independently identified config-driven evaluator as highest-leverage improvement.

## 5. Requirement Ledger

| Ref | Source | Capability | Acceptance | Status |
|-----|--------|-----------|------------|--------|
| RL-01 | User: "pip install selfplay" | pip installable | `pip install -e .` succeeds | PASS |
| RL-02 | User: 6 CLI commands | demo/run/history/tree/tui/init/status | all subcommands work | PASS |
| RL-03 | User: OEDM closed loop | Observe→Eval→Decide→Mutate | 4 stages visible per cycle | PASS |
| RL-04 | User: self-evolution not fake | eval_result drives mutation | weaknesses → prompt change | PASS |
| RL-05 | User: D5 rejected mutation | show rejected attempts | "Rejected" line visible | PASS |
| RL-06 | User: Docker QA | works in Docker container | all DQ checks pass | PASS |
| RL-07 | Phase 1 spec | scores change across cycles | max(scores) > min(scores) | PASS |
| RL-08 | Phase 1 spec | threshold reached in ≤3 cycles | "threshold reached" in output | PASS |
| RL-09 | Bach SOP | PDCA loop followed | ledger + interview + docker evidence | PASS |
| RL-10 | Bach SOP | Mom Test interview | SA interviewed, findings recorded | PASS |
| RL-11 | Phase 2.1 spec | Config-driven evaluator | YAML dims load + weight normalization | PASS |
| RL-12 | Phase 2.1 spec | FeatureBreakdown per dimension | id/label/passed/score/weight/evidence in JSON | PASS |
| RL-13 | Phase 2.2 spec | Features persistence | SQLite features_json round-trip | PASS |
| RL-14 | Phase 2.2 spec | Structured mutation | failed_feature_ids drive mutator targets | PASS |
| RL-15 | Phase 2.3 spec | Multi-profile support | --profile flag + YAML profiles load | PASS |
| RL-16 | Phase 2.3 spec | Dimension proposals | propose-dimension/review-proposal workflow | PASS |
| RL-17 | Phase 2.3 spec | Profile versioning | profile_id/profile_version in records | PASS |
| RL-18 | Phase 2.3 spec | Backward compatibility | default behavior = Phase 2.2 identical | PASS |
| RL-19 | Mom Test | Three-way convergence | SA+Builder+Master agree on config-driven evaluator | PASS |
| RL-20 | PMF Research | Value anchor identified | "用户控制 AI 怎么进化" not "自进化" concept | CONFIRMED |

## 6. Evidence Gate (Mandatory)

**Every QA run MUST produce a report before marking PASS.** No exceptions.

Evidence gate rules (from Builder QA review + Bach SOP):

1. **No evidence = no PASS**: Each capability MUST have `command`, `stdout excerpt`, `exit code`, `verdict`, and `evidence path`. Missing any field = SKIP (not PASS).
2. **Two-surface minimum**: Each capability needs evidence from at least 2 surfaces (CLI output + JSON/SQLite/file/code).
3. **No mock evidence**: Unit test mocks do not count as Docker QA evidence. Only real Docker container output counts.
4. **Report must be committed**: QA report file must exist in `docs/` before any capability is declared PASS.
5. **From-zero verification**: Full QA must include `docker rmi` + `--no-cache` build. Incremental builds only acceptable for quick iteration, not final PASS.

**Template for each capability row:**

```
| ID | Command | Exit Code | Stdout Excerpt | Evidence Path | Verdict |
|----|---------|-----------|----------------|---------------|---------|
| DQ-01 | `docker build --no-cache -t selfplay-dev .` | 0 | `sha256:5382557453...` | /tmp/qa-build.log | PASS |
```

## 7. QA Report Template

```markdown
# SelfPlay Docker QA Report

- Date:
- Git commit / dirty files:
- Docker profile: smoke | standard | from-zero | regression
- Resource baseline:
- Requirement ledger: see §5

| ID | Verdict | Evidence | Notes / next TODO |
|---|---------|----------|-------------------|
| DQ-01 | pass/fail/skip | path/command/log | ... |

## Mom Test Findings
- Agent:
- Observed blocker:
- Evidence:
- Product TODO:

## Final Verdict
PASS / REJECT / BLOCKED, with reason.
```

## 7. Verified QA Results (2026-05-11)

```
=== SelfPlay Docker QA (bach SOP) ===
  [PASS] DQ-01 Build completes
  [PASS] DQ-02 selfplay --version: selfplay 0.2.0
  [PASS] DQ-03 3 cycles visible
  [PASS] DQ-04 Threshold reached
  [PASS] DQ-05 Score improves (+0.48)
  [PASS] DQ-06 Mutation applied
  [PASS] DQ-07 D5 Rejected visible
  [PASS] DQ-10 All tests pass (3/3)
  [PASS] DQ-11 Clean exit (code 0)
  [PASS] DQ-12 No Python traceback
  [PASS] DQ-13 Valid JSON output
  PASS: 11 | FAIL: 0 | SKIP: 0
QA PASSED
```

## 8. Failure Response

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Build fails | Missing files in COPY | Check .dockerignore, verify source layout |
| Version mismatch | Stale Docker cache | `docker build --no-cache` |
| Score not improving | Evaluator or mutator broken | Check eval_result.weaknesses non-empty |
| No mutation | Threshold too low or score already high | Lower threshold or check initial prompt |
| Test failure | Code regression | Run `pytest tests/ -v` locally first |
| JSON invalid | Serialization bug | Check `result_payload()` output |
