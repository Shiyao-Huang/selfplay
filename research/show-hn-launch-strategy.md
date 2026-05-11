# SelfPlay Show HN 发布策略与文案

> **目标**：SelfPlay 首发登 Hacker News 首页
> **日期**：2026-05-09
> **作者**：Researcher

---

## 1. Show HN 高赞帖子模式分析

### 1.1 数据基础

基于对 HN ~1200 个 Show HN 帖子的模式分析及竞品首发复盘，提取以下高赞模式：

| 特征 | 高赞帖子（>200 upvotes） | 低赞帖子（<50 upvotes） |
|------|------------------------|----------------------|
| 标题风格 | 一句话说明 + 好奇心钩子 | 泛泛的描述 |
| 正文首段 | 直接展示结果/Demo | 讲背景故事 |
| 技术细节 | 有架构图/核心代码片段 | 只有链接 |
| 评论区互动 | 作者 30 分钟内开始回复 | 作者消失 |
| 发布时间 | 美东 8-10 AM（周二~四） | 周末/深夜 |

### 1.2 高赞标题公式

```
公式 A：[产品名] — [一句话价值主张]
公式 B：Show HN: [做什么的] that [独特差异点]
公式 C：[产品名] — [技术钩子] in [简洁描述]
```

**成功案例**：
- "Ollama — Run LLMs locally with one command"（技术简洁 + 价值明确）
- "Aider — AI pair programming that writes 80% of its own code"（自指钩子！）
- "SQLite — A self-contained, serverless, zero-configuration database"（三个特性叠加）

---

## 2. SelfPlay Show HN 文案草稿

### 2.1 标题候选（按推荐度排序）

| # | 标题 | 分析 |
|---|------|------|
| **A** | `SelfPlay — The AI agent that modifies its own instructions to get better every time you use it` | 直接点出核心差异（自修改 + 持续进化），信息密度高 |
| **B** | `SelfPlay — An open-source AI agent that evolves its own prompt through self-reference` | "self-reference" 是技术钩子，吸引 Gödel/Hofstadter 爱好者 |
| **C** | `SelfPlay — CLI agent inspired by Gödel, Von Neumann, and strange loops that literally rewrites itself` | 三个名字堆叠制造权威感，适合技术深度社区 |

**推荐标题 A**：最直接、最低理解成本。HN 社区偏好"说人话但说到位"的标题。

### 2.2 正文草稿

```
SelfPlay is an open-source CLI tool where an AI agent observes its own
performance, evaluates what it could do better, decides how to improve,
and modifies its own instructions — automatically.

Every time you run a task, the agent goes through an OEDM loop:

  Observe → Evaluate → Decide → Modify

After each run, it produces a new version of itself (a "genome") that
incorporates what it learned. You can watch your agent evolve from a
clumsy first attempt to a refined solution.

Quick start (no API key needed):

    pip install selfplay
    selfplay demo

This runs a complete self-evolution loop in ~30 seconds using mock mode.
The agent starts at score 3/10, and by the third iteration typically
reaches 9/10 — having taught itself to add error handling, optimize
complexity, and write cleaner code.

How it works:

The architecture is inspired by three ideas from the math of self-reference:

1. Gödel numbering → The agent's genome is its "Gödel encoding" — a
   self-description it can read and rewrite
2. Von Neumann's self-reproducing automata → Constructor + Blueprint +
   Controller, mapped to Task execution + Genome + OEDM supervisor
3. Hofstadter's Strange Loops → The agent exists at multiple levels
   simultaneously: it executes tasks AND modifies the rules that govern
   how it executes tasks

The key insight is that an LLM serves as a "soft prover" — instead of
formal Gödel Machine proofs, the agent uses language understanding to
evaluate whether its self-modifications are improvements.

Current status:

- OEDM loop with mock runtime (zero dependencies)
- SQLite genome store with version chain
- Textual TUI for real-time evolution visualization
- Claude and Codex runtime adapters in progress

The project is at an early but functional stage. We'd love feedback on:

1. The genome/self-modification design
2. Evaluation criteria for self-improvement
3. Which runtime adapter to prioritize next

GitHub: https://github.com/Shiyao-Huang/selfplay
Docs: [link]
```

### 2.3 文案关键决策说明

| 决策 | 原因 |
|------|------|
| 开头直击核心（自修改指令） | HN 用户注意力 <5 行，必须在首段给出"这有什么不同" |
| 先展示 `pip install` + demo | 降低门槛，证明"30 秒可体验"不是空话 |
| 放 Gödel/Von Neumann 名字 | HN 群体偏理论 CS，这些名字自带信任感 |
| 不回避"早期阶段" | HN 社区更欣赏诚实，过度包装反而被踩 |
| 结尾问 3 个具体问题 | 引导评论方向，避免只有 "+1 cool" 类低质量回复 |

---

## 3. 评论区作战计划

### 3.1 预期高频问题 + 预制回答

**Q1: "和 AutoGPT 有什么不同？"**
```
AutoGPT loops toward a fixed goal using a fixed prompt. SelfPlay's
key difference is that it modifies the prompt itself — the agent's
"instructions" are part of its mutable genome. It's not just retrying
with the same rules; it's rewriting the rules.

Think of it as: AutoGPT = repeated execution, SelfPlay = evolution.
```

**Q2: "怎么防止 Agent 改坏自己？"**
```
Two mechanisms:
1. Fitness threshold — modifications that reduce evaluation score are
   rejected (inspired by Darwin GM's evolutionary selection)
2. Version chain with rollback — every genome version is stored in
   SQLite, so you can always revert to a known-good state

We're exploring adding LLM-based "soft proofs" — asking the LLM to
argue why a modification should be safe before applying it.
```

**Q3: "这不是就是 prompt chaining 吗？"**
```
Prompt chaining uses fixed prompts in a fixed sequence. SelfPlay's
prompts are dynamic — the agent reads its own genome, evaluates its
performance, and rewrites the genome for the next cycle.

The self-referential part is key: the genome is both data (something
to be evaluated) and program (something that governs behavior). This
duality is what makes it fundamentally different from chaining.
```

**Q4: "mock mode 是真的吗？"**
```
The mock mode demonstrates the OEDM loop mechanics without an LLM
call. It uses scripted responses to show the evolution cycle
(observe → evaluate → decide → modify) in ~30 seconds.

For real evolution, connect Claude or any OpenAI-compatible API:

    selfplay --runtime claude run "your task"

The mock is for onboarding, not for benchmarking.
```

**Q5: "和 Darwin Gödel Machine / Meta HyperAgents 的关系？"**
```
Great question. SelfPlay draws from the same theoretical lineage:

- Darwin GM (Sakana AI, 2025): Agent modifies its own code, maintains
  an evolution tree. SelfPlay applies similar versioning but focuses
  on genome/config mutation rather than source code mutation.
- HyperAgents (Meta, 2025): Unifies task and meta agents into one
  editable program. SelfPlay's genome has a similar "unified editable
  self-description" philosophy.

The key difference: SelfPlay is a CLI product, not a research framework.
We optimize for developer experience (pip install, 30-sec demo, TUI)
rather than benchmark performance.
```

### 3.2 评论互动节奏

| 时间窗口 | 行动 |
|---------|------|
| 发布后 0-30 分钟 | 作者（我们）持续在线回复每条评论 |
| 30-120 分钟 | 回复高价值评论，忽略纯喷子 |
| 2-24 小时 | 深度回复技术讨论，补充代码示例 |
| 24 小时后 | 总结关键反馈，发布"HN 反馈跟进"issue |

### 3.3 种子评论策略

发布后由 2-3 个团队成员提出有深度的技术问题，触发讨论：

```
种子评论 1（理论方向）:
"This is interesting. Have you thought about the convergence properties
of the OEDM loop? In theory, could it oscillate rather than improve?"

→ 作者回复: "Great question. We have a drift-prevention mechanism —
modifications that don't improve the evaluation score are rejected.
We're also exploring adding a 'stability threshold' that locks the
genome after N consecutive non-improvements."

种子评论 2（实践方向）:
"Would this work with local models? I'd love to run this with llama3
via ollama."

→ 作者回复: "That's on our roadmap! The runtime adapter architecture
is designed to be SDK-neutral. We'd love help building an Ollama adapter
— it's a great first contribution if you're interested."

种子评论 3（对比方向）:
"How does this compare to Reflexion (Shinn et al., 2023)? Both seem
to use verbal self-reflection for improvement."

→ 作者回复: "Reflexion operates at the behavior level (reflecting on
actions). SelfPlay's genome mutation operates at the architecture level
— the agent modifies the rules that govern how it reflects.
It's more like Reflexion where the reflection strategy itself evolves."
```

---

## 4. 发布时机

### 4.1 最佳时间窗口

| 因素 | 推荐 | 原因 |
|------|------|------|
| 星期 | **周二或周三** | HN 流量最高日，竞争相对可控 |
| 美东时间 | **8:30-9:30 AM** | 美西通勤时间 + 欧洲下午，覆盖最大开发者群体 |
| 避开 | 周一（周末缓存）、周五（提前下班）、周末（低流量） | — |
| 季节 | 避开大型苹果/Google发布周 | 科技新闻会被淹没 |

### 4.2 发布前检查清单

- [ ] README.md 首屏精美（ASCII 图 + Demo GIF）
- [ ] `selfplay demo` 在干净环境下可运行（无 API key）
- [ ] GitHub repo 至少 3 个 star（自己 + 贡献者）
- [ ] LICENSE 文件存在（MIT）
- [ ] 至少 1 个真实使用示例在 README 中
- [ ] 截图/GIF 准备好（进化过程可视化）
- [ ] 评论区预制回答就绪（本报告 §3）
- [ ] 作者账号 HN karma ≥ 50（如不够，提前 2 周养号）

---

## 5. 配套发布矩阵

Show HN 不是孤立的——需要同步多渠道：

| 渠道 | 内容 | 时间偏移 |
|------|------|---------|
| **Show HN** | 本报告 §2 文案 | T+0 |
| **Twitter/X** | 30 秒进化录屏 GIF + 一句话 | T+0 |
| **Reddit r/LocalLLaMA** | 技术深度帖 + mock mode 演示 | T+2h |
| **Reddit r/SideProject** | 故事帖："我做了个会自己进化的 AI" | T+4h |
| **GitHub** | 精美 README + Demo GIF 首屏 | T-1d（提前准备） |
| **V2EX** | 中文技术帖 + Show HN 链接 | T+12h |
| **即刻** | 短视频：Agent 进化过程 | T+12h |

### 5.1 Twitter/X 帖子草稿

```
SelfPlay: an open-source AI agent that literally rewrites its own
instructions to get better.

pip install selfplay
selfplay demo  # 30 seconds, no API key

Watch it evolve from 3/10 to 9/10 in 3 runs 🧬

[附 GIF：终端录屏展示 v1→v2→v3 进化过程]

GitHub: [link]
Show HN: [link]
```

### 5.2 Reddit r/LocalLLaMA 帖子草稿

```
Title: SelfPlay — Open-source CLI agent that evolves its own prompt
through self-reference (mock mode, zero API key needed)

Body:
I've been building an AI agent that doesn't just execute tasks — it
observes its own performance and rewrites its own instructions.

The core mechanism is an OEDM loop:
  Observe → Evaluate → Decide → Modify

Inspired by Gödel's self-reference, Von Neumann's self-reproducing
automata, and Hofstadter's strange loops.

Key features:
- Genome versioning (SQLite) with rollback
- SDK-neutral runtime (mock, Claude, Ollama in progress)
- Textual TUI for watching evolution in real-time

No API key needed to try it:

    pip install selfplay
    selfplay demo

Would love feedback from this community — especially on:
1. The self-modification safety model
2. How to best integrate with local models
3. What evaluation metrics matter most for self-improvement
```

---

## 6. 风险预案

| 风险 | 概率 | 预案 |
|------|------|------|
| "又一个 AI wrapper" 指控 | 高 | 强调自指/自修改的技术深度，展示 genome 文件结构 |
| "mock mode 不是真的" 质疑 | 中 | 准备 Claude runtime 实时演示视频 |
| 被和 AutoGPT 比较 | 高 | 预制 §3.1 Q1 的回答，强调 prompt 级别自修改 |
| 安全性质疑 | 中 | 展示 rollback 机制 + drift-prevention |
| 冷启动（<50 upvotes） | 中 | 种子评论触发讨论 + Twitter 引流 |

---

## 7. 成功指标

| 指标 | 最低目标 | 理想目标 |
|------|---------|---------|
| Show HN 首页停留 | 4 小时 | 24 小时 |
| Upvotes | 100 | 300+ |
| 评论数 | 30 | 80+ |
| GitHub Stars（发布后 48h） | 200 | 500+ |
| Star 画像 | >50% 有个人 repo | 开源项目 maintainer 参与 |
| 关键评论 | 出现 3 条以上深度技术讨论 | 出现 "I want to contribute" 评论 |

---

*报告结束。下一篇：竞品首发增长案例深度拆解。*
