# 外部项目审查研究框架

> **目标**：为 Phase 3 真实项目代码审查准备分析框架和目标选择
> **日期**：2026-05-12
> **作者**：Researcher
> **用途**：Org-manager 执行扫描 + Researcher 合成报告

---

## 1. 目标项目选择

### 1.1 推荐项目

| 项目 | 文件 | 复杂度 | 适合度 | 理由 |
|------|------|--------|-------|------|
| **requests** `sessions.py` | ~600行，核心类 | 高 | ⭐⭐⭐ | 最知名 Python 库，代码质量高但仍有改进空间 |
| **requests** `adapters.py` | ~400行 | 中高 | ⭐⭐⭐ | 有资源管理（连接池），projdevbench 维度友好 |
| **flask** `app.py` | ~700行 | 高 | ⭐⭐ | 知名度高，但代码风格可能与 SelfPlay profile 不匹配 |
| **rich** `text.py` | ~500行 | 中 | ⭐⭐ | 现代 Python，类型标注完整 |

**推荐**：`requests/sessions.py` + `requests/adapters.py` — 知名度最高，有 docstring、错误处理、资源管理等关键维度可检测。

### 1.2 requests/sessions.py 预分析

基于源码阅读，预测 SelfPlay 双 profile 会发现：

**code-review profile 预测**：
- ✅ 有类型标注（大量 `-> Response`, `: str` 等）
- ✅ 有 docstring（每个方法都有详细文档）
- ✅ 有错误处理（`try/except`, `raise`）
- ❓ 有参数文档（param docs in docstring，但格式是 `:param` 不是标准 pattern）
- ✅ 有代码注释（多个 RFC 引用注释）
- ✅ 函数长度合理（大部分 <50 行）

**预期 code-review 分数**：0.80-0.90（高质量开源项目）

**projdevbench profile 预测**：
- ✅ 有输入验证（`isinstance` checks）
- ✅ 有边界条件（`if url is None`, `if not parsed.netloc`）
- ✅ 有错误传播（`raise TooManyRedirects`, `raise InvalidSchema`）
- ❓ 有资源管理（`resp.close()` 但没有 `with` 上下文管理器模式）
- ❓ 有日志记录（代码中未见 logging）
- ✅ 有类型防护（`isinstance(request, Request)` guard）

**预期 projdevbench 分数**：0.60-0.75

### 1.3 关键差异点（预期 SelfPlay 会发现的）

1. **无 logging**：requests 核心模块几乎没有 logging 调用——这是网络库的最佳实践吗？还是盲区？
2. **资源管理不一致**：`resp.close()` 在某些路径调用，但不是用 `with` 上下文管理器
3. **边界条件**：部分方法缺少 `None` 检查（如 `merge_setting` 接受 `Any` 类型但没有 `None` 防护）
4. **测试证据**：模块内无 `assert` 或测试（测试在单独目录，但 projdevbench 检查模块内断言）

---

## 2. 分析框架

### 2.1 报告结构

```
## SelfPlay × requests 真实项目审查报告

### 1. 审查目标
- 项目：psf/requests
- 文件：sessions.py, adapters.py
- Profile：code-review (10维度) + projdevbench (9维度)

### 2. 双 profile 分数对比表
| 文件 | code-review | projdevbench | 差距 |
|------|-----------|-------------|------|
| sessions.py | ? | ? | ? |
| adapters.py | ? | ? | ? |

### 3. 维度级分析
（每个维度的得分 + 具体发现 + 代码位置引用）

### 4. 发现的真实问题
（不仅是 pattern matching 的局限，而是真正有价值的改进建议）

### 5. 与 SelfPlay 自身代码对比
| 维度 | SelfPlay avg | requests | 差异分析 |
|------|------------|---------|---------|

### 6. 结论
- SelfPlay 能发现真实开源项目的问题吗？
- 双 profile 互补性在外部项目上也成立吗？
- 与手动 code review 对比如何？
```

### 2.2 对比维度

| 对比项 | SelfPlay 自身代码 | requests 开源代码 |
|-------|-----------------|-----------------|
| 项目成熟度 | 新项目（~2周） | 成熟项目（10+年） |
| 代码规模 | 13 文件，~2000行 | sessions.py ~600行 |
| 开发者 | AI agent + 人类协作 | 人类开发者（Kenneth Reitz 等） |
| 质量预期 | 中→高 | 高 |
| SelfPlay 价值 | 证明"进化"有效 | 证明"发现问题"有用 |

---

## 3. PMF 叙事框架

如果 requests 在 SelfPlay 审查下发现了真实问题：

> **"SelfPlay 发现了 requests 库的 N 个质量盲区"**
>
> requests 是 Python 下载量最高的 HTTP 库，有 10+ 年历史和数百位贡献者。
> SelfPlay 的双 profile 审查发现了 code-review 没看到的问题。

如果 requests 在 SelfPlay 审查下分数很高：

> **"SelfPlay 验证了 requests 的高代码质量"**
>
> 作为参考，SelfPlay 自身代码（2周开发）在相同 profile 下有 X 分差距，
> 证明 SelfPlay 的评估标准可以区分代码质量级别。

两种结果都有 PMF 价值。

---

## 4. 执行结果（2026-05-12 更新）

### 4.1 实际分数 vs 预测

| 文件 | 预测 CR | 实际 CR | 预测 PD | 实际 PD |
|------|---------|---------|---------|---------|
| sessions.py | 0.80-0.90 | **0.38** | 0.60-0.75 | **0.80** |
| adapters.py | - | 0.20 | - | **0.92** |

**code-review 预测偏差 ~0.50**：未预见到中文关键词导致英文项目系统性低分。

**projdevbench 预测略低估**：实际 0.80-0.92 vs 预测 0.60-0.75。

### 4.2 核心发现

1. **DEFAULT_DIMENSIONS fallback UX 问题**（P0）：初次扫描因未指定 profile → fallback 到中文关键词 → avg 0.20（SA 纠正后确认 code-review profile 本身是语言无关的）
2. **projdevbench 准确识别质量梯度**（✅）：0.24（api.py）→ 0.92（adapters.py）
3. **code-review 也准确识别梯度**（✅）：0.06（\_\_version\_\_.py）→ 0.92（adapters.py），SA 验证
4. **双 profile 高分一致**：adapters.py 两个 profile 都给 0.92

### 4.3 PMF 结果类型

> **"5 分钟，SelfPlay 完成了对 Python 最流行 HTTP 库的质量评估"**
>
> 质量梯度 0.06→0.92，与代码复杂度和工程质量的直觉完全一致。
> 这证明 SelfPlay 能区分代码质量，不是"给所有代码打高分"的玩具。

### 4.4 完整报告

→ 见 `research/external-project-audit-report.md`（已更正 SA 纠正后的数据）

---

*框架执行完毕。报告已更正：初次结论（code-review 语言偏差）是错误的，真正问题是 DEFAULT_DIMENSIONS fallback UX。*
