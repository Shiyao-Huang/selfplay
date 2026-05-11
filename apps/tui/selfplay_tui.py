"""Phase 0 Textual TUI.

Run:
  PYTHONPATH=src python apps/tui/selfplay_tui.py

If Textual is not installed, this falls back to one CLI-compatible OEDM cycle.
"""
from __future__ import annotations

import asyncio

from selfplay.storage import GenomeStore
from selfplay.supervisor import OEDMSupervisor


async def run_once() -> dict:
    store = GenomeStore()
    result = await OEDMSupervisor(store).run_cycle("TUI smoke test", runtime_adapter="mock")
    return {
        "image": f"{result.old_image.id} -> {result.new_image.id}",
        "score": f"{result.evaluation.score_before} -> {result.evaluation.score_after}",
        "decision": result.decision,
        "events": len(result.events),
        "runtime": result.old_image.runtime_adapter,
        "stages": "Goal → Run → Observe → Score → Reflect → Mutate → Persist",
    }


def fallback() -> None:
    data = asyncio.run(run_once())
    rows = [
        ("Runtime", data["runtime"]),
        ("AgentImage", data["image"]),
        ("Score", data["score"]),
        ("Decision", data["decision"]),
        ("Events", str(data["events"])),
        ("Stages", data["stages"]),
    ]
    print("┌─ SelfPlay OEDM Monitor ─────────────────────────────")
    for label, value in rows:
        print(f"│ {label:<10} {value}")
    print("└────────────────────────────────────────────────────")


try:
    from textual.app import App, ComposeResult
    from textual.widgets import Footer, Header, Static
except Exception:  # pragma: no cover - optional dependency
    App = None  # type: ignore


if App is not None:
    class SelfPlayApp(App):
        CSS = """
        Screen { background: #101820; color: #f2f7ff; }
        Static { padding: 1; border: round #2dd4bf; margin: 1; }
        #headline { text-style: bold; color: #7dd3fc; }
        """

        def compose(self) -> ComposeResult:
            yield Header()
            yield Static("SelfPlay OEDM Monitor — self-improving Agent demo", id="headline")
            yield Static("Loading one mock cycle...", id="status")
            yield Footer()

        async def on_mount(self) -> None:
            status = self.query_one("#status", Static)
            data = await run_once()
            status.update(
                "\n".join([
                    f"AgentImage: {data['image']}",
                    f"Score: {data['score']}",
                    f"Decision: {data['decision']}",
                    f"Events: {data['events']}",
                    f"Stages: {data['stages']}",
                ])
            )

    SelfPlayApp().run()
else:
    fallback()
