# AI 编码助手用户反馈挖掘报告

> **目标**：从竞品用户反馈中提取"用户真正在意什么"，指导 SelfPlay demo 展示重点
> **日期**：2026-05-10
> **作者**：Researcher

---

## 1. 研究方法

- Reddit（r/cursor, r/programming, r/AI_Agents, r/ClaudeAI, r/LocalLLaMA）
- Hacker News 讨论（HyperAgents, Zuckerman, Darwin GM 帖子）
- 开发者调查（Stack Overflow 2025, McKinsey AI 2025, PwC Agent Survey）
- 竞品 GitHub Issues/Discussions 反馈模式

---

## 2. 用户痛点 TOP 10（按频率排序）

| 排名 | 痛点 | 提及频率 | 来源 |
|------|------|---------|------|
| **#1** | **"差一点就对了"问题** — AI 输出 90% 正确，最后 10% 的修复比从头写更难 | 45% 开发者调查 | Reddit r/programming |
| **#2** | **质量退化** — 新版本 AI 助手比旧版更差，产生"看似正确实则错误"的代码 | 高频 | Reddit r/programming, r/cursor |
| **#3** | **错误处理无能** — AI 不能智能分析运行时异常，开发者需手动调试 AI 制造的问题 | 高频 | Reddit r/ClaudeAI |
| **#4** | **速度 vs 质量不可兼得** — 用 AI 感觉更快，但 PR 中错误明显增多 | 高频 | HN, Reddit |
| **#5** | **Agent 管理疲劳** — 2026 年开发者感觉在"同时管 8 个 AI agent" | 新兴 | Reddit r/singularity |
| **#6** | **复杂领域（iOS、嵌入式）完全不靠谱** | 中频 | Reddit r/iOSProgramming |
| **#7** | **上下文理解不足** — AI 只看当前文件，不理解整个代码库 | 中频 | 多源 |
| **#8** | **过度防御性编程** — AI 过度关注 edge case，核心功能反而跑不通 | 中频 | Reddit |
| **#9** | **指令遵循差** — AI 不按指令走，自由发挥导致混乱 | 中频 | Reddit r/cursor |
| **#10** | **多文件修改不一致** — 改了一个文件忘了改相关文件 | 中频 | Reddit |

---

## 3. 用户对"自改进 Agent"的态度

### 3.1 期待（What people want）

| 期待 | 比例/来源 |
|------|----------|
| **人类在环控制** — 不接受全自动自改进，需要 oversight | Reddit r/AI_Agents 首选 |
| **透明可审计** — 能看到 Agent 为什么/如何改进自己 | HN + Reddit 共识 |
| **可靠性 > 花哨** — 宁可稳定可靠也不要野心勃勃但不靠谱 | 跨平台共识 |
| **安全护栏** — 担心自修改代码产生意外行为或安全漏洞 | HN 技术讨论 |
| **具体场景有用** — 编码、调试等具体任务，不要泛泛的自主性 | 调查数据 |
| **自我纠错能力** — AI 能分析自己的错误、读 stack trace、自行修正 | 最 wanted feature |

### 3.2 担忧（What people fear）

| 担忧 | 来源 |
|------|------|
| **失控** — "AI 改自己的代码？太疯狂了" | Reddit r/AI_Agents |
| **安全** — 自修改代码可能引入漏洞（Vectra Moltbook 分析） | 安全社区 |
| **谄媚循环** — AI 过于讨好用户，自改进可能放大这个偏差（Stanford 研究） | 学术 |
| **黑盒** — "我不知道它怎么改的，我不敢用" | HN |

### 3.3 HN 对具体项目的反应

| 项目 | HN 反应 | 关键评论 |
|------|---------|---------|
| **HyperAgents (Meta)** | 积极，技术深度讨论多 | "self-referential 的工程实现终于有人做了" |
| **Zuckerman** | 强兴趣，"agent edits its own code" | "从最小开始，实时改进，这才是正确的方向" |
| **Darwin Gödel Machine** | 好奇+质疑并行 | "进化树很酷，但基准测试和真实任务差距大" |
| **Leaping (YC W25)** | 一般，语音 AI 不是 HN 核心群体 | — |

---

## 4. 关键洞察：SelfPlay Demo 应该展示什么

### 4.1 痛点→Demo 映射

| 用户痛点 | SelfPlay Demo 如何回应 |
|---------|---------------------|
| #1 "差一点就对了" | Demo 展示 Agent 第 1 轮 90% 正确，第 2 轮自动修复最后 10%（而不是人工修复） |
| #3 错误处理无能 | Demo 展示 Agent 自学添加 try-catch、参数校验、null check |
| #4 速度 vs 质量 | Demo 展示质量持续提升（分数上升），不是速度换质量 |
| #9 指令遵循差 | Demo 展示 Agent 学习遵循特定编码规范/风格 |
| 自改进担忧 | Demo 展示**每一步都可见**——用户看到 Agent 的评估、决策、修改过程 |

### 4.2 Demo "杀手级场景"候选

**场景 A：渐进式代码质量提升（推荐）**
```
v1: 基础实现，无错误处理 → score 4/10
v2: 自动添加边界检查和错误处理 → score 7/10
v3: 优化算法复杂度 → score 9/10
```
- 对应痛点 #1（90%→100%）
- 视觉冲击力：分数从 4 涨到 9
- 技术深度：展示真实代码改进，不是玩具

**场景 B：从错误中学习**
```
v1: 代码崩溃（模拟异常）→ score 2/10
v2: Agent 分析 stack trace，修复 bug → score 6/10
v3: 添加防御性编程，不再崩溃 → score 9/10
```
- 对应痛点 #3（错误处理）
- 情感冲击："它从崩溃中学到了"
- 但风险：模拟崩溃可能显得不够真实

**场景 C：适配编码规范**
```
v1: 用自己的风格写代码 → score 5/10
v2: 学习用户的命名/风格规范 → score 8/10
v3: 完全匹配用户偏好 → score 9/10
```
- 对应痛点 #9（指令遵循）
- 展示个性化能力
- 但不够"震撼"

**推荐：场景 A 为主 + 场景 B 的错误处理元素融入**

### 4.3 Demo 中的安全叙事

用户对自修改有顾虑。Demo 必须同时展示**安全性**：

```
[Run 2] Agent v2 evaluating proposed change...
  ├─ Proposal: Remove null checks to simplify code
  ├─ Evaluate: Score would DROP from 7 → 5
  └─ Decision: ❌ REJECTED (fitness threshold not met)

  ├─ Alternative: Add input validation instead
  ├─ Evaluate: Score would RISE from 7 → 8
  └─ Decision: ✅ ACCEPTED → Genome v2 → v3
```

这展示了三个安全机制：
1. **不是所有修改都接受** — 负面修改被拒绝
2. **评估过程透明** — 用户看到为什么拒绝/接受
3. **有回退能力** — 每个版本都保存

---

## 5. 自改进 Agent 市场情绪总结

```
用户态度光谱：

  怀疑 ←————————————————————→ 期待
   ↑                              ↑
   · "AI改自己代码太危险"          · "终于不用手动调 prompt 了"
   · "跟 AutoGPT 一样是噱头吧"     · "自指系统在工程上可行了？"
   · "又是 AI wrapper"             · "能看到 Agent 变聪明很酷"
   ↑                              ↑
  安全担忧                       效率期待
```

**SelfPlay 的定位策略**：从光谱右侧（期待）切入，同时主动回应左侧（安全担忧）。

具体做法：
1. Demo 首先展示**可见的改进过程**（满足期待）
2. 在改进过程中**穿插被拒绝的修改**（展示安全机制）
3. 文案中明确标注"human-in-the-loop"、"可回退"、"评估透明"

---

## 6. 对 Phase 1 实现的具体建议

基于用户反馈，Phase 1 demo 应优先实现：

| 优先级 | 功能 | 原因（用户反馈） |
|--------|------|----------------|
| **P0** | 多轮进化循环（3 轮） | 用户想看到**持续改进**，不是一次性修改 |
| **P0** | 分数可视化上升 | 对应"速度 vs 质量"痛点——展示质量确实在提升 |
| **P0** | 展示被拒绝的修改 | 回应安全担忧——"不是乱改" |
| **P1** | 错误处理自学 | 对应痛点 #3——最高频 feature request |
| **P1** | 修改过程透明展示 | 回应"黑盒"担忧 |
| **P2** | 编码规范适配 | 个性化能力，差异化 |

---

## 7. 参考来源

### 用户反馈
- [Reddit r/programming: "Developers remain willing but reluctant to use AI"](https://www.reddit.com/r/programming/comments/1mfhu30/developers_remain_willing_but_reluctant_to_use_ai/)
- [Reddit r/programming: "Newer AI Coding Assistants Are Failing in Insidious Ways"](https://www.reddit.com/r/programming/comments/1qdv6h0/newer_ai_coding_assistants_are_failing_in/)
- [Reddit r/cursor: "Frustrating Experience with Cursor"](https://www.reddit.com/r/cursor/comments/1jn9hkv/frustrating_experience_with_cursor_i_dont_want_to/)
- [Reddit r/AI_Agents: "Self-improving agents — hype or useful?"](https://www.reddit.com/r/AI_Agents/comments/1sy4obi/selfimproving_agents_hype_or_useful_what_would/)
- [HN: HyperAgents discussion](https://news.ycombinator.com/item?id=47505670)
- [HN: Zuckerman — minimalist personal AI agent that self-edits its own code](https://news.ycombinator.com/item?id=46846210)
- [HN: "I use Cursor daily — here's how I avoid the garbage parts"](https://news.ycombinator.com/item?id=43340662)

### 调查报告
- [McKinsey: The State of AI 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
- [PwC AI Agent Survey (May 2025)](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html)
- [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/ai)

---

*报告结束。核心结论：用户最在意的是"最后 10% 问题的自动修复"和"可见的安全机制"。Demo 设计应围绕这两个核心展示。*
