# README 定位反转草稿

> **目标**：基于 Mom Test 访谈发现（Q5: Tamagotchi 钩子），重写 README 首屏
> **原则**：先视觉体验 → 情感钩子 → 技术深度
> **日期**：2026-05-11
> **作者**：Researcher
> **状态**：草稿，待 Master/用户审批后替换 README.md

---

## 设计哲学

**旧 README 结构**：标题 → "它是什么"（技术描述）→ OEDM 图 → demo → 理论
**新 README 结构**：标题 → **30 秒震撼体验** → **看着 AI 变聪明** → 为什么不同 → demo 细节 → 理论（可选深入）

**核心改变**：
1. 第一屏就是可运行的 demo 命令 + 进化过程截图
2. "看着 AI 变聪明" 替代 "自我进化的 AI Agent"
3. 理论移到底部作为"想了解更多？"，不是前置条件

---

## 新 README 草稿

```markdown
<p align="center">
  <strong>SelfPlay 🧬</strong>
</p>

<p align="center">
  <strong>Watch your AI get smarter. Every time you use it.</strong>
</p>

<p align="center">
  <em>看着你的 AI 一轮比一轮聪明。</em>
</p>

<p align="center">
  <a href="#30秒体验">30秒体验</a> · <a href="#怎么做到的">怎么做到的</a> · <a href="#安装">安装</a> · <a href="#架构">架构</a>
</p>

---

## 30秒体验

```bash
pip install selfplay
selfplay demo
```

你会看到你的 AI Agent **从笨变聪明**：

```
🧬 SelfPlay — Cycle 1/3
├── 📝 Task: "Write a function to reverse a linked list"
├── 📊 Score: 0.42 — missing error handling, no edge cases
├── 🧠 Agent decides: +error handling +null check +cycle detection
└── 🧬 Genome evolved: v1 → v2

🧬 SelfPlay — Cycle 2/3
├── ❌ Attempt 1: aggressive simplification → score 0.38 ↓ REJECTED
├── ✅ Attempt 2: add input validation → score 0.78 ↑
└── 🧬 Genome evolved: v2 → v3

🧬 SelfPlay — Cycle 3/3
├── 📊 Score: 0.95 — comprehensive solution
├── 🎯 Threshold reached — no further improvement needed
└── ✅ Done

📈 Evolution: v1(0.42) → v2(0.68) → v3(0.95) — improved +126%
```

**不需要 API key。不需要配置。30 秒完成。**

> 每次你运行 SelfPlay，你的 Agent 都会观察自己的表现，决定如何改进，
> 然后修改自己的指令——自动地。它不是在重试，它在进化。

---

## 怎么做到的

你的 Agent 有一个 **Genome**——一份描述"我是谁、我怎么做事情"的自我画像。

每次执行任务后，Agent 会：

1. **Observe** — 观察自己做得怎么样
2. **Evaluate** — 打分，找出弱点
3. **Decide** — 决定怎么改进
4. **Modify** — 重写自己的 Genome

```
  Observe → Evaluate → Decide → Modify → (repeat)
       ▲                              │
       └──────── next run ◄───────────┘
```

修改不好的？会被拒绝（看 Cycle 2 的 ❌）。
修改好的？保留，下一轮更强。

**核心差异：** 其他 AI 工具的指令是固定的。SelfPlay 的 Agent 会**重写自己的指令**。

---

## 安装

### 零配置体验（推荐第一次使用）

```bash
pip install selfplay
selfplay demo
```

### 连接真实 AI（Claude / OpenAI）

```bash
pip install "selfplay[sdk]"
selfplay --runtime claude run "你的任务"
```

### Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## CLI 命令

```bash
selfplay demo                    # 30秒体验自进化
selfplay run "你的任务"           # 执行任务（3轮进化）
selfplay run --cycles 5 "任务"   # 5轮进化
selfplay history                 # 查看进化历史
selfplay tree                    # 可视化进化树 🌳
selfplay init                    # 创建配置文件
selfplay --runtime claude run    # 使用 Claude 作为运行时
```

---

## 进化树 — 你的 Agent 的家谱 🌳

```bash
$ selfplay tree

┌─ v1 (0.42) — basic implementation
└─ v2 (0.68) — +error handling +null checks
   └─ v3 (0.95) — +input validation +optimization
```

每个用户的进化树都是独一无二的。
**截图分享你的 Agent 是怎么变聪明的。**

---

## 架构

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

---

## 想了解更多？

<details>
<summary><strong>📖 理论背景（点击展开）</strong></summary>

SelfPlay 的理论基础来自自指系统的数学传统：

- **Gödel 不完备定理** (1931) — Agent 的 Genome 是它的"Gödel 编码"
- **Hofstadter Strange Loop** (1979) — Task/Meta/Arch 三层的纠缠层级
- **Von Neumann 自复制自动机** (1966) — 构造器 + 蓝图 + 控制器的工程映射
- **控制论反馈回路** (Wiener 1948) — OEDM 四阶段最小闭环

详细理论报告见 `research/` 目录。

</details>

<details>
<summary><strong>🔬 项目结构（点击展开）</strong></summary>

```
selfplay/
├── src/selfplay/
│   ├── models.py        # AgentImage + Genome 数据模型
│   ├── supervisor.py    # OEDM Supervisor 主循环
│   ├── evaluator.py     # 结构化 Evaluator
│   ├── mutator.py       # 基于 EvalResult 的 Mutator
│   ├── config.py        # selfplay.yaml 配置
│   ├── sdk_bridge.py    # SDK-neutral Runtime Adapters
│   ├── cli.py           # CLI 入口
│   └── storage.py       # SQLite 持久化
├── docs/
├── research/            # 理论调研报告
└── pyproject.toml
```

</details>

---

## 开发

```bash
pip install -e ".[tui,sdk,dev]"
PYTHONPATH=src python -m selfplay.cli run "验证最小闭环"
```

## 参与贡献

欢迎！特别需要：
- 新的 Runtime Adapter（OpenAI、Gemini、本地模型）
- 评估策略改进
- 多语言文档

## License

MIT

---

<p align="center">
  <sub>Built with ❤️ and self-reference</sub>
</p>
```

---

## 新旧对比

| 维度 | 旧 README | 新 README |
|------|----------|----------|
| **第一屏** | "它是什么"（技术描述） | `pip install selfplay && selfplay demo`（可运行体验） |
| **情感钩子** | "自己改进自己的开源框架" | "Watch your AI get smarter" |
| **理论位置** | 正文中间（OEDM 图 → 理论背景） | 底部折叠（"想了解更多？"） |
| **Demo 位置** | 第 3 节 | 第 1 节 |
| **被拒绝的修改** | 无展示 | Cycle 2 ❌ Rejected（安全叙事） |
| **进化树** | 无独立展示 | 独立小节 + "截图分享"CTA |
| **Tamagotchi 元素** | 无 | "你的 Agent 的家谱 🌳" + "独一无二" |
| **CTA** | 无明确行动号召 | "截图分享你的 Agent 是怎么变聪明的" |
| **中文体验** | 双语标题 | 双语标题，英文主体 |

---

## 关键决策说明

| 决策 | 原因（Mom Test Q5 洞察） |
|------|------------------------|
| demo 放第一屏 | 用户先"看到"Agent 变聪明，才想知道"怎么做到的" |
| 标题用 "Watch your AI get smarter" | 情感共鸣 > 技术正确（Twitter 传播靠情感） |
| 理论放折叠 | HN 读者会点开，普通用户不被吓跑 |
| 进化树独立展示 + CTA | 进化树截图 = 天然可分享内容（独特增长飞轮） |
| 被拒绝的修改展示 | 回应用户安全担忧（Mom Test 用户反馈 #1） |
| 英文主体 | HN/Reddit 首发是英文社区 |

---

*草稿完成。待 Master/用户审批后替换 README.md。*
