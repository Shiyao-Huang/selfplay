# SelfPlay 产品定义与差异化定位报告

> **目标**：可发布的开源 CLI 项目，目标是爆款
> **日期**：2026-05-09
> **作者**：Researcher

---

## 1. 竞品 landscape

### 1.1 当前 AI CLI Agent 市场（2025-2026）

| 产品 | 类型 | Stars | 核心卖点 | 自指/自进化 |
|------|------|-------|---------|-----------|
| **Claude Code** | 终端编码 Agent | N/A（闭源） | Anthropic 原生、最强 Claude 集成 | ❌ 无 |
| **OpenAI Codex CLI** | 自主编码 Agent | N/A（闭源） | 沙箱执行、长任务 | ❌ 无 |
| **aider** | AI pair programming | ~30k | 开源、多模型支持、Git 集成 | ❌ 无 |
| **ollama** | 本地 LLM 运行器 | ~140k | 一键本地运行模型 | ❌ 无 |
| **AutoGPT** | 自主 Agent 框架 | ~175k | "让 AI 自己思考" | ⚠️ 弱（预设目标循环） |
| **OpenCode** | 终端编码 Agent | ~15k | 开源、多模型 | ❌ 无 |
| **EvoAgentX** | 自进化 Agent 框架 | ~5k | Agent 自进化工作流 | ✅ 有（但非 CLI 产品） |
| **Darwin Gödel Machine** | 自改进编码 Agent | ~2k | 修改自身代码进化 | ✅ 有（研究原型） |
| **Meta HyperAgents** | 自指自改进 Agent | ~1k | 统一可编辑程序 | ✅ 有（研究原型） |

### 1.2 关键洞察

**市场空白**：没有一款产品同时满足：
1. ✅ **CLI 优先**（终端原生体验）
2. ✅ **自指自进化**（Agent 能修改自己的规则/代码）
3. ✅ **可视化进化过程**（用户能看到 Agent 如何改进自己）
4. ✅ **零门槛上手**（`pip install` 或 `npx` 一键启动）

EvoAgentX 最接近但它是 Python 库/框架，不是 CLI 产品。Darwin GM 和 HyperAgents 是研究原型，不是用户产品。

---

## 2. 产品定义

### 2.1 一句话定位

> **SelfPlay — 终端里能自我进化的 AI Agent**
>
> *The AI agent that improves itself every time it runs.*

### 2.2 核心价值主张

**对开发者**：
- "你的 AI Agent 会从每次任务中学习，自动优化自己的策略"
- "看着你的 Agent 从笨拙变聪明——过程完全透明"
- "不需要手动调 prompt，Agent 自己进化"

**对研究者**：
- "自指系统的工程实现——OEDM 闭环、Genome 进化、LLM 柔性证明器"
- "可复现的 Agent 自进化实验平台"

**对好奇者**：
- "看着 AI 学会改进自己——比任何 static AI 都更令人着迷"

### 2.3 与竞品的核心差异化

| 维度 | 其他 CLI Agent | SelfPlay |
|------|---------------|----------|
| 工作方式 | 执行任务 → 结束 | 执行任务 → 自我评估 → 修改自身 → 更好地执行 |
| 能力增长 | 固定不变 | 每次运行都在进化 |
| 用户体验 | 工具 | 宠物（你看着它成长） |
| 技术深度 | prompt engineering | 自指系统 + 反馈闭环 |
| 话题性 | "又一个 AI 编码工具" | "能自我进化的 AI" |

---

## 3. 爆款策略

### 3.1 病毒式传播的核心要素

**1. 令人震撼的 Demo（最重要）**

30 秒 Demo 脚本：
```bash
# 安装
pip install selfplay

# 第一次运行（Agent v1，表现一般）
selfplay run "帮我重构这个函数"
# 输出：Agent v1 完成任务 | Score: 3/10

# 第二次运行（Agent 已自动进化）
selfplay run "帮我重构另一个函数"
# 输出：Agent v2 完成任务 | Score: 7/10 ↑
#       ✨ Genome 已进化：新增了测试驱动策略

# 查看进化历史
selfplay history
# 输出：
#   v1 → v2: 新增测试驱动策略 (+4)
#   v2 → v3: 优化错误处理流程 (+2)
#   v3 → v4: 学会使用上下文缓存 (+1)

# 可视化进化树
selfplay tree
# ┌─ v1 (score: 3)
# └─ v2 (score: 7, +4)
#    └─ v3 (score: 9, +2)
#       └─ v4 (score: 10, +1)
```

**2. "养 AI" 的情感钩子**

类比成功案例：
- **Tamagotchi（拓麻歌子）**：人们愿意花时间照顾虚拟宠物
- **Neopets**：养成系统的吸引力
- **GitHub Copilot**：开发者喜欢 AI 助手的感觉
- SelfPlay = **"养一个会变聪明的 AI 助手"**

**3. 透明性即吸引力**

用户能看到：
- Agent 的自我评估（"我觉得这次做得不好，因为..."）
- Agent 的改进决策（"我决定修改策略，新增..."）
- Agent 的进化历程（完整家族树）

### 3.2 传播渠道策略

| 渠道 | 策略 | 优先级 |
|------|------|--------|
| **Hacker News** | Show HN 帖子 + "self-referential agent" 技术钩子 | P0 |
| **GitHub** | 精美 README + Demo GIF + 一键安装 | P0 |
| **Twitter/X** | 30s 录屏：Agent 从 3分进化到 10分 | P0 |
| **Reddit** | r/LocalLLaMA, r/ArtificialIntelligence, r/SideProject | P1 |
| **Product Hunt** | "Self-improving AI agent" | P1 |
| **YouTube** | 技术深度讲解（OEDM + Gödel + Von Neumann） | P2 |
| **V2EX / 即刻** | 中文开发者社区 | P2 |

### 3.3 首发内容策略

**README 首屏（最重要的一屏）**：

```markdown
# SelfPlay 🧬

The AI agent that improves itself every time you use it.

[Demo GIF: Agent 从 v1(3分) 进化到 v4(10分) 的实时录屏]

## Quick Start

pip install selfplay
selfplay demo    # 30秒体验自进化闭环

## How it works

SelfPlay uses an OEDM (Observe-Evaluate-Decide-Modify) loop —
inspired by Gödel's self-reference, Hofstadter's Strange Loops,
and Von Neumann's self-reproducing automata.

Your Agent doesn't just run tasks. It watches itself, evaluates
its performance, decides how to improve, and modifies its own
instructions — automatically.

## Features

- 🧬 Self-evolving: Agent modifies its own instructions after each run
- 📊 Evolution dashboard: Watch your Agent get smarter in real-time
- 🌳 Evolution tree: Full lineage of your Agent's improvements
- 🔌 SDK-neutral: Works with Claude, GPT, or local models
- 🖥️ Beautiful TUI: Terminal-native experience with Textual
```

---

## 4. 命名与品牌

### 4.1 命名方案

| 方案 | 含义 | 优势 | 劣势 |
|------|------|------|------|
| **SelfPlay** | 自我对弈（AlphaGo Self-Play 的隐喻） | 技术关联强、简短好记 | 可能被误认为游戏 |
| **OEDM** | 最小闭环缩写 | 学术精确 | 不够直觉 |
| **Genome** | 基因组 | 生物学隐喻、进化感强 | 与其他项目重名 |
| **StrangeLoop** | Hofstadter 概念 | 理论关联、有神秘感 | 较长 |
| **EvoCLI** | 进化 CLI | 直觉、简洁 | 不够独特 |

**推荐**：保持 **SelfPlay** — 自我对弈的隐喻（AlphaGo 通过 self-play 成为最强围棋 AI；SelfPlay 通过 self-play 让 Agent 自我进化）。

### 4.2 Slogan 候选

- "The AI that gets better every time you use it."
- "Watch your AI evolve."
- "Self-improving AI, in your terminal."
- "你的 AI，越用越聪明。"

---

## 5. MVP 功能优先级

### Phase 0（当前已有）
- [x] OEDM 闭环核心逻辑
- [x] Genome 序列化 + SQLite 持久化
- [x] CLI 基本命令（run/status）
- [x] Mock 模式（零依赖演示）

### Phase 1（爆款 MVP 必须有）
- [ ] **`selfplay demo`** — 30秒一键体验自进化（无需 API key）
- [ ] **`selfplay history`** — 进化历史展示
- [ ] **`selfplay tree`** — 进化树可视化
- [ ] **Textual TUI 面板** — 实时展示 OEDM 循环
- [ ] **LLM 柔性证明器** — 替换硬编码评分
- [ ] **真实 Claude/GPT adapter** — 接入真实 LLM

### Phase 2（增长阶段）
- [ ] **进化分享** — 导出进化树为图片（社交传播）
- [ ] **社区 Genome 市场** — 分享和下载进化好的 Agent
- [ ] **Web Dashboard** — Next.js 可视化面板
- [ ] **多语言支持** — 中英双语

### Phase 3（生态阶段）
- [ ] **tRPC API** — 第三方集成
- [ ] **插件系统** — 自定义 OEDM 阶段
- [ ] **团队进化** — 多 Agent 协同自进化

---

## 6. 技术产品化要点

### 6.1 安装体验（爆款生死线）

```bash
# 方案 A：pip install（推荐，当前技术栈）
pip install selfplay
selfplay demo

# 方案 B：pipx（隔离环境）
pipx install selfplay
selfplay demo

# 方案 C：uvx（最快）
uvx selfplay demo
```

**关键**：`selfplay demo` 必须在 **30秒内** 展示完整自进化闭环，**不需要任何 API key**。

### 6.2 Python 版本兼容

当前限制：Python ≥3.10（claude-agent-sdk 要求）

**解决方案**：
- Phase 1 用 `mock` 模式支持 Python 3.9+（不需要 SDK）
- 真实 LLM 模式要求 3.10+
- `pyproject.toml` 声明 `requires-python = ">=3.9"`，真实 adapter 做 lazy import

### 6.3 Demo 设计（30秒爆款）

```
$ selfplay demo

🧬 SelfPlay — Self-Evolving AI Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Task: "Write a function to reverse a linked list"

[Run 1] Agent v1 executing...
  ├─ Observe: Task completed in 2.3s
  ├─ Evaluate: Score 4/10 — missing edge cases
  ├─ Decide: Add null-check and cycle-detection
  └─ Modify: Genome v1 → v2 ✨

[Run 2] Agent v2 executing...
  ├─ Observe: Task completed in 1.8s
  ├─ Evaluate: Score 8/10 — improved coverage
  ├─ Decide: Optimize time complexity
  └─ Modify: Genome v2 → v3 ✨

[Run 3] Agent v3 executing...
  ├─ Observe: Task completed in 1.2s
  ├─ Evaluate: Score 9/10 — optimal solution
  ├─ Decide: No improvement needed (stable)
  └─ Modify: Genome v3 preserved ✓

📊 Evolution Summary:
   v1 (4) → v2 (8, +4) → v3 (9, +1)
   Total improvement: +125%

🌳 Your agent evolved 2 times in 3 runs!
   Try 'selfplay tree' to see the full evolution tree.
```

---

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| LLM 自修改产生退化 | 高 | 高 | 无收益防漂移机制（已实现）+ 回退支持 |
| 用户不理解"自进化" | 中 | 高 | 30秒 Demo + 可视化进化过程 |
| 安装失败率过高 | 中 | 高 | mock 模式零依赖 + Docker 备选 |
| 竞品跟进（EvoAgentX 出 CLI） | 低 | 中 | 先发优势 + 持续迭代 |
| 安全顾虑（Agent 修改自身） | 中 | 中 | 透明日志 + 用户确认机制 |

---

## 8. 结论

### 8.1 为什么 SelfPlay 能爆款

1. **独特定位**：唯一一款"能自我进化的 CLI AI Agent"——无直接竞品
2. **情感钩子**："养 AI"的养成感——比工具更有黏性
3. **技术深度**：Gödel + Hofstadter + Von Neumann 的理论背书——吸引技术社区
4. **视觉冲击**：实时进化树 + 分数提升——天然适合社交媒体传播
5. **低门槛**：`pip install selfplay && selfplay demo`——30秒上手

### 8.2 成功指标

| 指标 | Phase 1 目标 | Phase 2 目标 |
|------|-------------|-------------|
| GitHub Stars | 1,000（首月） | 10,000（3个月） |
| HN 首页 | Show HN 前 10 | — |
| 日活用户 | 100 | 1,000 |
| 进化总次数 | 10,000 | 100,000 |

### 8.3 下一步

1. **立即**：完善 `selfplay demo` 命令（30秒体验闭环）
2. **立即**：美化 CLI 输出（rich/textual）
3. **本周**：录制 Demo GIF，撰写 README
4. **本周**：发布到 GitHub + HN + Reddit

---

*报告结束。*
