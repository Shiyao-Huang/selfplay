# SelfPlay Docker QA 报告 — Phase 2.1 Config-Driven Evaluator

**结果**: PASS
**日期**: 2026-05-11
**版本**: 0.2.0 + Phase 2.1 (config-driven evaluator)
**QA Profile**: Phase 2.1 regression + new capability verification
**参考 spec**: `docs/phase2-config-driven-evaluator.md` v1.1

## 构建

| 项目 | 值 |
| --- | --- |
| `docker build --no-cache` | exit 0, 含 pyyaml |
| 镜像 | `selfplay-qa` sha256:a599bd29c9c9 |
| 基础镜像 | python:3.11-slim |
| 新增依赖 | pyyaml (for evaluation.dimensions config parsing) |

## 能力矩阵 — 逐项证据

### SP-11: Config-driven evaluator

| 字段 | 值 |
| --- | --- |
| command | `selfplay --config /app/data/custom.yaml --db /app/data/custom.db demo "技术架构分析" --cycles 1 --json` |
| exit code | 0 |
| config | 2 custom dimensions: humor(0.5) + tech_depth(0.5) |
| stdout excerpt | `"score_before": 0.5, "score_after": 0.55` |
| verdict | PASS |
| evidence | Custom dimensions loaded via PyYAML; score 0.5 = 1/2 dimensions passed; verified both dimensions work individually: output with "有趣"+"架构" → score=1.0 |

### SP-13: 向后兼容

| 字段 | 值 |
| --- | --- |
| command | `selfplay --config /app/data/selfplay.yaml --db /app/data/selfplay.db demo --cycles 3 --json` (no evaluation.dimensions in config) |
| exit code | 0 |
| stdout excerpt | `"total_improvement": 0.58, "stopped_early": true` |
| verdict | PASS |
| evidence | Score trajectory: 0.42→0.47→1.00→1.00, identical to Phase 1 results |

### SP-14: 默认 parity

| 字段 | 值 |
| --- | --- |
| command | Same as SP-13 |
| exit code | 0 |
| stdout excerpt | Cycle 1: 0.42→0.47 / Cycle 2: 0.68→1.00 / Cycle 3: 1.00→1.00 |
| verdict | PASS |
| evidence | Total improvement +0.58 = Phase 1 baseline; DEFAULT_DIMENSIONS 8 items, total weight=1.0; score calculation identical |

### SP-15: 自定义配置变化

| 字段 | 值 |
| --- | --- |
| command | Python verification: `HeuristicEvaluator(dimensions=config.dimensions).evaluate_text(...)` |
| exit code | 0 |
| stdout excerpt | `Dimensions loaded: 2` / `humor: passed=True score=0.5` / `tech_depth: passed=True score=0.5` |
| verdict | PASS |
| evidence | Custom 2-dimension config correctly loaded; weight normalization: 0.5/1.0=0.5 per dimension; evidence shows matched keywords |

## 本地验证（非 Docker）

| 测试 | 结果 |
| --- | --- |
| DEFAULT_DIMENSIONS count | 8 ✅ |
| DEFAULT_DIMENSIONS total weight | 1.0 ✅ |
| Phase 1 score parity (evaluate_text) | 0.32 for same input ✅ |
| Custom dimensions (2 dims, humor+tech_depth) | Score 1.0 when both keywords present ✅ |
| FeatureBreakdown fields | id/label/passed/score/raw_weight/effective_weight/evidence all populated ✅ |
| OEDM full cycle | 0.42→1.00, +0.58, stopped_early=true ✅ |
| D5 rejected mutation | Rejected in Cycle 2 ✅ |
| Features in eval result | 8 features per cycle ✅ |

## Phase 2.1 代码变更清单

| 文件 | 变更 |
| --- | --- |
| `src/selfplay/config.py` | +EvaluationDimension dataclass, +_parse_dimensions(), +dimensions field |
| `src/selfplay/models.py` | +FeatureBreakdown dataclass, +EvalResult.features field |
| `src/selfplay/evaluator.py` | +DEFAULT_DIMENSIONS, +_check_dimension(), HeuristicEvaluator accepts custom dimensions |
| `Dockerfile` | +pyyaml |
| `pyproject.toml` | +evaluation = ["pyyaml>=6.0"] |

## 失败项 TODO

无。

## 备注

- Phase 2.2 (SP-12: history --json features) 待实现
- PyYAML optional: 无 pyyaml 时 fallback 到 DEFAULT_DIMENSIONS，不报错
