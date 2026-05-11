# CLI/TUI + Web 界面技术栈 & tRPC 通讯层调研报告

> **Solution Architect 调研** | 2026-05-09
> 任务来源：Master 分配的「CLI/TUI/Web 界面技术栈 + tRPC 通讯层调研」

---

## 一句话版本

推荐 **Python Textual（CLI TUI）+ tRPC（通讯层）+ Next.js（Web 界面）** 的技术组合，以 Python 进程内调用为主路径，tRPC 作为跨进程/跨语言的标准通讯接口。

---

## 1. CLI TUI 技术选型

### 1.1 候选方案

| 维度 | Textual (Python) | Ink (React/TS) | OpenTUI (TS/Zig) |
|------|-------------------|----------------|-------------------|
| **语言** | Python | TypeScript | TypeScript |
| **渲染引擎** | Rich + 终端原生 | Yoga (Flexbox) | Zig 优化后端 |
| **组件模型** | Widget（OOP） | React Component | React/Solid/Vue |
| **样式** | CSS-like | CSS-in-JS | CSS-like |
| **异步支持** | ✅ async-first | ✅ 基于 React | ✅ |
| **成熟度** | ⭐⭐⭐ 生产级 | ⭐⭐⭐ 生产级 | ⭐ 实验性 |
| **生态** | 丰富的 Widget 库 | npm 生态 + npm组件 | 极少 |
| **Claude Agent SDK 集成** | ✅ 同进程（Python） | ❌ 需要 IPC 桥接 | ❌ 需要 IPC 桥接 |
| **Claude Code 同栈** | ❌ | ✅ Claude Code 用 Ink | ❌ |
| **维护状态** | 活跃（2025 持续更新） | 活跃 | 实验性 |
| **学习曲线** | 低（Python OOP） | 中（需 React 知识） | 高 |

### 1.2 关键发现

**Ink 的优势：**
- Claude Code 自身用 Ink 构建，证明了 AI Agent TUI 的可行性
- TypeScript 原生，与 tRPC 无缝集成
- React 组件模型，复用 npm 生态

**Textual 的优势：**
- **与 Claude Agent SDK Python API 同进程**，零序列化开销
- async-first 架构，天然适配 `query()` async API
- CSS-like 样式系统，可快速构建复杂布局
- 无需 IPC/桥接，减少复杂度

**Textual 的风险：**
- 2025-05-07 Textualize 发布博客讨论"未来"，团队规模有限
- 但框架本身已成熟，短期维护无忧

### 1.3 选型结论：Textual（主） + Ink（备选）

**Phase 0-1 用 Textual**：
- 与 Claude Agent SDK Python `query()` API 在同一进程
- 最小闭环原型无需 IPC，直接调用
- 开发速度最快

**Phase 2+ 可考虑迁移至 Ink**：
- 当需要 Web 界面复用组件时
- 当 tRPC 的 TS 类型安全成为刚需时
- 当团队更倾向 TypeScript 技术栈时

### 1.4 Textual TUI 设计规格

```
┌──────────────────────────────────────────────────────────┐
│ SelfPlay OEDM Monitor                    Gen:12 Elo:342  │
├──────────────────────┬───────────────────────────────────┤
│ Task Layer           │ Meta Layer                        │
│ ┌──────────────────┐ │ ┌─────────────────────────────┐   │
│ │ Agent-A  ████░░  │ │ │ [Observe]  执行结果: 0.87   │   │
│ │ Agent-B  ██████  │ │ │ [Evaluate] 质量评分: 0.91   │   │
│ │ Agent-C  ██░░░░  │ │ │ [Decide]   修改 instructions │   │
│ └──────────────────┘ │ │ [Modify]   Genome v5→v6      │   │
│                      │ └─────────────────────────────┘   │
│ Arch Layer           │                                   │
│ ┌──────────────────┐ │ Evolution Log                     │
│ │ Arch-α  Elo:1250│ │ [12:34:01] OEDM cycle #47        │
│ │ Genome 热力图    │ │ [12:34:02] Agent-A 0.87→0.91 ↑  │
│ │ 工具集: 5/8     │ │ [12:34:03] Arch modified hooks  │
│ └──────────────────┘ │ [12:34:04] Saving genome v6...   │
├──────────────────────┴───────────────────────────────────┤
│ > command (status/evolve/inspect/rollback <ver>/quit)    │
└──────────────────────────────────────────────────────────┘
```

**Textual 组件映射：**

| TUI 区域 | Textual Widget | 数据源 |
|---------|---------------|--------|
| 状态栏 | Header | Gen/Elo 全局状态 |
| Task Layer 面板 | DataTable | Agent 状态 + Elo |
| Meta Layer 面板 | Static + Rich | OEDM 四阶段状态 |
| Arch Layer 面板 | DataTable | Genome 维度热力图 |
| Evolution Log | RichLog | 实时事件流 |
| 命令栏 | Input | 用户交互入口 |

---

## 2. tRPC 通讯层分析

### 2.1 tRPC 核心特性

- **TypeScript-native**：端到端类型安全，Router 定义即 API 契约
- **HTTP 底层**：所有调用本质是 HTTP 请求，任何语言可通过 HTTP 调用
- **零代码生成**：不需要 Protobuf/OpenAPI 中间文件（但可生成）
- **Subscription 支持**：基于 WebSocket 的实时推送

### 2.2 Python 集成方案

**问题**：tRPC 官方仅支持 TypeScript 客户端。Python Agent 如何调用 tRPC？

**方案 A — HTTP 直接调用（推荐 MVP）：**

```python
import httpx

async def trpc_call(procedure: str, input_data: dict):
    """直接通过 HTTP 调用 tRPC Server"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:3000/trpc/{procedure}",
            json=input_data,
            params={"batch": "1"},
        )
        return response.json()
```

- 优点：零依赖、简单直接
- 缺点：丢失类型安全（仅 TS 侧有类型检查）

**方案 B — tRPC OpenAPI 生成 + Python 客户端：**

```
tRPC Router → OpenAPI Schema → openapi-generator → Python Client
```

- tRPC v11 支持 OpenAPI 导出（alpha）
- 生成强类型 Python 客户端
- 复杂度较高，适合 Phase 2+

**方案 C — FastAPI + tRPC 双协议：**

```
Python (FastAPI) ←→ tRPC Gateway ←→ TypeScript (tRPC Server)
```

- Python 侧用 FastAPI 提供 REST API
- tRPC Gateway 统一 TypeScript 前端
- 最大灵活性但复杂度最高

### 2.3 选型结论

| 阶段 | 方案 | 理由 |
|------|------|------|
| Phase 0-1 | **方案 A（HTTP 直调）** | 最简实现，MVP 不需要类型安全 |
| Phase 2 | 方案 B（OpenAPI 生成） | 需要跨服务类型契约 |
| Phase 3 | 方案 C（双协议） | 生产化、多服务协作 |

### 2.4 Agent 间通讯架构

```
┌─────────────────────────────────────────────────┐
│                tRPC Server (TS)                  │
│  Router: agentRouter / genomeRouter / oedmRouter │
│  Port: 3000                                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  HTTP/WS  ┌──────────┐            │
│  │Textual   │◄─────────►│tRPC      │            │
│  │TUI (Py)  │           │Server    │            │
│  └──────────┘           └──────────┘            │
│                                                  │
│  ┌──────────┐  HTTP      ┌──────────┐            │
│  │Claude    │◄─────────►│tRPC      │            │
│  │Agent SDK │           │Server    │            │
│  │(Python)  │           │          │            │
│  └──────────┘           └──────────┘            │
│                                                  │
│  ┌──────────┐  tRPC      ┌──────────┐            │
│  │Web UI    │◄─────────►│tRPC      │            │
│  │(Next.js) │  (原生)    │Server    │            │
│  └──────────┘           └──────────┘            │
└─────────────────────────────────────────────────┘
```

**但 Phase 0-1 最简方案不需要 tRPC Server：**

```
Textual TUI (Python)
  └── 直接调用 Claude Agent SDK query()
      └── OEDM 循环在同一进程
  └── SQLite 直接读写

无需网络层。tRPC 在需要多进程/多服务时引入。
```

---

## 3. Web 界面技术方案

### 3.1 技术栈

| 技术 | 选型 | 理由 |
|------|------|------|
| 框架 | Next.js 15 (App Router) | SSR + tRPC 集成成熟 |
| 状态 | tRPC React Query | 自动缓存、重试、乐观更新 |
| 可视化 | D3.js + Recharts | Elo 曲线、进化树、热力图 |
| 实时 | tRPC Subscription + SSE | Agent 执行流实时推送 |

### 3.2 Web 界面功能（Phase 2+）

| 页面 | 功能 |
|------|------|
| Dashboard | 全局状态、Agent 群体概览、OEDM 循环进度 |
| Agent Inspector | 单个 Agent 的 Genome 详情、评估历史 |
| Evolution Tree | Darwin GM 式进化谱系图（支持回退） |
| Elo Leaderboard | 动态排名、历史曲线 |
| MAP-Elites Heatmap | 多维质量档案可视化 |
| Execution Stream | 实时执行日志、工具调用流 |

### 3.3 CLI ↔ Web 共享

- **tRPC Router 是单一数据源**：CLI 和 Web 共享同一个 API
- **Genome 状态由 SQLite → tRPC 暴露**：两种界面看到同一数据
- **优先级**：CLI 先行，Web 后补。但 API 层一次设计到位

---

## 4. 最终技术栈推荐

```
Phase 0-1（MVP 最小闭环）:
├── 运行时: Python 3.11+ (Claude Agent SDK)
├── TUI: Textual
├── 存储: SQLite + aiosqlite
├── 通讯: 进程内直接调用（无网络层）
└── 依赖: claude-agent-sdk, textual, aiosqlite, pyyaml

Phase 2（双群体 + 可视化）:
├── + tRPC Server (TypeScript)
├── + Web UI (Next.js)
├── + Python→tRPC HTTP 桥接
└── + Elo 排名系统

Phase 3（生产化）:
├── + tRPC OpenAPI 生成
├── + Codex SDK 沙箱集成
├── + MCP 工具接入 (gitnexus 等)
└── + MAP-Elites 可视化
```

---

## 5. 与架构方案的衔接

本调研报告的结论已反映在 `docs/architecture.md` v0.2 中：

- TUI 面板设计对应架构的三层结构（Task/Meta/Arch Layer）
- tRPC 分阶段引入策略对应架构的渐进式实现路径
- 进程内直接调用策略降低 Phase 0 的启动成本
- Web 界面的功能清单对应架构的数据模型（Elo、MAP-Elites、进化树）

---

## 附录：依赖清单（Phase 0 MVP）

```
# requirements.txt
claude-agent-sdk>=0.1.0
textual>=0.50.0
aiosqlite>=0.19.0
pyyaml>=6.0
httpx>=0.27.0  # tRPC HTTP 调用（Phase 2+）
```
