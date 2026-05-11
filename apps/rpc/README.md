# tRPC 通讯层占位

Phase 0-1 采用 Python 进程内调用，不启动网络层。

Phase 2 再引入 TypeScript tRPC Server：

- `agentRouter.registerTask`
- `oedmRouter.runCycle`
- `genomeRouter.latest`
- `events.onExecutionStream`

Python 侧先通过 HTTP 直调 tRPC endpoint，Web 侧使用原生 tRPC client。
