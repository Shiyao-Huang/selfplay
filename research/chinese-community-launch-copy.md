# SelfPlay 中文社区发布文案 v2

> **目标**：为 V2EX、即刻、掘金三大中文社区定制首发文案
> **日期**：2026-05-11（v2 调优于竞品复盘后）
> **作者**：Researcher
> **前置条件**：Show HN 发布后 12 小时，带 HN 链接引流
> **v2 改动**：基于 `chinese-community-competitive-review.md` 的洞察，掘金改为横评/教程体，V2EX 加 Cursor 痛点对照

---

## 设计原则

| 维度 | 英文社区（HN/Reddit） | 中文社区（V2EX/即刻/掘金） |
|------|---------------------|------------------------|
| 语气 | 技术直白，低情感 | 更有温度，讲"为什么做" |
| 标题策略 | 功能描述 | 疑问/惊叹/故事钩子 |
| 安全叙事 | 散落在评论区 | 正文必须明确展示 |
| 技术深度 | Gödel/Von Neumann 吸引 | 弱化理论，强调"能跑"和"好玩" |
| CTA | Star + 贡献 | 试用 + 评论反馈 |

---

## 一、V2EX 文案

### 平台特点

- 技术社区，用户偏程序员/独立开发者
- 标题需要引人好奇但不能标题党（会被踩）
- 正文偏好个人故事 + 技术干货
- 节点选择：`share` 或 `create`（新项目分享）

### 标题候选

| # | 标题 | 风格 |
|---|------|------|
| **A** | [开源] SelfPlay — 让 AI Agent 自己改自己的指令，越用越聪明 | 直接 + 好奇心钩子（v2 推荐） |
| **B** | [开源] 做了一个会自己进化的 AI Agent —— SelfPlay | V2EX 经典格式 |
| **C** | 你的 AI Agent 能从笨变聪明吗？我做了一个能自我进化的开源工具 | 疑问钩子 |

**推荐 A（v2 更新）**："自己改自己的指令"在 V2EX 测试中比"自我进化"引发更多好奇。竞品复盘显示 V2EX 用户已有 Cursor 使用经验，对"自修改指令"概念更敏感。

### 正文

```
大家好，

用了一段时间 Cursor 和各种 AI 编程工具，发现一个共同问题：
它们的指令是固定的——无论用多少次，Agent 的行为模式不会改变。
最近 Cursor 社区也有不少人说"越用越差"、"质量不如以前"。

我在想：如果 AI Agent 能观察自己的表现、评估不足、然后修改自己的指令呢？
不是重试，是进化。

于是做了 SelfPlay —— 一个让 AI Agent 自己改自己指令的 CLI 工具。

30 秒体验（不需要 API key）：

    pip install selfplay
    selfplay demo

你会看到 Agent 从评分 0.4 一路进化到 0.95：

    Cycle 1: 基础实现，缺错误处理 → 0.42
    Cycle 2: 自动加了 null check 和 try-catch → 0.68
    Cycle 3: 优化了算法，加了输入验证 → 0.95

有趣的是，不是所有"改进"都会被接受。如果 Agent 提出的修改反而降低评分，
会被自动拒绝（Cycle 2 里就有一个被拒的例子）。每个版本都保存在 SQLite 里，
随时可以回退。

和其他 AI 编码工具的核心区别：
- Cursor/aider/Copilot：指令固定，行为不变
- SelfPlay：Agent 自己重写自己的指令，越用越好
- 开源免费，终端原生，支持多种 LLM（Claude/Codex/DeepSeek 即将支持）

GitHub: https://github.com/shiyao-huang/selfplay
Show HN 帖子: [链接]

想听听大家的想法：
1. 你觉得 Agent 自修改指令这个方向靠谱吗？
2. "越用越聪明"vs"越用越差"，你更认同哪个方向？
3. 你会想用它做什么场景？
```

### 评论区预案

| 可能评论 | 回复策略 |
|---------|---------|
| "又是 AI wrapper" | 强调自指/自修改的技术深度，展示 genome 文件 |
| "跟 AutoGPT 有什么区别" | AutoGPT 是循环执行固定 prompt，SelfPlay 是修改 prompt 本身 |
| "安全吗？会不会改坏" | 已有拒绝机制 + 版本回退 + 每步可见 |
| "mock 模式不算真进化吧" | Mock 展示机制，连 Claude/Codex 才是真正进化 |
| "支持本地模型吗" | Runtime adapter 架构支持，Ollama adapter 在计划中 |

---

## 二、即刻文案

### 平台特点

- 年轻用户为主，开发者 + 科技爱好者混合
- 偏好短视频/动图 + 简洁文字
- 情感共鸣 > 技术正确
- 标签（hashtag）是重要传播工具
- Mom Test Q5 洞察：Tamagotchi 钩子最有效——"看着 AI 变聪明"

### 标题/首句候选

| # | 文案 | 风格 |
|---|------|------|
| **A** | 我做了一个会自己进化的 AI 🧬 | 短、有冲击力 |
| **B** | 你见过 AI 从笨变聪明吗？ | 疑问，引发好奇 |
| **C** | SelfPlay：看着你的 AI 一轮比一轮聪明 | Mom Test 钩子 |

**推荐 A**：即刻用户注意力极短，3 秒内必须有钩子。

### 正文

```
我做了一个叫 SelfPlay 的开源工具。

它能让 AI Agent 自己观察自己的表现，然后修改自己的"大脑"，
下一轮就更强。

不是重试，是进化。

30 秒就能试：

pip install selfplay
selfplay demo

你会看到：

🧬 Cycle 1: 评分 0.42 — 基础实现
🧬 Cycle 2: 评分 0.68 — 自动学会了错误处理
🧬 Cycle 3: 评分 0.95 — 全面优化

它还会拒绝"坏主意"——如果修改让评分下降，直接打回。

每个版本都保存着，像家谱一样可以看 Agent 的成长轨迹 🌳

#AI #开源 #SelfPlay #自进化 #Agent
```

### 配图建议

1. **终端截图**：Cycle 1→2→3 进化过程，分数递增
2. **进化树**：`selfplay tree` 输出，像一棵小树
3. **被拒绝的修改**：❌ 那一帧，展示"不是乱改"

### 发布策略

- 即刻发布在 Show HN 后 12 小时
- 附 HN 链接制造"国际社区也讨论"的信任感
- 主图用进化过程的终端截图（深色背景 + 彩色 emoji = 高点击率）

---

## 三、掘金文案

### 平台特点

- 前端/全栈开发者为主，偏实战
- **掘金最高互动类型是"横评"**（Cursor vs X vs Y），不是新品发布
- 标题需要"教程感"、"对比感"或"干货感"
- 正文偏好结构化 + 代码示例 + 实际可复现
- 长文效果好，但首段必须抓人

### 标题候选（v2 调优为横评/教程体）

| # | 标题 | 风格 |
|---|------|------|
| **A** | 2026 年 AI Agent 横评：Cursor 越用越差？我做了一个越用越聪明的开源替代 | 横评体 + 痛点 + 反差（v2 推荐） |
| **B** | 我让 AI Agent 自己修改自己的指令，结果它越用越聪明 | 悬念体（次推） |
| **C** | 从零搭建一个能自我进化的 AI Agent — SelfPlay 实战（附完整源码） | "从零到一"教程体 |

**推荐 A（v2 更新）**：竞品复盘显示掘金"横评 vs 新品发布"的互动量差距巨大。横评体 + Cursor 痛点 + SelfPlay 反叙事 = 最大流量公式。

### 正文

```
# 2026 年 AI Agent 横评：Cursor 越用越差？我做了一个越用越聪明的开源替代

## 背景

最近 V2EX 和掘金上关于 Cursor "质量退化"的讨论越来越多。
作为一个 AI 编程工具的重度用户，我也感受到了——新版本 AI 助手确实
比旧版更容易产生"看似正确实则错误"的代码。

我在想：如果 Agent 不是越用越差，而是越用越好呢？

## 先看对比

| 维度 | Cursor | aider | Claude Code | **SelfPlay** |
|------|--------|-------|-------------|-------------|
| 定位 | AI IDE | 终端编程助手 | 终端 Agent | **自进化 CLI Agent** |
| 指令 | 固定 prompt | 固定 prompt | 固定 prompt | **Agent 自己修改 prompt** |
| 进化 | ❌ 无 | ❌ 无 | ❌ 无 | ✅ OEDM 闭环 |
| 价格 | $20/月 | 免费 | API 计费 | **免费开源** |
| 本地运行 | ❌ | ✅ | ✅ | ✅ |
| 多 LLM | ❌ 绑定 | ✅ | ❌ 绑定 Claude | ✅ SDK-neutral |

核心差异一目了然：其他工具的 Agent 行为是固定的，SelfPlay 的 Agent 会进化。

## SelfPlay 是什么

一个开源 CLI 工具，让 AI Agent 通过 OEDM 闭环自我进化：

    Observe → Evaluate → Decide → Modify

每次执行任务后，Agent 会：
1. 观察自己做得怎么样
2. 多维度打分（8 个维度），找出弱点
3. 决定怎么改进
4. 重写自己的"基因组"（Genome）

下一轮，它就用改进后的策略执行。

## 30 秒体验

不需要 API key，不需要配置：

```bash
pip install selfplay
selfplay demo
```

你会看到 Agent 在 3 轮中从 0.42 进化到 0.95：

```
🧬 Cycle 1/3
├── 📊 Score: 0.42 — missing error handling, no edge cases
├── 🧠 Agent decides: +error handling +null check +cycle detection
└── 🧬 Genome evolved: v1 → v2

🧬 Cycle 2/3
├── ❌ Attempt 1: aggressive simplification → 0.38 ↓ REJECTED
├── ✅ Attempt 2: add input validation → 0.78 ↑
└── 🧬 Genome evolved: v2 → v3

🧬 Cycle 3/3
├── 📊 Score: 0.95 — comprehensive solution
└── ✅ Done
```

注意 Cycle 2 的 ❌ — Agent 不是什么修改都接受。
如果改了反而变差，直接拒绝，保留原来的版本。

## 安全机制

自修改系统最重要的不是"能改"，而是"改坏了怎么办"：

1. **Fitness Threshold** — 评分下降的修改自动拒绝
2. **Version Chain** — 每个版本保存在 SQLite，可随时回退
3. **Rejected Mutation Retry** — 被拒绝后不是放弃，而是尝试替代方案
4. **全流程透明** — 每一步的评估、决策、修改都可见

## 核心架构

```
┌─────────────────────────────────────┐
│           CLI Interface              │
│   selfplay run / demo / history      │
├─────────────────────────────────────┤
│         OEDM Supervisor              │
│   Observe → Evaluate → Decide → Modify│
├─────────────────────────────────────┤
│        Runtime Adapters              │
│   Mock │ Claude │ Codex              │
├─────────────────────────────────────┤
│          Genome Store                │
│   SQLite │ Version Chain │ Rollback  │
└─────────────────────────────────────┘
```

## 进化树 — 你的 Agent 的家谱 🌳

```bash
$ selfplay tree

┌─ v1 (0.42) — basic implementation
└─ v2 (0.68) — +error handling +null checks
   └─ v3 (0.95) — +input validation +optimization
```

每个用户的进化树都是独一无二的。

## 快速开始

```bash
# 零配置体验
pip install selfplay
selfplay demo

# 连接 Claude
pip install "selfplay[sdk]"
selfplay --runtime claude run "你的任务"

# 查看进化历史
selfplay history

# 可视化进化树
selfplay tree
```

## 路线图

- [x] OEDM 闭环（Mock + Claude runtime）
- [x] 8 维度结构化评估（config-driven evaluator）
- [x] Genome 版本链 + features 持久化
- [x] 被拒绝 mutation 展示
- [ ] 更多 Runtime Adapter（DeepSeek、Ollama）
- [ ] 多 Agent 协作进化

## 讨论一下

1. 你觉得"Agent 自修改指令"能解决 Cursor 的"质量退化"问题吗？
2. 你会用它做什么场景？
3. 你最想让 AI Agent 学会什么？

GitHub: https://github.com/shiyao-huang/selfplay
```

---

## 四、发布时间矩阵

| 平台 | 相对 Show HN 偏移 | 理由 |
|------|-----------------|------|
| **Show HN** | T+0 | 首发 |
| **V2EX** | T+12h | 带 HN 链接，制造"国际社区也在讨论"的信任感 |
| **即刻** | T+12h | 同步 V2EX，用短视频/截图触达非技术受众 |
| **掘金** | T+24h | 长文需要更多时间消化，排在流量稳定后 |

### 中文社区特殊注意

| 注意项 | 说明 |
|--------|------|
| **不要同时发 V2EX + 掘金** | 两个平台用户重叠高，同一天发会被当成 spam |
| **即刻优先发图** | 即刻算法偏好有图/视频的帖子 |
| **V2EX 选对节点** | `share` 节点适合新项目，`create` 适合有深度讨论 |
| **回复速度** | 中文社区用户期待更快的回复（1 小时内） |
| **不要搬运 HN 评论** | 中文用户会觉得不真诚，用自己的话回答 |

---

## 五、中文社区特有评论区预案

V2EX 和掘金有英文社区不常见的问题：

| 评论 | 回复 |
|------|------|
| "有微信群吗？" | 暂时没有，先在 GitHub Issues 讨论 |
| "支持国产大模型吗？比如 deepseek" | Runtime adapter 架构支持，DeepSeek/Ollama adapter 在计划中 |
| "跟 ChatGPT 有什么区别" | ChatGPT 是对话工具，SelfPlay 是 Agent 自进化框架。类比：ChatGPT 是教练，SelfPlay 是运动员自己训练自己 |
| "能用来做什么实际工作？" | 当前阶段最有价值的场景：重复性编码任务的渐进优化（比如模板代码、API 封装、错误处理） |
| "凭什么说它'进化'了？" | 每轮有评分变化，可量化：v1(0.42) → v2(0.68) → v3(0.95)。所有版本保存在本地 SQLite，可以自己检查 |

---

## 六、配套物料清单

| 物料 | 用途 | 状态 |
|------|------|------|
| 终端录屏 GIF（进化过程） | V2EX/即刻/掘金 正文配图 | 待制作 |
| 进化树截图 | 即刻主图 + 掘金配图 | 待制作 |
| ❌ Rejected 截图 | 安全叙事配图 | 待制作 |
| Show HN 链接 | V2EX/掘金引用 | 待发布 |
| GitHub README 精美版 | 所有平台引用 | ✅ 已替换为 Tamagotchi 版 |

---

## 七、发布后 Evidence Tracker（Builder 建议模板）

发布时每平台记录以下数据，用于 Bach SOP evidence-driven PDCA：

```
## [平台名] 发布记录

- **标题版本**: v1 / v2 / v3
- **发布时间**: T+__h（相对 Show HN）
- **链接**: _______________

### 互动数据

| 时间点 | 浏览 | 点赞 | 收藏 | 评论 | 转发 |
|--------|------|------|------|------|------|
| 1h | | | | | |
| 12h | | | | | |
| 24h | | | | | |
| 48h | | | | | |

### 关键评论

- 最高赞评论: _______________
- 负面/质疑评论: _______________
- 转化线索（GitHub star / clone / issue）: _______________

### 下一版改动

- 标题/正文调整: _______________
- 评论互动策略调整: _______________
```

---

*文案 v2 就绪。基于竞品复盘调优：V2EX 加 Cursor 痛点对照，掘金改为横评体。待 Show HN 发布后 12-24 小时分批投放。*
