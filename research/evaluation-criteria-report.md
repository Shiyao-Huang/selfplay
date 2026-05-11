# SelfPlay Agent 评估标准研究报告

> **目标**：为 Phase 2 Config-driven Evaluator 提供评估维度、信号来源、权重设计的研究基础
> **日期**：2026-05-11
> **作者**：Researcher
> **直接输入**：Phase 2 P0 — EvaluationSpec 设计

---

## 1. 研究背景

SelfPlay 的 OEDM 闭环中，Evaluate 是承上启下的关键阶段：
- 承上：对 Observe 阶段的执行结果进行质量判断
- 启下：为 Decide/Mutator 提供改进方向的精确信号

当前 Phase 1 的 HeuristicEvaluator 是硬编码的规则匹配。Phase 2 需要可配置的评估框架（EvaluationSpec），让用户能定义"什么是好的"。

**核心问题**：Agent 自我评估应该评什么、怎么评、如何避免自欺？

---

## 2. 现有系统的评估方法

### 2.1 Reflexion（Shinn et al., NeurIPS 2023）

**架构**：Actor → Evaluator → Self-Reflection 三模型

| 组件 | 功能 | 对 SelfPlay 的映射 |
|------|------|------------------|
| Actor | 生成文本和动作 | Task Agent |
| Evaluator | 对输出打分 | HeuristicEvaluator / ClaudeEvaluator |
| Self-Reflection | 生成语言反馈信号 | Mutator 的输入 |

**关键发现**：
- 评估信号可以是**标量分数**（scalar）或**自然语言**（free-form）
- 反思存储在**情节记忆**（episodic memory）中，跨轮次持久化
- 在 HumanEval 上达到 91% pass@1（GPT-4 基线 80%）
- **局限**：依赖 Agent 的自评能力，复杂任务中可能不准确

**对 SelfPlay 的启发**：
1. 评估不应只有分数——需要结构化的 strengths/weaknesses/suggestions
2. 反思信号（语言描述）比纯分数对 Mutator 更有用
3. 需要外部信号（测试/环境反馈）来校准自评偏差

### 2.2 Darwin Gödel Machine（Sakana AI, ICLR 2026）

**评估方法**：经验式适应度评估（empirical fitness evaluation）

| 特征 | 说明 |
|------|------|
| 评估方式 | 在下游任务（coding benchmarks）上实际运行，用任务得分作为适应度 |
| 进化策略 | 生成变体 → 评分 → 保留改进的 → 丢弃退化的 |
| 评估粒度 | 代码级别（整个 agent 变体的表现） |

**对 SelfPlay 的启发**：
1. **实证优于理论** — DGM 不要求形式化证明，而是用实际任务表现验证
2. **进化树 + 适应度分数** — 这正是 SelfPlay 的 `selfplay tree` 展示的
3. **开放性** — 评估标准不是固定的，可以随进化扩展

### 2.3 Self-Refine（Madaan et al., 2023）

**方法**：迭代自优化框架，Agent 根据任务约束自我评估和改进

| 特征 | 说明 |
|------|------|
| 约束驱动 | 评估基于显式约束（如"更简洁"、"更安全"） |
| 无外部反馈 | 纯自评，不需要外部 evaluator |
| 单轮改进 | 通常 2-3 轮就收敛 |

**对 SelfPlay 的启发**：
1. 评估标准应该**可配置为约束**（constraints），不只是分数
2. 约束可以是定性的（"遵循 PEP8"）或定量的（"测试覆盖率 > 80%"）

### 2.4 行业最佳实践（综合来源）

来自 [Galileo AI](https://galileo.ai/blog/ai-agent-metrics)、[InfoQ](https://www.infoq.com/articles/evaluating-ai-agents-lessons-learned/)、[notes.muthu.co](https://notes.muthu.co/2026/02/agent-evaluation-and-benchmarking-for-measuring-what-matters/) 的共识：

**核心原则："一个数字永远不够"（One number is never enough）**

评估必须是多维度的：

| 维度 | 量度 | 重要性 |
|------|------|--------|
| **成功率** | 任务是否完成 | 必须 |
| **效率** | token 消耗、时间、步骤数 | 高 |
| **成本** | API 调用费用 | 中 |
| **安全性** | 是否产生有害输出 | 必须 |
| **可靠性** | 多次运行的一致性 | 高 |
| **遵循度** | 是否按要求执行 | 高 |

---

## 3. SelfPlay EvaluationSpec 设计建议

基于以上研究，对 Phase 2 Config-driven Evaluator 的设计建议：

### 3.1 评估维度（EvaluationDimensions）

```yaml
evaluation:
  dimensions:
    correctness:
      weight: 0.35
      signals: [test_pass_rate, syntax_check, runtime_error]

    quality:
      weight: 0.25
      signals: [code_style, naming_convention, doc_coverage]

    robustness:
      weight: 0.20
      signals: [error_handling, edge_cases, null_safety]

    efficiency:
      weight: 0.10
      signals: [time_complexity, token_usage, step_count]

    safety:
      weight: 0.10
      signals: [no_injection, no_data_leak, permission_scope]
```

### 3.2 评估信号来源

| 信号类型 | 来源 | 可靠性 | 适用场景 |
|---------|------|--------|---------|
| **测试结果** | 运行测试套件 | 高 | 代码任务 |
| **LLM 评估** | Claude/GPT 评判 | 中 | 通用任务 |
| **启发式规则** | 关键词/模式匹配 | 中-高 | 特定约束 |
| **环境反馈** | 运行时错误/输出 | 高 | 可执行任务 |
| **用户反馈** | 人工标注 | 最高（但稀缺） | 标定基准 |

### 3.3 评估结果结构

结合 Reflexion 的 strengths/weaknesses 模式：

```python
@dataclass
class EvalResult:
    overall_score: float          # 加权总分 [0, 1]
    dimension_scores: dict        # 每维度分数
    strengths: list[str]          # 做得好的地方（给 Mutator 正向信号）
    weaknesses: list[str]         # 需要改进的地方（给 Mutator 改进方向）
    suggestions: list[str]        # 具体改进建议
    evidence: list[EvalEvidence]  # 每个结论的证据来源
    confidence: float             # 评估置信度 [0, 1]
```

### 3.4 自评偏差校准

这是自指系统的根本挑战（Gödel 不完备性的工程体现）。参考 [Zylos Research](https://zylos.ai/research/2026-03-06-ai-agent-reflection-self-evaluation-patterns) 的分析：

| 偏差类型 | 表现 | 校准方法 |
|---------|------|---------|
| **自满偏差** | Agent 总是给自己高分 | 引入外部基准（测试、linter）作为锚点 |
| **过度自信** | confidence 偏高 | 多次独立评估取平均，计算方差 |
| **谄媚偏差** | 改进方向迎合用户偏好而非客观质量 | 区分"用户满意度"和"客观质量"两个维度 |
| **维度遗漏** | 忽略安全/效率等维度 | EvaluationSpec 强制包含所有维度（即使权重为 0） |

---

## 4. Config-driven Evaluator 的 YAML Schema 建议

```yaml
# selfplay.yaml 中的 evaluation 段
evaluation:
  # 评估器类型
  type: composite  # heuristic | llm | composite

  # 维度定义（用户可自定义）
  dimensions:
    - name: correctness
      weight: 0.35
      signals:
        - type: heuristic
          name: test_pass_rate
          source: runtime
        - type: heuristic
          name: syntax_check
          source: ast_parse

    - name: quality
      weight: 0.25
      signals:
        - type: llm
          prompt: "Evaluate code quality on a 0-1 scale..."

    - name: robustness
      weight: 0.20
      signals:
        - type: heuristic
          name: error_handling_ratio
          source: pattern_match

    - name: efficiency
      weight: 0.10
      signals:
        - type: heuristic
          name: token_efficiency
          source: metrics

    - name: safety
      weight: 0.10
      signals:
        - type: heuristic
          name: no_injection_patterns
          source: pattern_match

  # 适应度阈值
  fitness_threshold: 0.6        # 低于此分数的 mutation 被拒绝
  improvement_threshold: 0.05   # 改进幅度低于此值视为无变化
  max_rejected_retries: 3       # 被拒绝后最多重试次数

  # 评估校准
  calibration:
    multi_run_average: false     # 是否多次评估取平均
    confidence_threshold: 0.7    # 评估置信度低于此值时标记为不确定
```

---

## 5. 评估维度与用户痛点映射

回到用户反馈洞察（`research/user-feedback-insights.md`），评估维度应该直接对应用户最在意的痛点：

| 用户痛点（TOP 5） | 评估维度 | 信号设计 |
|-----------------|---------|---------|
| #1 "差一点就对了" | correctness + robustness | test_pass_rate + error_handling_ratio |
| #2 质量退化 | correctness (趋势) | 跨版本 score 趋势监控 |
| #3 错误处理无能 | robustness | error_handling_ratio + exception_coverage |
| #4 速度 vs 质量 | efficiency + correctness | 分数/时间比，不是只看分数 |
| #9 指令遵循差 | quality (following维度) | 指令匹配度检查 |

---

## 6. 实现优先级建议

基于研究和对 Phase 2 路线图的影响：

| 优先级 | 功能 | 原因 |
|--------|------|------|
| **P0** | EvaluationSpec YAML 加载 | 让用户能自定义评估维度和权重 |
| **P0** | 结构化 EvalResult（strengths/weaknesses/evidence） | 给 Mutator 精确信号而非模糊分数 |
| **P1** | CompositeEvaluator（heuristic + llm 组合） | 单一信号源不可靠 |
| **P1** | evidence 字段强制要求 | 解决"自评偏差"——每个结论有证据 |
| **P2** | 多次评估取平均（calibration） | 降低非确定性带来的噪音 |
| **P2** | 评估置信度字段 | 标记不确定评估，避免 Mutator 基于低置信信号修改 |

---

## 7. 参考来源

| 来源 | 关键贡献 | 状态 |
|------|---------|------|
| [Reflexion (Shinn et al., NeurIPS 2023)](https://arxiv.org/abs/2303.11366) | Actor-Evaluator-Reflection 三模型、verbal reinforcement、episodic memory | [VERIFIED] |
| [Darwin Gödel Machine (Sakana AI, ICLR 2026)](https://arxiv.org/abs/2505.22954) | 经验式适应度评估、进化树、开放性搜索 | [VERIFIED] |
| [Self-Refine (Madaan et al., 2023)](https://arxiv.org/abs/2303.17651) | 约束驱动的自优化 | [VERIFIED] |
| [AI Agent Metrics — Galileo AI](https://galileo.ai/blog/ai-agent-metrics) | 多维度评估最佳实践 | [VERIFIED] |
| [Evaluating AI Agents — InfoQ](https://www.infoq.com/articles/evaluating-ai-agents-lessons-learned/) | 混合评估管道、生产环境教训 | [VERIFIED] |
| [Agent Evaluation — notes.muthu.co](https://notes.muthu.co/2026/02/agent-evaluation-and-benchmarking-for-measuring-what-matters/) | "一个数字不够"、多轮评估 | [VERIFIED] |
| [AI Agent Reflection Patterns — Zylos Research](https://zylos.ai/research/2026-03-06-ai-agent-reflection-self-evaluation-patterns) | 自评偏差分析 | [VERIFIED] |
| [Self-Evolving Benchmarks (Fudan DISC)](http://www.fudan-disc.com/) | 自进化基准框架 | [VERIFIED] |

---

*报告完成。直接输入 Phase 2 EvaluationSpec 设计，等待 SA/Builder 参考。*
