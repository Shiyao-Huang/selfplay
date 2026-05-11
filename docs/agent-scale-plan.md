# Agent Scale Plan

目标不是立刻增加 agent 数量，而是在低资源机器上提高吞吐并避免崩溃。

## 当前判断

- 不应继续 spawn：主机长期只有约 1% free memory。
- Supervisor auto-spawn 已产生重复实例，先要止血。
- Docker build 需要拉镜像和装依赖，当前环境不安全。
- Builder context 已到 critical，适合交接，不适合长任务。

## Scale 策略

1. **Queue first**：先把任务拆成队列，只保持 1 个 active implementer。
2. **Standby roles**：Researcher/SA/Org/Supervisor 默认 standby，按需唤醒。
3. **Remote heavy ops**：Docker build、真实 SDK run、发布 CI 放到远端或干净机器。
4. **Spawn gate**：只有 free memory > 4GB、无重复 Supervisor、无阻塞 build 时再加 agent。
5. **Reuse artifacts**：优先复用 README、CLI、Docker 文件，不重复探索。

## 下一步

释放资源后先跑 `docker compose up --build`，再决定是否扩容到 1 Master + 1 Builder + 1 Reviewer。
