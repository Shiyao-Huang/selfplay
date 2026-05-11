from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from . import __version__
from .analytics import compute_analytics, suggest_dimensions
from .config import SelfPlayConfig
from .evaluator import HeuristicEvaluator
from .proposal import DimensionProposal, ProposalStore
from .storage import GenomeStore
from .supervisor import OEDMSupervisor
from .tree_export import export_markdown, export_mermaid, export_svg


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "dim": "\033[2m",
}


def color(text: str, style: str, enabled: bool = True) -> str:
    if not enabled:
        return text
    return f"{ANSI.get(style, '')}{text}{ANSI['reset']}"


def supports_color() -> bool:
    return os.environ.get("NO_COLOR") is None and os.environ.get("TERM") != "dumb"


def stage_line(icon: str, title: str, detail: str, use_color: bool) -> str:
    return f"{icon} {color(title, 'bold', use_color)} {color(detail, 'dim', use_color)}"


def cycle_payload(result: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "cycle": result.cycle,
        "runtime": result.old_image.runtime_adapter,
        "old_image": result.old_image.id,
        "new_image": result.new_image.id,
        "score_before": result.evaluation.score_before,
        "score_after": result.evaluation.score_after,
        "decision": result.decision,
        "profile_id": result.evaluation.profile_id,
        "profile_version": result.evaluation.profile_version,
        "events": [
            {"kind": e.kind, "runtime": e.runtime, "content": e.content[:120]}
            for e in result.events
        ],
    }
    # Include per-feature breakdown if available in task_result metadata.
    eval_meta = result.task_result.metadata.get("eval", {})
    if isinstance(eval_meta, dict) and "features" in eval_meta:
        payload["features"] = [
            f.to_dict() if hasattr(f, "to_dict") else f for f in eval_meta["features"]
        ]
    return payload


def result_payload(result: Any) -> dict[str, Any]:
    if hasattr(result, "cycles"):
        return {
            "goal": result.goal,
            "cycles": [cycle_payload(item) for item in result.cycles],
            "initial_image": result.initial_image.id,
            "final_image": result.final_image.id,
            "total_improvement": result.total_improvement,
            "stopped_early": result.stopped_early,
        }
    return cycle_payload(result)


def score_bar(score: float, width: int = 20) -> str:
    """Visual score bar: [████████░░░░░░░░] 0.68"""
    filled = int(round(score * width))
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {score:.2f}"


def print_cycle(result: Any, use_color: bool, total: int | None = None) -> None:
    score = f"{result.evaluation.score_before:.2f} → {result.evaluation.score_after:.2f}"
    label = f"Cycle {result.cycle}/{total}" if total else f"Cycle {result.cycle}"
    print(color(f"🔄 {label}", "cyan", use_color))
    print(stage_line("🎯", "Goal", result.task_result.task, use_color))
    print(stage_line("▶", "Run", result.old_image.runtime_adapter, use_color))
    print(stage_line("👁", "Observe", f"{len(result.events)} runtime events", use_color))
    errors = [e.content for e in result.events if e.kind == "error"]
    if errors:
        print(stage_line("⚠", "Error", "; ".join(errors)[:180], use_color))
    for attempt in result.rejected_attempts:
        print(stage_line("❌", f"Rejected (attempt {attempt['attempt']})", attempt["reason"], use_color))
    after = result.evaluation.score_after if result.evaluation.score_after is not None else result.evaluation.score_before
    bar = score_bar(after)
    if use_color:
        if after >= 0.9:
            bar = color(bar, "green", True)
        elif after >= 0.5:
            bar = color(bar, "yellow", True)
        else:
            bar = color(bar, "red", True)
    print(stage_line("📈", "Score", f"{score}  {bar}", use_color))
    # Feature breakdown mini-summary
    eval_meta = result.task_result.metadata.get("eval", {})
    features = eval_meta.get("features", []) if isinstance(eval_meta, dict) else []
    if features:
        passed = sum(1 for f in features if f.get("passed"))
        total_f = len(features)
        feat_summary = f"{passed}/{total_f} passed"
        print(stage_line("🏷", "Features", feat_summary, use_color))
    print(stage_line("🧬", "Mutate", result.decision[:120], use_color))
    print(stage_line("💾", "Persist", f"{result.old_image.id} → {result.new_image.id}", use_color))


def print_evolution(result: Any, use_color: bool) -> None:
    print(color(f"SelfPlay v{__version__} — Self-evolving Agent", "cyan", use_color))
    total = len(result.cycles)
    for item in result.cycles:
        print()
        print_cycle(item, use_color, total=total)
    print()
    print(color("📊 Evolution Summary", "green", use_color))
    path = []
    for item in result.cycles:
        after = item.evaluation.score_after
        after_value = after if after is not None else item.evaluation.score_before
        path.append(
            f"v{item.old_image.version}:"
            f"{item.evaluation.score_before:.2f}→{after_value:.2f}"
        )
    print(" → ".join(path))
    # Visual score trajectory
    scores = []
    for item in result.cycles:
        after = item.evaluation.score_after
        scores.append(after if after is not None else item.evaluation.score_before)
    if scores:
        for i, s in enumerate(scores):
            bar = score_bar(s, width=15)
            print(color(f"  v{i + 1} {bar}", "green" if s >= 0.9 else "yellow" if s >= 0.5 else "red", use_color))
    print(f"Total improvement: {result.total_improvement:+.2f}")
    if result.stopped_early:
        print(color("✅ Threshold reached — evolution stopped early", "green", use_color))
    print(f"Final prompt: {result.final_image.prompt[:180]}")


def print_status(summary: dict[str, Any], use_color: bool) -> None:
    latest = summary.get("latest_image") or {}
    print(color("SelfPlay status", "cyan", use_color))
    print(f"DB: {summary['db']}")
    print(f"Genomes: {summary['genomes']} | AgentImages: {summary['agent_images']}")
    print(f"Evaluations: {summary['evaluations']} | Runtime events: {summary['runtime_events']}")
    if latest:
        print(
            f"Latest: {latest.get('id')} "
            f"v{latest.get('version')} ({latest.get('runtime_adapter')})"
        )
        print(f"Prompt: {latest.get('prompt')}")


def print_history(records: list[dict[str, Any]], use_color: bool) -> None:
    print(color("SelfPlay evolution history", "cyan", use_color))
    if not records:
        print("No evaluations yet. Run: selfplay demo")
        return
    for item in records:
        score = f"{item['score_before']} → {item['score_after']}"
        print(f"cycle {item['cycle']} | {score} | {item['note']}")


def print_tree(images: list[Any], use_color: bool) -> None:
    print(color("SelfPlay AgentImage tree", "cyan", use_color))
    if not images:
        print("No AgentImages yet. Run: selfplay demo")
        return
    for image in reversed(images):
        parent = image.parent_id or "root"
        print(f"{parent} ──▶ {image.id} v{image.version} [{image.runtime_adapter}]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="selfplay",
        description="SelfPlay: a tiny self-improving Agent CLI demo.",
        epilog=(
            'examples:\n'
            '  selfplay demo\n'
            '  selfplay run "write a launch tweet"\n'
            '  selfplay history\n'
            '  selfplay init'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"selfplay {__version__}")
    parser.add_argument("--config", default="selfplay.yaml", help="path to SelfPlay YAML config")
    parser.add_argument("--db", default=None, help="SQLite database path; overrides config")
    parser.add_argument("--runtime", choices=["mock", "claude", "codex"], default=None)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--profile", default=None, help="evaluation profile id from config")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run SDK-neutral OEDM evolution cycles")
    run.add_argument("task", nargs="?", default="验证最小自指闭环")
    run.add_argument("--cycles", type=int, default=None, help="OEDM evolution cycles")
    run.add_argument("--json", action="store_true", help="print machine-readable JSON")
    demo = sub.add_parser("demo", help="show a 30-second self-improvement demo")
    demo.add_argument("task", nargs="?", default="用一句话介绍 SelfPlay")
    demo.add_argument("--cycles", type=int, default=None, help="OEDM evolution cycles")
    demo.add_argument("--json", action="store_true", help="print machine-readable JSON")
    init = sub.add_parser("init", help="create local SelfPlay config and data directory")
    init.add_argument("--force", action="store_true", help="overwrite selfplay.yaml")
    status = sub.add_parser("status", help="show store summary")
    status.add_argument("--json", action="store_true", help="print machine-readable JSON")
    image = sub.add_parser("image", help="show latest AgentImage genome")
    image.add_argument("--json", action="store_true", help="print machine-readable JSON")
    history = sub.add_parser("history", help="show recent evaluation history")
    history.add_argument("--limit", type=int, default=10)
    history.add_argument("--json", action="store_true", help="print machine-readable JSON")
    tree = sub.add_parser("tree", help="show AgentImage parent chain")
    tree.add_argument("--limit", type=int, default=10)
    tree.add_argument("--json", action="store_true", help="print machine-readable JSON")
    tree.add_argument("--format", choices=["text", "json", "mermaid", "markdown", "svg"],
                      default="text", help="tree output format (default: text)")
    tree.add_argument("--output", "-o", default=None, help="write to file instead of stdout")
    sub.add_parser("tui", help="run a lightweight terminal monitor")
    propose = sub.add_parser("propose-dimension", help="propose a new evaluation dimension")
    propose.add_argument("--id", required=True, help="dimension id")
    propose.add_argument("--label", required=True, help="human-readable label")
    propose.add_argument("--keywords", nargs="*", default=[], help="keywords to match")
    propose.add_argument("--pattern", default="", help="regex pattern")
    propose.add_argument("--weight", type=float, default=0.10, help="dimension weight")
    propose.add_argument("--rationale", default="", help="why this dimension is needed")
    propose.add_argument("--proposed-by", default="cli", help="proposer identifier")
    review = sub.add_parser("review-proposal", help="approve or reject a dimension proposal")
    review.add_argument("--id", required=True, help="proposal id to review")
    review.add_argument("--approve", action="store_true", help="approve the proposal")
    review.add_argument("--reject", action="store_true", help="reject the proposal")
    review.add_argument("--note", default="", help="review note")
    list_proposals = sub.add_parser("list-proposals", help="list dimension proposals")
    list_proposals.add_argument("--all", action="store_true", help="show all, not just pending")
    list_proposals.add_argument("--json", action="store_true", help="print machine-readable JSON")
    analytics = sub.add_parser("analytics", help="show evolution analytics and metrics")
    analytics.add_argument("--limit", type=int, default=50, help="number of evaluations to analyze")
    analytics.add_argument("--json", action="store_true", help="print machine-readable JSON")
    check = sub.add_parser("check", help="evaluate a source file using configured dimensions")
    check.add_argument("file", help="path to source file to evaluate")
    check.add_argument("--profile", default=None, help="evaluation profile id from config")
    check.add_argument("--json", action="store_true", help="print machine-readable JSON")
    suggest = sub.add_parser("suggest-dimensions", help="auto-suggest new evaluation dimensions (Strange Loop)")
    suggest.add_argument("--limit", type=int, default=50, help="evaluations to analyze")
    suggest.add_argument("--auto-submit", action="store_true", help="auto-submit suggestions as proposals")
    suggest.add_argument("--json", action="store_true", help="print machine-readable JSON")
    return parser


async def run_async(args: argparse.Namespace) -> None:
    use_color = supports_color() and not args.no_color
    config = SelfPlayConfig.load(
        args.config,
        overrides={
            "database": args.db,
            "runtime": args.runtime,
            "threshold": args.threshold,
            "cycles": getattr(args, "cycles", None),
            "profile": getattr(args, "profile", None),
        },
    )
    args.db = config.database
    args.runtime = config.runtime
    args.threshold = config.threshold
    args.cycles = config.cycles
    store = GenomeStore(args.db)
    if args.cmd == "init":
        data_dir = Path(args.db).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        config_path = Path(args.config)
        if config_path.exists() and not args.force:
            print(
                color(
                    "selfplay.yaml already exists; use --force to overwrite",
                    "yellow",
                    use_color,
                )
            )
            return
        config_path.write_text(config.to_yaml(), encoding="utf-8")
        print(color("SelfPlay initialized", "green", use_color))
        print("Created selfplay.yaml and data directory.")
        return
    if args.cmd == "status":
        summary = store.summary()
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print_status(summary, use_color)
        return
    if args.cmd == "image":
        image = store.latest_agent_image(args.runtime)
        payload = image.to_genome() if image else None
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if args.cmd == "history":
        records = store.recent_evaluations(args.limit)
        if args.json:
            print(json.dumps(records, ensure_ascii=False, indent=2))
        else:
            print_history(records, use_color)
        return
    if args.cmd == "tree":
        images = store.recent_agent_images(args.limit)
        fmt = getattr(args, "format", "text")
        if args.json or fmt == "json":
            output = json.dumps([x.to_genome() for x in images], ensure_ascii=False, indent=2)
        elif fmt == "mermaid":
            output = export_mermaid(images)
        elif fmt == "markdown":
            output = export_markdown(images)
        elif fmt == "svg":
            output = export_svg(images)
        else:
            output = None
            print_tree(images, use_color)
        if output is not None:
            out_path = getattr(args, "output", None)
            if out_path:
                Path(out_path).write_text(output, encoding="utf-8")
                print(color(f"Tree exported to {out_path}", "green", use_color))
            else:
                print(output)
        return
    if args.cmd == "propose-dimension":
        proposal_store = ProposalStore(Path(args.db).parent / "proposals.json")
        proposal = DimensionProposal(
            id=args.id,
            label=args.label,
            keywords=args.keywords,
            pattern=args.pattern,
            weight=args.weight,
            rationale=args.rationale,
            proposed_by=args.proposed_by,
        )
        proposal_store.submit(proposal)
        print(color(f"Proposal submitted: {proposal.id}", "green", use_color))
        return
    if args.cmd == "review-proposal":
        proposal_store = ProposalStore(Path(args.db).parent / "proposals.json")
        if args.approve:
            result = proposal_store.review(args.id, approved=True, note=args.note)
            if result:
                print(color(f"Approved: {result.id}", "green", use_color))
            else:
                print(color(f"Proposal not found or already reviewed: {args.id}", "red", use_color))
        elif args.reject:
            result = proposal_store.review(args.id, approved=False, note=args.note)
            if result:
                print(color(f"Rejected: {result.id}", "yellow", use_color))
            else:
                print(color(f"Proposal not found or already reviewed: {args.id}", "red", use_color))
        else:
            print(color("Use --approve or --reject", "yellow", use_color))
        return
    if args.cmd == "list-proposals":
        proposal_store = ProposalStore(Path(args.db).parent / "proposals.json")
        proposals = proposal_store.list_all() if args.all else proposal_store.list_pending()
        if args.json:
            print(json.dumps([p.to_dict() for p in proposals], ensure_ascii=False, indent=2))
        else:
            for p in proposals:
                icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(p.status, "?")
                print(f"{icon} {p.id} | {p.label} | weight={p.weight} | {p.status}")
        return
    if args.cmd == "analytics":
        analytics = compute_analytics(store, args.limit)
        if args.json:
            print(json.dumps(analytics.to_dict(), ensure_ascii=False, indent=2))
        else:
            c = analytics.convergence
            m = analytics.mutations
            print(color("📊 SelfPlay Evolution Analytics", "cyan", use_color))
            print()
            print(color("Convergence", "bold", use_color))
            print(f"  Cycles: {c.total_cycles} | To threshold: {c.cycles_to_threshold or 'never'}")
            print(f"  Improvement: {c.total_improvement:+.4f} | Rate: {c.improvement_rate:+.4f}/cycle")
            print(f"  Early stops: {c.early_stop_count}")
            print()
            print(color("Mutations", "bold", use_color))
            print(f"  Total: {m.total_mutations} | Accepted: {m.accepted_mutations} | Rejected: {m.rejected_mutations}")
            print(f"  Acceptance rate: {m.acceptance_rate:.1%}")
            print(f"  Avg gain/mutation: {m.avg_score_gain_per_mutation:+.4f}")
            print()
            if analytics.dimension_trends:
                print(color("Dimension Trends", "bold", use_color))
                for d in analytics.dimension_trends:
                    trend_icon = {"improving": "📈", "stable": "➡️", "declining": "📉"}.get(d.trend, "?")
                    bar = score_bar(d.pass_rate, width=10)
                    print(f"  {trend_icon} {d.label}: pass={d.pass_rate:.0%} avg={d.avg_score_contribution:.3f} {bar}")
            if analytics.score_trajectory:
                print()
                print(color("Score Trajectory", "bold", use_color))
                for i, s in enumerate(analytics.score_trajectory):
                    bar = score_bar(s, width=15)
                    print(f"  c{i + 1} {bar}")
        return
    if args.cmd == "suggest-dimensions":
        suggestions = suggest_dimensions(store, limit=args.limit)
        if args.auto_submit:
            proposal_store = ProposalStore(Path(args.db).parent / "proposals.json")
            from .proposal import DimensionProposal
            for s in suggestions:
                p = DimensionProposal(
                    id=s["id"],
                    label=s["label"],
                    keywords=s.get("keywords", []),
                    pattern=s.get("pattern", ""),
                    weight=s.get("weight", 0.10),
                    rationale=s.get("rationale", ""),
                    proposed_by="strange_loop",
                )
                proposal_store.submit(p)
        if args.json:
            print(json.dumps(suggestions, ensure_ascii=False, indent=2))
        else:
            print(color("🔄 SelfPlay Strange Loop — Dimension Suggestions", "cyan", use_color))
            if not suggestions:
                print("  No suggestions. System is evolving well!")
            for s in suggestions:
                icon = {"strange_loop:declining_dimension": "📉",
                        "strange_loop:zero_pass_dimension": "❓",
                        "strange_loop:low_convergence": "🔄"}.get(s.get("source", ""), "💡")
                print(f"  {icon} {s['label']} (weight={s.get('weight', 0.1)})")
                print(f"     {s['rationale'][:120]}")
            if args.auto_submit and suggestions:
                print(color(f"  {len(suggestions)} proposals auto-submitted", "green", use_color))
        return
    if args.cmd == "check":
        file_path = Path(args.file)
        if not file_path.exists():
            print(color(f"File not found: {args.file}", "red", use_color))
            return
        content = file_path.read_text(encoding="utf-8")
        profile = config.resolve_profile(args.runtime) if config.profiles else None
        dims = profile.resolve_dimensions(config.dimensions) if profile else config.dimensions
        evaluator = HeuristicEvaluator(dimensions=dims or None)
        eval_result = evaluator.evaluate_text(task=f"code review: {file_path.name}", output=content)
        if args.json:
            payload = {
                "file": str(file_path),
                "score": eval_result.score,
                "features": [f.to_dict() for f in eval_result.features],
                "strengths": eval_result.strengths,
                "weaknesses": eval_result.weaknesses,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(color(f"SelfPlay code review: {file_path.name}", "cyan", use_color))
            bar = score_bar(eval_result.score)
            if use_color:
                bar = color(bar, "green" if eval_result.score >= 0.7 else "yellow" if eval_result.score >= 0.4 else "red", True)
            print(f"  Score: {eval_result.score:.2f}  {bar}")
            print()
            for f in eval_result.features:
                icon = "✅" if f.passed else "❌"
                w = f"({f.effective_weight:.0%})"
                ev = f" — {f.evidence}" if f.evidence else ""
                print(f"  {icon} {f.label} {w}{ev}")
            if eval_result.weaknesses:
                print()
                print(color("Weaknesses:", "yellow", use_color))
                for w in eval_result.weaknesses:
                    print(f"  • {w}")
        return

    supervisor = OEDMSupervisor(
        store,
        threshold=args.threshold,
        max_prompt_length=config.max_prompt_length,
        dimensions=config.dimensions or None,
        profile=config.resolve_profile(args.runtime) if config.profiles else None,
    )
    if args.cmd in {"demo", "tui"} and not getattr(args, "json", False):
        print(color("SelfPlay demo: watch an Agent improve itself", "cyan", use_color))
        print(stage_line("1", "Start", "seed AgentImage from disk", use_color))
        print(stage_line("2", "Loop", "run → observe → score → mutate", use_color))
    task = getattr(args, "task", "TUI monitor smoke test")
    cycles = 1 if args.cmd == "tui" else args.cycles
    result = await supervisor.run_evolution(task, cycles=cycles, runtime_adapter=args.runtime)
    if getattr(args, "json", False):
        print(json.dumps(result_payload(result), ensure_ascii=False, indent=2))
    else:
        print_evolution(result, use_color)
        if args.cmd == "demo":
            print(
                color(
                    "Try next: selfplay history | selfplay tree | selfplay tui",
                    "green",
                    use_color,
                )
            )


def main() -> None:
    args = build_parser().parse_args()
    asyncio.run(run_async(args))


if __name__ == "__main__":
    main()
