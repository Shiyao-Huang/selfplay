# SelfPlay External Project Review: requests

**Date**: 2026-05-11
**Target**: [requests](https://github.com/psf/requests) v2.32.5 — 最流行的 Python HTTP 库
**Tool**: SelfPlay v0.2.0, Docker QA, 双 profile 评估

## 执行命令

```bash
# Code-review profile (需指定 --config 以使用 YAML profile)
docker run --rm -v /path/to/requests-src:/review selfplay-final2 \
  selfplay --config examples/selfplay-code-review.yaml check /review/requests/<file>.py

# ProjDevBench profile
docker run --rm -v /path/to/requests-src:/review selfplay-final2 \
  selfplay --config examples/selfplay-projdevbench.yaml check /review/requests/<file>.py
```

## Results

### Code-Review Profile (代码风格/工程实践维度)

| File | Score | Status |
|------|-------|--------|
| api.py | 0.50 | ⚠️ 缺少 logging, type check, test markers |
| exceptions.py | 0.50 | ⚠️ 简单文件 |
| structures.py | 0.50 | ⚠️ 缺少 docstring, logging |
| auth.py | 0.64 | ⚠️ 部分通过 |
| models.py | 0.74 | ✅ 良好 |
| utils.py | 0.74 | ✅ 良好 |
| sessions.py | 0.82 | ✅ 良好 |
| cookies.py | 0.84 | ✅ 良好 |
| adapters.py | 0.92 | ✅ 优秀 |

**Avg: 0.69**

### ProjDevBench Profile (正确性/工程维度)

| File | Score | Status |
|------|-------|--------|
| api.py | 0.24 | ❌ 简单文件，工程维度少 |
| exceptions.py | 0.44 | ⚠️ 纯异常定义 |
| auth.py | 0.56 | ⚠️ 部分工程模式 |
| structures.py | 0.58 | ⚠️ 部分工程模式 |
| sessions.py | 0.80 | ✅ 良好 |
| cookies.py | 0.84 | ✅ 良好 |
| models.py | 0.84 | ✅ 良好 |
| adapters.py | 0.92 | ✅ 优秀 |
| utils.py | 0.92 | ✅ 优秀 |

**Avg: 0.68**

### 双 Profile 对比

| File | Code-Review | ProjDevBench | Diff |
|------|------------|-------------|------|
| adapters.py | 0.92 | 0.92 | 0.00 |
| utils.py | 0.74 | 0.92 | -0.18 |
| cookies.py | 0.84 | 0.84 | 0.00 |
| models.py | 0.74 | 0.84 | -0.10 |
| sessions.py | 0.82 | 0.80 | +0.02 |
| structures.py | 0.50 | 0.58 | -0.08 |
| auth.py | 0.64 | 0.56 | +0.08 |
| exceptions.py | 0.50 | 0.44 | +0.06 |
| api.py | 0.50 | 0.24 | +0.26 |

**观察**: 两个 profile 对同一文件给出不同但相关的评估角度。核心文件（adapters/cookies）两者一致高分，简单文件差异更大。

### 关键发现

#### 1. 两个 profile 对高质量代码给出一致评价

- adapters.py/cookies.py: 两个 profile 均给出 0.84~0.92 — 双重验证
- 简单文件（api.py）: code-review 0.50 vs projdevbench 0.24 — 不同角度发现不同弱点

#### 2. 维度级互补分析（adapters.py, 双 profile 均 0.92）

**Code-Review 唯一失分项**: 日志记录（无 logging 调用）
**ProjDevBench 唯一失分项**: 测试证据（无 test_/assert 引用）

两个 profile 的失败维度**不重叠** — 再次验证互补性。

#### 3. 质量梯度与直觉一致

- 简单文件（api/exceptions/structures）：0.24~0.58 — 工程模式少
- 核心文件（adapters/utils/models/sessions/cookies）：0.74~0.92 — 扎实工程实践
- requests 经过多年社区审查，核心模块质量确实更高

## 结论

1. **SelfPlay 正确识别了 requests 的质量梯度** — 核心文件高分，工具文件低分
2. **双 profile 互补有效** — 失败维度不重叠，覆盖面更广
3. **两个 profile 均为语言无关** — 可评估任意 Python 项目（注：需用 `--config` 指定 YAML profile）
4. **Docker volume mount 方案** — 5 分钟完成 9 文件双角度评估，开箱即用

## PMF 价值

SelfPlay 在 5 分钟内完成了对一个知名开源项目的 9 文件双角度质量评估，产出：
- 文件级分数和排名
- 维度级弱点分析
- 双 profile 互补验证
- 明确的改进方向

这证明了 SelfPlay 可以作为**通用代码质量评估工具**使用——不仅限于自研代码。
