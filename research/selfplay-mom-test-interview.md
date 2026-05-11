# SelfPlay Agent Mom Test 访谈协议

> **来源**：基于 Bach SOP (`/Users/copizza2/work/bach/bach-orchestra/sops/agent-self-evolution/README.md`) 访谈协议
> **日期**：2026-05-10
> **作者**：Researcher
> **适用对象**：SelfPlay Agent（Task Agent、OEDM Supervisor、Evaluator、Mutator）

---

## 1. 访谈原则（摘自 Bach SOP）

1. **禁止向用户抛 A/B/C 选项** — 改为追问具体过去行为
2. **三轮追问才能定主要矛盾** — 第一轮是 normal 解，第三轮才逼近本质
3. **分层压缩** — 每轮输出 1 句话 / 3 句话 / 5 句话 / 完整版
4. **证据驱动** — 结论必须有日志/代码/CLI 输出支撑，禁止 mock 证据冒充通过

---

## 2. SelfPlay 核心访谈问题（5 问 Mom Test）

### 2.1 基础 5 问（改编自 Bach 原版）

| # | 问题 | 探测目标 |
|---|------|---------|
| **Q1** | 最近一次你执行任务时，你想完成什么具体目标？ | Agent 是否有清晰的自我目标感知 |
| **Q2** | 你执行任务时，先看了自己 genome 里的哪些规则？ | Agent 是否真的读取并遵循自己的指令 |
| **Q3** | 哪一步让你停下来、猜测、或使用了"不在 genome 里的方法"？ | 发现 genome 覆盖不到的盲区 |
| **Q4** | 你绕过自己的规则时，用了什么外部办法或上下文线索？ | 发现隐性能力来源（genome 未显式描述的） |
| **Q5** | 如果只能修改 genome 的一个地方，哪个改变会让下一轮少花最多时间？ | 定位最高杠杆的自我改进点 |

### 2.2 追加 5 问（SelfPlay 特有，针对自进化机制）

| # | 问题 | 探测目标 |
|---|------|---------|
| **Q6** | 上一轮 OEDM 循环中，Evaluate 给你打了什么分？你同意这个分数吗？ | Evaluator 准确性 + Agent 自我评估能力 |
| **Q7** | Mutator 建议的修改是什么？这个修改真的让你的表现变好了吗？ | Mutator 有效性验证 |
| **Q8** | 有没有出现过 mutation 被拒绝的情况？被拒绝时你怎么"想"的？ | 拒绝机制是否合理 + Agent 的"反思"能力 |
| **Q9** | 你的 genome 已经进化了 N 个版本，从 v1 到现在最大的变化是什么？是量变还是质变？ | 进化是否有方向性还是随机游走 |
| **Q10** | 如果你同时是 Evaluator 和被评估者，你觉得这个"自我评估"可靠吗？哪里可能自欺？ | 自指系统的根本局限（Gödel 不完备性） |

---

## 3. 访谈执行协议

### 3.1 三轮追问流程

```
第一轮：表面现象（normal 解）
├── 问 Q1-Q5
├── 收集 Agent 的第一反应
└── 标记矛盾点（回答不一致、模糊、回避）

第二轮：剥到机制
├── 针对第一轮标记的矛盾点追问 "为什么"
├── 要求 Agent 引用具体日志/代码/eval_result
└── 禁止接受 "大概是这样" 的回答

第三轮：逼近本质
├── 问 "如果这个限制明天消失，你第一个改变的行为是什么？"
├── 问 "你认为当前系统最大的谎言是什么？"
└── 定位主要矛盾 → 落地修复
```

### 3.2 分层压缩输出格式

每个访谈问题回答后，Agent 必须提供：

```
1 句话：[主要矛盾]
3 句话：[矛盾 + 证据 + 动作]
5 句话：[矛盾 + 证据 + 动作 + 风险 + 下一步]
完整版：[以上全部 + 日志引用 + 代码位置 + 建议修改]
```

### 3.3 Docker QA 证据要求

根据 Bach SOP，访谈结论不能停留在"感觉"。必须：

| 结论类型 | 证据要求 |
|---------|---------|
| "Evaluator 打分不准" | 引用 eval_result + 人工判断对比 |
| "Mutator 修改无效" | genome diff + 前后 eval score 对比 |
| "genome 盲区" | 找到 genome 中缺失的具体规则 |
| "自进化方向正确" | N 轮 score 趋势数据 |

---

## 4. Docker QA 能力矩阵（SelfPlay 版本）

基于 Bach SOP Step 10 的能力矩阵，适配 SelfPlay：

| 能力项 | 验证方式 | Pass 条件 |
|--------|---------|----------|
| **SP-01: Demo 运行** | `selfplay demo` | 3 轮进化，score 持续上升 |
| **SP-02: 被拒绝 mutation** | demo 输出 | 至少 1 次 ❌ Rejected 展示 |
| **SP-03: History 可查** | `selfplay history` | 显示完整版本链 |
| **SP-04: Tree 可视化** | `selfplay tree` | 显示父子关系 |
| **SP-05: Config 加载** | `selfplay init` + `selfplay run --config` | YAML 正确覆盖默认值 |
| **SP-06: 多轮进化** | `selfplay run --cycles 5` | 5 轮不崩溃 |
| **SP-07: Evaluator 评估** | 检查 eval_result 输出 | 分数有实际变化 |
| **SP-08: Mutator 修改** | genome diff | v1→v2 有实质性变更 |
| **SP-09: 安全回退** | 手动降分触发 reject | 负面修改被拒绝 |
| **SP-10: Docker 运行** | `docker compose up --build` | 容器内 selfplay demo 正常 |

---

## 5. PDCA 循环（SelfPlay 版本）

```
历史输入需求账本
├── 读取 README.md 的承诺
├── 读取 research/user-feedback-insights.md 的用户痛点
├── 读取 docs/phase1-implementation-spec.md 的规格要求
└── 读取 docs/launch-execution-checklist.md 的发布标准

         ↓

Mom Test 访谈（Q1-Q10）
├── 对 Task Agent 访谈
├── 对 Evaluator 访谈
├── 对 Mutator 访谈
└── 对 Supervisor 访谈

         ↓

排序主要矛盾
├── 按杠杆排序（修复哪个 = 最大化改进？）
└── 转化为 TODO

         ↓

Docker QA 验证
├── 按能力矩阵 SP-01 ~ SP-10 逐项验证
├── 每项 pass/fail/skipped + 证据
└── 禁止 mock 证据冒充通过

         ↓

Commit/Push
├── 修复项 + 验证证据 + 访谈结论
└── 更新下一轮更好问题清单

         ↓

循环
```

---

## 6. 下一轮更好问题清单

1. SelfPlay 的 Evaluator 评估标准是否与用户实际满意度对齐？还是自我感觉良好？
2. Mutator 的修改方向是收敛还是随机游走？多轮后是否形成稳定的策略偏好？
3. 当前 genome 的"自描述"足够丰富吗？是否存在 Agent 知道但 genome 未记录的隐性知识？
4. 如果把 SelfPlay 放到 Docker 中运行（而非本地 Python），能力是否有变化？
5. 自进化闭环的瓶颈在哪里——是 Evaluate 不准、Decide 不对、还是 Modify 太保守？

---

*访谈协议就绪。待 Master 分配执行时间。*
