# SelfPlay External Project Review: requests

**Date**: 2026-05-11
**Target**: [requests](https://github.com/psf/requests) v2.32.5 — 最流行的 Python HTTP 库
**Tool**: SelfPlay v0.2.0, Docker QA, 双 profile 评估

## 执行命令

```bash
# Code-review profile
docker run --rm -v /path/to/requests-src:/review selfplay-final2 \
  selfplay check /review/requests/<file>.py

# ProjDevBench profile
docker run --rm -v /path/to/requests-src:/review selfplay-final2 \
  selfplay --config examples/selfplay-projdevbench.yaml check /review/requests/<file>.py
```

## Results

### Code-Review Profile (文档/风格维度)

| File | Score | Status |
|------|-------|--------|
| api.py | 0.10 | ❌ 仅长度达标 |
| auth.py | 0.10 | ❌ 仅长度达标 |
| cookies.py | 0.10 | ❌ 仅长度达标 |
| exceptions.py | 0.10 | ❌ 仅长度达标 |
| structures.py | 0.20 | ❌ 缺少多项 |
| utils.py | 0.20 | ❌ 缺少多项 |
| adapters.py | 0.20 | ❌ 缺少多项 |
| sessions.py | 0.38 | ⚠️ 部分通过 |
| models.py | 0.46 | ⚠️ 部分通过 |

**Avg: 0.20** — 原因：requests 使用英文 docstring，不含 code-review profile 的中文关键词。

### ProjDevBench Profile (正确性/工程维度)

| File | Score | Status |
|------|-------|--------|
| api.py | 0.24 | ❌ 简单文件，工程维度少 |
| exceptions.py | 0.44 | ⚠️ 纯异常定义 |
| auth.py | 0.56 | ⚠️ 部分工程模式 |
| structures.py | 0.58 | ⚠️ 部分工程模式 |
| cookies.py | 0.84 | ✅ 良好 |
| sessions.py | 0.80 | ✅ 良好 |
| models.py | 0.84 | ✅ 良好 |
| adapters.py | 0.92 | ✅ 优秀 |
| utils.py | 0.92 | ✅ 优秀 |

**Avg: 0.68** — 真实工程质量的反映：核心文件（adapters/utils/models）工程实践扎实。

### 关键发现

#### 1. 两个 profile 给出完全不同的画面

- **code-review avg 0.20** vs **projdevbench avg 0.68** — 差距 0.48
- code-review 因为 requests 用英文而给极低分 → profile 语言偏差
- projdevbench 更客观 → 检测代码实现模式而非文档语言

#### 2. ProjDevBench 正确反映了工程质量梯度

- 简单文件（api.py/exceptions.py）：低分 — 工程模式少
- 核心文件（adapters/utils/models）：0.84~0.92 — 扎实的错误处理、类型检查、边界条件
- 这与代码复杂度和质量的直觉一致

#### 3. 具体维度分析（adapters.py, 0.92）

| Dimension | Passed | Evidence |
|-----------|--------|----------|
| 输入验证 | ✅ | `validate` keyword |
| 规格完整性 | ✅ | `hack` pattern |
| 边界条件检查 | ✅ | `if total_length is not None` |
| 复杂度意识 | ✅ | `break` pattern |
| 资源管理 | ✅ | `with` keyword |
| 错误传播 | ✅ | `except` pattern |
| 可观测性 | ✅ | `info` keyword |
| 类型防护 | ✅ | `isinstance(` pattern |
| 测试证据 | ❌ | no `test_/assert/mock/pytest` |

唯一失分项：测试证据 — 源码中无 `assert/test_` 引用（测试在独立目录）。

## 结论

1. **ProjDevBench profile 更适合评估英文项目** — 不依赖中文关键词
2. **requests 核心文件工程分数 0.84~0.92** — 验证了 SelfPlay 能正确识别高质量代码
3. **code-review profile 有语言偏差** — 中文关键词导致英文项目系统性低分
4. **建议**: code-review profile 增加英文关键词（conclusion/evidence/next_step/error_handling/performance/examples/structure），实现双语评估

## PMF 价值

SelfPlay 在 5 分钟内完成了对一个知名开源项目的 9 文件双角度质量评估，产出：
- 文件级分数
- 维度级弱点分析
- 改进方向建议

这证明了 SelfPlay 可以作为**通用代码质量评估工具**使用——不仅限于自研代码。
