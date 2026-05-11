# Phase 2 规格：Config-Driven Evaluator + Per-Feature Evidence Ledger

**Version**: 1.1（Builder QA review 修订）
**Date**: 2026-05-11
**Author**: SA (Solution Architect)
**来源**: Mom Test 访谈三方收敛（SA Q5 + Builder Q5 + Builder Q3 确认）

## 一句话

把 `evaluator.py` 的 8 个硬编码 regex 检查替换为 `config.yaml` 声明的 `EvaluationSpec`，让每个评估维度可配置、可审计、可进化。

## 三句话

1. 当前 `HeuristicEvaluator` 的 8 个 feature check（`evaluator.py:29-58`）是进化的唯一方向控制器 — 系统只能学"补关键词"，不能学"变好"。
2. 改为 config-driven 后，用户可以增删评估维度、调整权重、甚至注入自定义 pattern — 进化方向从硬编码变为用户可定义。
3. `EvalResult` 扩展为 per-feature breakdown（每个维度 passed/score/evidence），让 Docker QA 能验证"为什么进化"，不只是"分数变了"。

## 动机：为什么这是 Phase 2 最高优先级

### Mom Test 证据

| Agent | 访谈问题 | 核心发现 |
| --- | --- | --- |
| SA (Q5) | "修改哪个地方杠杆最大" | "一个 YAML 数组替换 8 个 if-else，是 Phase 2 MAP-Elites 的前置条件" |
| Builder (Q5) | "只能改一个地方" | "EvaluationSpec: 评估维度/pattern/weight 从配置加载" |
| Builder (Q3) | "哪步让你停下来" | "系统在优化 evaluator 的关键词，不是真实用户满意度" |

两个独立 agent 得出相同结论 → **高置信度**。

### 当前瓶颈

```
evaluator.py:29-58  ──→  固定 8 个维度 + 权重
     ↓
mutator.py:62-72   ──→  从 weakness 文本重写 prompt
     ↓
mock adapter       ──→  关键词匹配，越多越高分
     ↓
结果：系统学会"补关键词"，不是"变好"
```

### 目标架构

```
config.yaml        ──→  evaluation.dimensions: [{label, pattern, weight, enabled}]
     ↓
ConfigDrivenEvaluator  ──→  按 spec 执行，产出 per-feature breakdown
     ↓
EvalResult         ──→  {score, features: [{id, passed, score, evidence}], ...}
     ↓
RuleBasedMutator   ──→  从 failed feature ids 生成 mutation（不再从自然语言 weakness 反推）
     ↓
Docker QA          ──→  验证"修改 config 维度 → breakdown/score 可解释变化"
```

## 设计

### 1. EvaluationSpec 数据结构

```yaml
# selfplay.yaml 新增 section
evaluation:
  dimensions:
    - id: conclusion
      label: "有短结论"
      pattern: "结论|一句话|summary|conclusion"
      weight: 0.16
      enabled: true
    - id: evidence
      label: "有证据路径"
      keywords: ["证据", "路径", "验证", "evidence"]
      weight: 0.16
      enabled: true
    - id: next_step
      label: "有下一步"
      keywords: ["下一步", "next"]
      weight: 0.12
      enabled: true
    - id: error_handling
      label: "覆盖错误处理"
      keywords: ["错误", "边界", "异常", "edge"]
      weight: 0.14
      enabled: true
    - id: performance
      label: "覆盖复杂度/性能"
      keywords: ["复杂度", "性能", "performance"]
      weight: 0.12
      enabled: true
    - id: examples
      label: "包含示例"
      keywords: ["示例", "样例", "example"]
      weight: 0.10
      enabled: true
    - id: structure
      label: "结构清晰"
      keywords: ["步骤", "结构", "分层"]
      weight: 0.10
      enabled: true
    - id: length
      label: "信息量足够"
      type: length
      min_length: 80
      weight: 0.10
      enabled: true
```

### 2. 代码变更清单

| 文件 | 变更 | 影响 |
| --- | --- | --- |
| `src/selfplay/config.py` | 新增 `EvaluationDimension` dataclass + `SelfPlayConfig.dimensions` 字段 | config 加载/序列化 |
| `src/selfplay/evaluator.py` | `HeuristicEvaluator` 从 `config.dimensions` 构建 checks，而非硬编码 | 核心变更 |
| `src/selfplay/models.py` | `EvalResult` 新增 `features: list[FeatureBreakdown]` 字段 | 结构化证据 |
| `src/selfplay/mutator.py` | `RuleBasedMutator` 从 `failed_feature_ids` 生成 mutation | 更精确的进化方向 |
| `src/selfplay/cli.py` | `--verbose` 或 `--json` 时输出 per-feature breakdown | 用户可见性 |
| `src/selfplay/storage.py` | `evaluations` 表新增 `features_json` 列 | 持久化 |

### 3. FeatureBreakdown 结构

```python
@dataclass
class FeatureBreakdown:
    id: str           # dimension id, e.g. "conclusion"
    label: str        # human-readable label
    passed: bool      # 是否通过
    score: float      # 该维度的权重贡献（passed=effective_weight, failed=0）
    raw_weight: float     # config 中声明的原始权重
    effective_weight: float  # 归一化后的有效权重（raw_weight / sum(enabled weights)）
    evidence: str     # "matched_keyword: 结论" 或 "not_found"，上限 80 chars
```

### 3.1 Config Parser 方案（Builder Review P0 修正）

当前 `_parse_flat_yaml` 只支持 scalar。`evaluation.dimensions` 是 nested list。**最小可实现方案**：

引入 `pyyaml` 作为可选依赖（`pip install pyyaml`），仅在 `selfplay.yaml` 包含 `evaluation:` section 时使用。理由：
- 自写 nested parser 容易出 bug，不值得
- JSON string 方案用户不友好
- PyYAML 是 Python 生态标准依赖，体积小

```python
# config.py 新增
def _parse_dimensions(text: str) -> list[EvaluationDimension]:
    """Parse evaluation.dimensions from YAML. Requires pyyaml."""
    try:
        import yaml
    except ImportError:
        return []  # fallback to hardcoded
    data = yaml.safe_load(text) or {}
    dims = data.get("evaluation", {}).get("dimensions", [])
    return [EvaluationDimension(**d) for d in dims if d.get("enabled", True)]
```

`pyproject.toml` 新增 `evaluation = ["pyyaml>=6.0"]` 可选依赖组。

### 3.2 权重归一化（Builder Review P1 修正）

- **默认 config（无 dimensions）**: 直接使用硬编码 8 维权重，分数与 Phase 1 完全一致
- **自定义 config**: 按 `enabled` 维度的 weight 之和归一化
- `FeatureBreakdown` 同时记录 `raw_weight` 和 `effective_weight`，让用户看到归一化前后
- 公式: `effective_weight = raw_weight / sum(d.raw_weight for d in enabled_dims)`

### 3.3 Evidence 字段安全（Builder Review P1 修正）

- `evidence` 字段上限 80 chars，超出截断 + `...`
- 匹配 keyword 时记录 `matched_keyword: <keyword>`，不记录原文
- 无匹配返回 `"not_found"`
- 禁止记录 token/secret/env 内容（evaluator 只看 task + output，不看 image 的内部状态）

### 3.4 SQLite Migration（Builder Review P1 修正）

```python
# storage.py __init__ 新增幂等迁移
def _ensure_features_column(self, conn):
    """Idempotent ALTER TABLE for features_json column."""
    cursor = conn.execute("PRAGMA table_info(evaluations)")
    columns = {row[1] for row in cursor.fetchall()}
    if "features_json" not in columns:
        conn.execute("ALTER TABLE evaluations ADD COLUMN features_json TEXT DEFAULT '[]'")
```

### 4. 向后兼容

- 如果 `selfplay.yaml` 没有 `evaluation.dimensions`，使用当前 8 个硬编码维度（默认行为不变）
- `EvalResult.features` 默认为空列表，旧代码不需要改
- `FeatureBreakdown` 是增量字段，不影响现有 `score/strengths/weaknesses`

### 5. Docker QA 回归项（Builder Review 修正）

| ID | 能力 | Phase | 通过门槛 |
| --- | --- | --- | --- |
| SP-11 | Config-driven evaluator | 2.1 | 修改 config 中某个维度 weight → `demo --json` 的 breakdown/score 可解释变化 |
| SP-12 | Per-feature breakdown 持久化 | 2.2 | `history --json` 包含 features 字段，每个维度有 passed/score/evidence |
| SP-13 | 向后兼容 | 2.1 | 无 `evaluation.dimensions` 的 config → `demo --json` 分数与 Phase 1 完全一致 |
| SP-14 | 默认 parity | 2.1 | 默认 8 维 config → `demo --json` features 有 8 项，score ≈ Phase 1 |
| SP-15 | 自定义配置变化 | 2.1 | 新增/禁用/改权重后，同一 task 的 breakdown/score 可解释变化 |

## 实现路径

```
Phase 2.1 (P0):
  ├── Step 1: EvaluationDimension dataclass + _parse_dimensions (config.py, 引入 pyyaml 可选依赖)
  ├── Step 2: FeatureBreakdown dataclass + EvalResult.features (models.py)
  ├── Step 3: ConfigDrivenEvaluator (evaluator.py，从 config.dimensions 动态构建 checks + 权重归一化)
  ├── Step 4: Docker QA 验证 SP-11 + SP-13 + SP-14 + SP-15
  └── 边界：2.1 只验 demo --json features，不含 storage/history（SP-12 在 2.2）

Phase 2.2 (P1):
  ├── Step 5: Storage 幂等迁移 features_json + 持久化 (storage.py)
  ├── Step 6: CLI 输出 per-feature breakdown (--verbose / --json)
  ├── Step 7: Mutator 从 failed_feature_ids 生成结构化 mutation (mutator.py)
  └── Docker QA 验证 SP-12

Phase 2.3 (P2):
  ├── Step 8: 多套 evaluation profiles（可按 runtime adapter 切换评估维度）
  ├── Step 9: ClaudeEvaluator 使用同一套 EvaluationSpec（校准 heuristic）
  └── Step 10: 自进化的评估维度（Agent 自己提出新 dimension → 人工审批 → 合并进 config）
```

## 验收标准

### Phase 2.1 (P0)
1. 默认 config（无 `evaluation.dimensions`）→ `demo --json` 分数与 Phase 1 完全一致（SP-14）
2. `demo --json` 输出包含 `features` 数组，每项有 id/label/passed/score/raw_weight/effective_weight/evidence
3. 修改某个维度的 weight → breakdown/score 可解释变化（SP-11）
4. 新增一个自定义维度 → demo 输出包含该维度的 breakdown（SP-15）
5. 禁用一个维度 → 该维度不参与评分，其余维度权重归一化
6. 无 `evaluation.dimensions` → 行为与 Phase 1 完全一致（SP-13）

### Phase 2.2 (P1)
7. `history --json` 包含 per-feature breakdown（SP-12）
8. SQLite `features_json` 列存在，旧 rows 返回 `features=[]`

### Docker QA
9. From-zero build + SP-11 + SP-13 + SP-14 + SP-15 全部 PASS (Phase 2.1)
10. SP-12 PASS (Phase 2.2)

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| YAML 解析复杂度 | 引入 pyyaml 可选依赖；无 pyyaml 时 fallback 到硬编码维度，不报错 |
| 旧 config 不兼容 | 默认 fallback 到硬编码维度，不报错 |
| 权重总和 ≠ 1.0 | 运行时 normalize enabled 维度；breakdown 同时显示 raw_weight 和 effective_weight |
| pattern 注入安全 | pattern 仅用于 `re.search`，不用于 `re.sub` 或命令执行 |
| evidence 字段泄露 | 上限 80 chars，记录 matched_keyword 不记录原文，不接触 token/secret |
| SQLite migration 失败 | 幂等 ALTER TABLE（PRAGMA table_info 检查列是否存在），旧 rows features=[] |

## 与 Phase 3 的关系

Config-driven evaluator 是 MAP-Elites（Phase 3）的前置条件：
- MAP-Elites 需要多维度的 fitness landscape → config-driven dimensions 提供维度定义
- MAP-Elites 需要可比较的 fitness score → FeatureBreakdown 提供结构化对比
- 自进化的评估维度（Phase 2.3 Step 10）是 Strange Loop 的起点：Agent 不只优化自身 prompt，还优化评估自身的标准
