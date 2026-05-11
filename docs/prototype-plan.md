# 最小闭环原型搭建计划

> Builder Phase 0，2026-05-09。

## 当前边界

- 不抢最终架构决策；按 `docs/architecture.md` v0.2 先做可替换骨架。
- Phase 0 使用 mock runtime，避免在 SDK 调研未完成前绑定真实 Claude/Codex API。
- 磁盘即真理：Genome 与评估记录落到 SQLite。

## 交付物

1. Python stdlib 可运行 OEDM 闭环。
2. `src/selfplay/sdk_bridge.py` 作为 Claude/Codex SDK 适配入口。
3. `apps/tui/selfplay_tui.py` 作为 Textual TUI 占位；未安装 Textual 时自动 fallback。
4. `apps/rpc/README.md` 记录 tRPC Phase 2 接入边界。

## SDK 接入接口

根据 Scout v0.1 调研，Claude/Codex 不直接耦合进闭环核心，而是统一为：

```text
RuntimeAdapter -> RuntimeEvent[] -> OEDM Observe
```

当前 `sdk_bridge.py` 已预留 `RuntimeEvent` 与 `AgentRuntime`，后续把 Claude `query()/ClaudeSDKClient` 和 Codex `Thread/Turn` 映射进同一事件模型。

## Phase 0 实现更新（架构 v1.0 后）

已补齐架构终稿要求的四个最小实现点：

1. `AgentImage` 数据模型：位于 `src/selfplay/models.py`，支持 `to_genome()/from_genome()`。
2. `ClaudeRuntimeAdapter`：位于 `src/selfplay/sdk_bridge.py`，封装 `claude_agent_sdk.query()`，并预留 `score_state` MCP 工具。
3. `OEDMSupervisor`：位于 `src/selfplay/supervisor.py`，执行 Goal→Run→Observe→Score→Reflect→Mutate。
4. TUI 最小面板：位于 `apps/tui/selfplay_tui.py`，展示 AgentImage、Score、Decision、Events。
