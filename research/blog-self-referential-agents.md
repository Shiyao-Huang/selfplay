# From Gödel to Agent: How Self-Referential Systems Enable Self-Improving AI

> **类型**：技术博客（面向 Hacker News / dev.to / Medium）
> **日期**：2026-05-09
> **作者**：SelfPlay Team
> **目标**：Show HN 配套深度技术文章，提供理论背书

---

## The Problem with Fixed Agents

Every AI agent today has a fixed set of instructions. You write a system prompt, configure some tools, and the agent executes. It might retry, reflect, or chain thoughts — but the rules never change.

The prompt is always the same. The strategy is always the same. The agent is always the same.

This is fundamentally limited. In any complex system, the ability to improve *the rules themselves* — not just follow them better — is what separates adaptation from execution.

**What if an agent could rewrite its own instructions?**

Not randomly. Not chaotically. But through a structured loop where it observes itself, evaluates its performance, decides what to change, and makes the change — then starts again, better than before.

This isn't science fiction. The mathematics of self-reference — developed across a century by some of the deepest thinkers in logic and computation — gives us a precise framework for understanding how systems can meaningfully improve themselves.

---

## Three Mathematical Insights That Make Self-Improving Agents Possible

### Insight 1: Gödel's Encoding — A System Can Describe Itself

In 1931, Kurt Gödel proved something shocking: any sufficiently powerful formal system contains statements that reference their own provability. The key mechanism was **Gödel numbering** — a way to assign a unique number to every mathematical statement, including statements *about* those numbers.

This created something unprecedented: a formal system that could "talk about itself."

**What this means for agents**: An agent's configuration — its system prompt, tool selection, evaluation criteria, and behavior rules — is its "Gödel encoding." If the agent can read this encoding, it can reason about its own behavior. And if it can *modify* this encoding, it can change its own rules.

The self-referential entry point is simple: **make the agent's instructions readable and writable by the agent itself.**

### Insight 2: Von Neumann's Blueprint — Data and Program Are the Same Thing

In the 1940s, John von Neumann designed a theoretical machine that could reproduce itself. The machine had four components:

1. **Constructor (A)**: Builds any machine from a blueprint
2. **Copier (B)**: Copies the blueprint itself
3. **Blueprint (I)**: A description of the complete machine (including A, B, and I)
4. **Controller (C)**: Coordinates A and B

The critical insight: the blueprint I is simultaneously **data** (it gets copied) and **program** (it instructs construction). This duality is what makes self-reproduction possible.

**What this means for agents**: An agent's genome (its self-description file) plays both roles:
- **As data**: It's evaluated, scored, compared against goals
- **As program**: It governs how the agent behaves

When the agent modifies its genome, it's changing both the description *and* the behavior simultaneously. This is the Von Neumann duality applied to AI agents.

### Insight 3: Hofstadter's Strange Loop — Hierarchies Must Tangle

Douglas Hofstadter argued that consciousness emerges from "Strange Loops" — circular relationships between different levels of a system, where moving "up" through levels eventually brings you back to where you started.

The key property is a **tangled hierarchy**: the levels aren't cleanly separated. High-level patterns can influence low-level implementation, and low-level states can determine high-level behavior.

**What this means for agents**: A self-improving agent needs at least two tangled levels:
- **Task level**: Executing tasks, producing results
- **Meta level**: Evaluating task-level performance, modifying task-level rules

The "strangeness" comes from the fact that the meta level is *also* executing a task (the task of self-improvement), and its own rules are subject to modification. The hierarchy tangles.

---

## The OEDM Loop: A Minimal Self-Referential Cycle

Combining these three insights, we arrive at a minimal four-phase cycle that any self-improving system must implement:

```
┌──────────┐         ┌──────────┐
│ Observe  │────────→│ Evaluate │
│          │         │          │
│ Watch    │         │ Score    │
│ results  │         │ quality  │
└──────────┘         └────┬─────┘
     ↑                     │
     │                     ▼
┌────┴─────┐         ┌──────────┐
│ Modify   │←────────│ Decide   │
│          │         │          │
│ Rewrite  │         │ Choose   │
│ genome   │         │ changes  │
└──────────┘         └──────────┘
```

1. **Observe**: The agent watches its own execution results — what it did, how long it took, what went wrong
2. **Evaluate**: It scores its performance against defined criteria (correctness, efficiency, completeness)
3. **Decide**: It determines what to improve (add error handling, optimize complexity, restructure logic)
4. **Modify**: It rewrites its own genome — the self-description that governs its behavior

After modification, the cycle restarts with the new genome. The agent is now a slightly different agent, executing the same task with improved rules.

**This is the minimal closed loop of self-reference.** Everything else — version chains, rollback, fitness thresholds — is engineering built on top of this fundamental cycle.

---

## The Genome: Where Data Meets Program

The genome is the agent's self-description. In SelfPlay, it's a structured document that includes:

```yaml
# SelfPlay Genome v3
identity:
  name: "code-refactor-agent"
  version: 3
  parent: "genome-v2"

capabilities:
  - "read and analyze code"
  - "suggest refactoring strategies"
  - "write improved code"

strategies:
  - "always check for edge cases before refactoring"
  - "prefer readability over cleverness"
  - "add tests for any new code paths"      # added in v2
  - "check time complexity of hot paths"    # added in v3

evaluation_criteria:
  correctness: 0.4
  readability: 0.3
  performance: 0.2
  error_handling: 0.1                       # added in v2

self_modification_rules:
  min_score_threshold: 0.7
  max_changes_per_cycle: 3
  require_improvement: true                 # reject degrading changes
```

Notice the duality: this file is simultaneously:
- **Data** that gets evaluated ("did the strategies improve the score?")
- **Program** that governs behavior ("follow these strategies when executing tasks")

When the OEDM loop runs, the genome is the object being modified *and* the subject doing the modification. It's Gödel numbering in practice.

---

## The "Soft Prover": Replacing Formal Proofs with LLM Judgment

Jürgen Schmidhuber's original Gödel Machine (2003) had a brilliant but impractical requirement: the agent should only modify itself if it can *formally prove* the modification is an improvement. This guarantees safety but is computationally intractable for real systems.

SelfPlay takes a different approach inspired by Gödel Agent (2024) and Darwin Gödel Machine (2025): **use the LLM itself as a "soft prover."**

Instead of formal proof, the agent:
1. Generates a proposed modification
2. The LLM evaluates: "Would this modification improve performance?"
3. If the LLM judges yes, apply the modification
4. The next OEDM cycle *measures* whether the judgment was correct
5. If the score improved, keep the change. If not, revert.

This is empirical validation with LLM-guided search, rather than formal proof. It trades theoretical guarantees for practical feasibility — and it works.

---

## What Makes This Different from Prompt Chaining?

This is the most common question, and it deserves a precise answer.

**Prompt chaining**: Fixed prompts → Fixed sequence → Fixed rules → Retries with same instructions

**Self-referential evolution**: Mutable genome → Dynamic sequence → Evolving rules → Retries with *improved* instructions

The critical difference is that in a self-referential system, the *rules themselves* are in the improvement loop. It's not "try harder with the same strategy" — it's "discover a better strategy and try that instead."

Formally:

```
Prompt chaining:     task(P) → result(R) → retry(P, R)
Self-referential:    task(P) → result(R) → modify(P, R) → P' → task(P')
```

The second form has an additional degree of freedom: the prompt itself can change. This is what Hofstadter would call the "tangled hierarchy" — the meta level (modifying P) and the task level (executing P) are not cleanly separated.

---

## Safety: Preventing Self-Destruction

Self-modification sounds dangerous. An agent that rewrites its own rules could break itself. Three mechanisms prevent this:

1. **Fitness threshold**: Modifications that reduce the evaluation score below a threshold are automatically rejected. This is inspired by Darwin GM's evolutionary selection.

2. **Version chain with rollback**: Every genome version is stored in a version chain (like Git). If a modification causes problems, the agent can revert to any previous version.

3. **Bounded modification**: The genome specifies rules for its own modification — maximum changes per cycle, required improvement, protected sections. These rules create a "safe envelope" for self-modification.

These don't provide formal safety guarantees (Gödel's theorem suggests perfect self-monitoring is impossible). But they provide practical safety sufficient for real-world use.

---

## Try It Yourself

```bash
pip install selfplay
selfplay demo
```

This runs a complete OEDM evolution cycle in ~30 seconds using mock mode. You'll see an agent start at score 3/10 and evolve to 9/10 across three iterations — teaching itself to add error handling, optimize complexity, and write cleaner code.

The mock mode demonstrates the mechanism without an LLM call. For real self-evolution:

```bash
selfplay --runtime claude run "your task here"
```

Watch your agent's genome evolve. Each version is stored, each improvement is logged, and you can always roll back.

---

## What's Next

SelfPlay is at an early but functional stage. The OEDM loop works, genome versioning works, and the mock demo shows the full cycle in 30 seconds.

The open questions are the most interesting part:
- **Convergence**: Do self-referential loops always converge, or can they oscillate?
- **Complexity threshold**: How complex must an initial genome be before meaningful self-improvement is possible?
- **Meta-evolution**: Can the OEDM loop itself be evolved? (Can the agent improve *how it improves*?)
- **Multi-agent co-evolution**: What happens when multiple self-improving agents interact?

If these questions interest you, we'd love your help. The genome design, evaluation criteria, and runtime adapters are all areas where community input could make SelfPlay significantly better.

**GitHub**: [SelfPlay Repository](https://github.com/shiyao-huang/selfplay)
**Docs**: [selfplay.dev](https://selfplay.dev)

---

*Built with self-reference and the ghosts of Gödel, Von Neumann, and Hofstadter.*
