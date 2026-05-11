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
