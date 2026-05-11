# SelfPlay 发布执行 Checklist & Timeline

> 基于 `research/show-hn-launch-strategy.md` 制定
> 状态：等待 Phase 1 完成 + Demo 打磨

---

## Phase 0: 阻塞项（必须先完成）

- [ ] **Phase 1 实现完成** — Builder 正在按 `docs/phase1-implementation-spec.md` 实现 Evaluator + Mutator + 多轮进化
- [ ] **`selfplay demo` 在干净环境可运行** — pip install + demo 30秒无报错
- [ ] **Demo 展示真实自进化** — 不是硬编码表演，score 确实在改善
- [ ] **GitHub repo 创建** — 用户名确认后 push 代码
- [ ] **README.md 首屏打磨** — ASCII 架构图 + Demo GIF

## Phase 1: 预发布准备（T-7d ~ T-1d）

### T-7d: 基础设施
- [ ] GitHub repo 创建，push 全部代码
- [ ] LICENSE (MIT) 确认
- [ ] pyproject.toml GitHub 用户名替换
- [ ] README 中 GitHub 链接替换
- [ ] 首次 `pip install -e . && selfplay demo` 全流程验证

### T-5d: 内容准备
- [ ] 终端录屏 GIF（v1→v2→v3 进化过程，<30秒）
- [ ] README 首屏 GIF 嵌入
- [ ] Show HN 正文最终定稿（基于 `research/show-hn-launch-strategy.md` §2）
- [ ] 评论区预制回答 5 条就绪（§3.1 Q1-Q5）
- [ ] 种子评论 3 条分配给团队成员

### T-3d: 渠道准备
- [ ] HN 账号 karma ≥ 50（如不够提前养号）
- [ ] Twitter/X 账号就绪
- [ ] Reddit 账号就绪（r/LocalLLaMA, r/SideProject）
- [ ] V2EX 账号就绪
- [ ] 即刻账号就绪

### T-1d: 最终检查
- [ ] 干净虚拟环境测试 `pip install selfplay && selfplay demo`
- [ ] 所有链接可访问
- [ ] 团队成员确认发布时间并在线
- [ ] 种子评论作者确认参与

## Phase 2: 发布日（T+0）

### 最佳窗口：周二或周三，美东 8:30-9:30 AM

| 时间 (ET) | 行动 | 负责人 |
|-----------|------|--------|
| 8:30 AM | 发布 Show HN | 主作者 |
| 8:30-9:00 | Twitter/X 发帖（GIF + 一句话） | 社交负责人 |
| 8:30-9:00 | 种子评论 1-3 投入 | 团队成员 |
| 9:00-9:30 | 回复每条评论 | 主作者 |
| 10:30 AM | Reddit r/LocalLLaMA 技术帖 | +2h |
| 12:30 PM | Reddit r/SideProject 故事帖 | +4h |
| 全天 | 持续回复 HN 评论（0-30min 内响应） | 主作者 |

## Phase 3: 发布后跟进（T+1d ~ T+7d）

| 时间 | 行动 |
|------|------|
| T+12h | V2EX 中文技术帖 + Show HN 链接 |
| T+12h | 即刻短视频（Agent 进化过程） |
| T+24h | 总结 HN 关键反馈，开 GitHub issue |
| T+48h | 评估 star 数 vs 目标（最低 200，理想 500+） |
| T+7d | 发布 "HN 反馈跟进" 博客/issue |

## 成功指标

| 指标 | 最低 | 理想 |
|------|------|------|
| Show HN 首页停留 | 4h | 24h |
| Upvotes | 100 | 300+ |
| 评论数 | 30 | 80+ |
| GitHub Stars (48h) | 200 | 500+ |

## 风险预案速查

| 风险 | 响应 |
|------|------|
| "又一个 AI wrapper" | 展示 genome 文件结构 + 自修改技术深度 |
| "mock mode 不是真的" | 准备 Claude runtime 实时演示视频 |
| 被比 AutoGPT | 预制回答：AutoGPT=repeated execution, SelfPlay=evolution |
| 安全性质疑 | 展示 rollback + drift-prevention |
| 冷启动 <50 upvotes | 种子评论 + Twitter 引流 |

---

## 当前状态

**阻塞**: Phase 1 实现 + Demo 打磨 + GitHub 用户名
**就绪物料**: Show HN 策略文档、竞品拆解、技术博客草稿、本 checklist
**下一步**: 等 Builder 完成 Phase 1 → 验证 demo → 启动 Phase 1 预发布准备
