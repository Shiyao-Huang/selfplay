# SelfPlay Docker QA 报告

**结果**: PASS
**日期**: 2026-05-10
**版本**: 0.2.0

## 构建

- `docker build --no-cache`: PASS — 38.5s，无缓存
- 镜像基础: python:3.11-slim
- 依赖: selfplay 0.2.0 (editable) + pytest + rich

## 能力矩阵

| ID | 能力 | 结果 | 证据摘要 |
| --- | --- | --- | --- |
| SP-01 | Docker 构建与容器启动 | PASS | `--no-cache` 构建成功，镜像 sha256:6c13e5a3 |
| SP-02 | 包版本与 Python 环境 | PASS | `selfplay 0.2.0`，Python 3.11.15，pip show 版本一致 |
| SP-03 | `selfplay init` 初始化 | PASS | selfplay.yaml + selfplay.db 创建，config 可解析 |
| SP-04 | `selfplay status` 状态查询 | PASS | `--json` 输出包含 genomes/agent_images/evaluations 计数 |
| SP-05 | `selfplay demo` OEDM 闭环 | PASS | 3 cycle 完成，0.42→1.0，总提升 +0.58，提前停止 |
| SP-06 | Score + Genome 持久化 | PASS | history 3 条记录，image v3，parent chain 3 级完整 |
| SP-07 | `selfplay run` 多轮进化 | PASS | 到达 threshold 后 early stop，正常行为 |
| SP-08 | D5 被拒绝的 mutation | PASS | Cycle 2: `❌ Rejected (attempt 1): score 0.48 < current 0.68`，保守策略 0.68→1.0 |
| SP-09 | 数据持久化与可恢复性 | PASS | SQLite: 5 agent_images, 6 evaluations, 19 runtime_events，volume 跨容器持久 |
| SP-10 | `--runtime` 切换 | PASS | claude: "SDK unavailable" error event（不崩溃）；codex: "reserved for Phase 2" error event |

## 失败项 TODO

无。所有 10 项通过。

## 多面证据覆盖

| SP | CLI 输出 | CLI --json | SQLite | 文件系统 |
| --- | --- | --- | --- | --- |
| SP-01 | ✅ | — | — | ✅ |
| SP-02 | ✅ | — | — | — |
| SP-03 | ✅ | — | — | ✅ |
| SP-04 | — | ✅ | — | — |
| SP-05 | ✅ | ✅ | ✅ | — |
| SP-06 | — | ✅ | ✅ | — |
| SP-07 | — | ✅ | — | — |
| SP-08 | ✅ | ✅ | — | — |
| SP-09 | — | — | ✅ | ✅ |
| SP-10 | — | ✅ | — | — |

每个能力项至少 1 个证据面，关键项（SP-05/06/08/09）有 2-3 个面。

## 备注

- D5 (per-cycle retry) 在 Cycle 2 自然触发：aggressive simplification score 0.48 被拒绝，conservative enrichment score 1.0 被接受
- Claude/Codex runtime adapters 在无 SDK 时优雅降级，产出 error event 而非异常退出
- 当前无 auth/OTP/团队/chat 概念，无需 Bach DQA-02/04/13 等能力
