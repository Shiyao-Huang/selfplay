# README Strange Loop 演示区块文案草稿

> **目标**：为 README 新增 "评估标准的 Strange Loop" 区块，展示多 profile 互补发现盲区
> **日期**：2026-05-12
> **作者**：Researcher
> **数据来源**：Master Docker QA 对比（models.py: code-review 1.00 vs projdevbench 0.62）
> **用途**：嵌入 README.md，展示 SelfPlay 的核心差异化价值

---

## 文案选项

### 选项 A：直接对比式（推荐）

```markdown
## 评估标准的 Strange Loop 🔄

同一份代码，两个评估视角，截然不同的结论：

```
$ selfplay --config selfplay-code-review.yaml check src/models.py
  Score: 1.00  [████████████████████] 1.00
  ✅ 有类型标注  ✅ 有 docstring  ✅ 有错误处理  ✅ 有代码注释

$ selfplay --config selfplay-projdevbench.yaml check src/models.py
  Score: 0.62  [████████████░░░░░░░] 0.62
  ✅ 有错误传播  ✅ 有类型防护
  ❌ 输入验证缺失  ❌ 资源管理缺失  ❌ 边界条件未检查
```

**code-review 说"完美"，projdevbench 说了"3个盲区"。**

这就是 Strange Loop —— 评估标准本身需要进化。
单一视角的"完美"是假象。SelfPlay 让你看到"你不知道你不知道什么"。

试试不同视角：

```bash
# 代码风格视角（10 维度）
selfplay --config selfplay-code-review.yaml check src/your_code.py

# 正确性保证视角（9 维度，基于 ProjDevBench 研究）
selfplay --config selfplay-projdevbench.yaml check src/your_code.py

# 或创建你自己的评估标准
selfplay init
```
```

### 选项 B：叙事式

```markdown
## "完美"代码的盲区 🔄

你刚写完一段代码，跑了一下代码审查：

```
Score: 1.00  ✅ 完美
```

满意了吗？换一个评估视角：

```
$ selfplay --config selfplay-projdevbench.yaml check src/models.py
  Score: 0.62  ❌ 3 个盲区：输入验证、资源管理、边界条件
```

同一份代码，从 1.00 到 0.62。

这不是 bug。这是 SelfPlay 的核心理念：**评估标准本身需要进化**。
没有"完美"的代码，只有"还没找到盲区"的代码。

```bash
# 用不同视角审查你的代码
selfplay --config selfplay-code-review.yaml check src/your_code.py
selfplay --config selfplay-projdevbench.yaml check src/your_code.py
```
```

### 选项 C：数据驱动式（适合技术博客/掘金）

```markdown
## 多维度评估：1.00 不等于"完美"

| 评估 Profile | models.py 分数 | 发现 |
|-------------|---------------|------|
| `code-review` (10 维度) | **1.00** | 类型标注 ✅ docstring ✅ 错误处理 ✅ |
| `projdevbench` (9 维度) | **0.62** | 输入验证 ❌ 资源管理 ❌ 边界条件 ❌ |

同一段代码，code-review 给满分，projdevbench 发现 38% 的质量盲区。

这不是评分不一致——而是**评估维度不同，发现的盲区不同**。
code-review 关注代码风格，projdevbench 关注正确性保证。
两者互补，不是替代。

这就是 SelfPlay 的 Strange Loop：
评估标准在进化 → 发现新盲区 → 定向改进 → 标准再次进化。

```bash
selfplay --config selfplay-code-review.yaml check src/your_code.py
selfplay --config selfplay-projdevbench.yaml check src/your_code.py
```
```

---

## 建议位置

放在 README 的 "代码审查" 区块之后、"架构" 区块之前。
逻辑流：先体验（demo）→ 看到改进 → 发现"完美"是假象 → 了解架构。

---

## 配图建议

1. **并排终端截图**：左边 code-review 1.00（全绿），右边 projdevbench 0.62（有红）
2. **雷达图**：两个 profile 的维度覆盖对比
3. **Strange Loop 循环图**：评估标准 → 发现盲区 → 改进 → 标准进化 → 重新评估

---

*文案草稿完成。推荐选项 A（直接对比式）——最直观、最短、最有冲击力。*
