# SelfPlay Docker QA 报告 — Phase 2.3 Multi-Profiles + Self-Evolving Dimensions

**结果**: PASS (7/7)
**日期**: 2026-05-11
**版本**: 0.2.0 + Phase 2.3
**QA Profile**: Phase 2.3 new capability + regression verification
**参考 spec**: `docs/phase2.3-docker-qa-plan.md`

## 构建

| 项目 | 值 |
| --- | --- |
| `docker build --no-cache` | exit 0 |
| 镜像 | `selfplay-qa` sha256:0b575d091404 |
| 基础镜像 | python:3.11-slim |
| 新增文件 | `src/selfplay/proposal.py` |

## 能力矩阵 — 逐项证据

### SP-16: Profile loading

| 字段 | 值 |
| --- | --- |
| command | `selfplay --config profile.yaml --db qa-profile.db demo "SP-16" --json` |
| exit code | 0 |
| config | 1 profile: mock-minimal v5, 2 dims (conclusion+evidence) |
| stdout excerpt | `"profile_id": "qa-mock-profile", "profile_version": 5` |
| verdict | PASS |
| evidence | Selected profile loaded; 2 custom dimensions visible in features; score 1.0 on first cycle |

### SP-17: Runtime-specific profile fallback

| 字段 | 值 |
| --- | --- |
| command | `selfplay --config fallback.yaml --runtime mock demo "SP-17" --json` |
| exit code | 0 |
| config | 1 profile: claude-only (no mock profile) |
| stdout excerpt | `"profile_id": null, "profile_version": null` |
| verdict | PASS |
| evidence | Missing profile → fallback to DEFAULT_DIMENSIONS (8 items); no crash, warning-free |

### SP-18: LLM calibration graceful fallback

| 字段 | 值 |
| --- | --- |
| command | `SELFPLAY_ENABLE_LLM_CALIBRATION=1 selfplay --runtime mock demo "SP-18" --json` |
| exit code | 0 |
| stdout excerpt | Heuristic features present, no error events |
| verdict | PASS |
| evidence | No SDK installed → heuristic result preserved; no secret printed; no crash |

### SP-19: External anchor evidence

| 字段 | 值 |
| --- | --- |
| command | `selfplay demo "SP-19" --json` → parse features |
| exit code | 0 |
| stdout excerpt | `conclusion: passed=True, evidence=matched_pattern: 结论` |
| verdict | PASS |
| evidence | 3 features with anchor evidence (`matched_pattern:`, `matched_keyword:`, `length=`); evidence format consistent |

### SP-20: Agent-proposed dimension approval

| 字段 | 值 |
| --- | --- |
| command | `propose-dimension` → `list-proposals` → `review-proposal --approve` → `list-proposals --all` |
| exit code | 0 |
| stdout excerpt | `status: "pending"` → `status: "approved"` |
| verdict | PASS |
| evidence | Full lifecycle: submit → pending → approve → all shows approved; JSON fields: id/label/keywords/weight/rationale/status/reviewed_at/review_note |

### SP-21: Profile versioning in history

| 字段 | 值 |
| --- | --- |
| command | `selfplay --config profile.yaml demo --json` → `selfplay history --json` |
| exit code | 0 |
| config | hist-profile v2 |
| stdout excerpt | `"profile_id": "hist-profile", "profile_version": 2` in history |
| verdict | PASS |
| evidence | Evaluation record links profile id/version; history --json returns both fields |

### SP-22: Regression parity

| 字段 | 值 |
| --- | --- |
| command | `selfplay demo "parity test" --cycles 3 --json` |
| exit code | 0 |
| stdout excerpt | Cycle 1: 0.42→0.47 / Cycle 2: 0.52→0.88 / Cycle 3: 0.9→0.9 |
| verdict | PASS |
| evidence | Score trajectory consistent with Phase 2.2 baseline; 8 default dimensions; total improvement +0.48; `profile_id: null` for default mode |

## Phase 2.3 代码变更清单

| 文件 | 变更 |
| --- | --- |
| `src/selfplay/config.py` | +EvaluationProfile dataclass, +_parse_profiles(), +resolve_profile(), +profile field |
| `src/selfplay/models.py` | +EvaluationRecord.profile_id, +EvaluationRecord.profile_version |
| `src/selfplay/storage.py` | +_ensure_profile_columns(), save_evaluation/recent_evaluations with profile metadata |
| `src/selfplay/supervisor.py` | +_resolve_dimensions(), profile passthrough, profile_id in EvaluationRecord |
| `src/selfplay/cli.py` | +--profile flag, +propose-dimension/review-proposal/list-proposals commands |
| `src/selfplay/proposal.py` | **新文件**: DimensionProposal, ProposalStore, merge_approved_into_profile |

## 失败项 TODO

无。

---

## Appendix: Real Claude API Docker QA (2026-05-11)

**首次在 Docker 中用真实 LLM 运行进化闭环。**

### 环境

| 项目 | 值 |
| --- | --- |
| Docker image | selfplay-qa (python:3.11-slim + anthropic SDK) |
| Runtime adapter | AnthropicRuntimeAdapter (anthropic Python SDK) |
| Model | claude-sonnet-4-20250514 |
| API auth | `ANTHROPIC_AUTH_TOKEN` env (proxy-managed) |

### Docker 命令

```bash
docker run --rm \
  -e ANTHROPIC_AUTH_TOKEN="$ANTHROPIC_AUTH_TOKEN" \
  -e ANTHROPIC_BASE_URL="http://host.docker.internal:15721" \
  selfplay-qa \
  selfplay --db /tmp/qa-real.db --runtime claude demo \
  "审查 _check_dimension 函数：当 dim.type 不是 'length' 且既没有 pattern 也没有 keywords 时，函数返回 passed=False 但 evidence='no_pattern_or_keywords'。这是否应该视为配置错误而非评估失败？" \
  --cycles 3
```

### 结果

| Cycle | Score | Features | Decision |
| --- | --- | --- | --- |
| 1 | 0.56 → 0.92 | 4/8 passed | Rejected 1 attempt, conservative enrichment |
| 2 | 1.00 → 1.00 | 8/8 passed | Threshold reached, early stop |

- **Total improvement: +0.44**
- **Early stop: Yes** (cycle 2 reached threshold)
- **Runtime events**: 5 per cycle (thread.started, turn.started, message, usage, turn.completed)

### 代码变更

| 文件 | 变更 |
| --- | --- |
| `sdk_bridge.py` | +AnthropicRuntimeAdapter (anthropic SDK direct, AUTH_TOKEN fallback) |
| `supervisor.py` | claude adapter → AnthropicRuntimeAdapter |
| `Dockerfile` | +anthropic package |
| `pyproject.toml` | sdk deps 加 anthropic>=0.30.0 |

### 验证意义

SelfPlay 首次在 Docker 中：
1. 连接真实 Claude LLM API
2. 对实际代码审查任务运行进化
3. 通过 OEDM 闭环将 Agent 输出从 0.56 提升到 1.00
4. 全程可复现（Docker + env injection + SQLite 持久化）
