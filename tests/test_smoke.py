from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from selfplay.cli import build_parser
from selfplay.storage import GenomeStore
from selfplay.supervisor import OEDMSupervisor


class SmokeTests(unittest.TestCase):
    def test_parser_has_product_commands(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("demo", help_text)
        self.assertIn("history", help_text)
        self.assertIn("tree", help_text)
        self.assertIn("--version", help_text)

    def test_mock_cycle_persists_agent_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "selfplay.sqlite"
            store = GenomeStore(db)
            result = asyncio.run(OEDMSupervisor(store).run_cycle("hello", runtime_adapter="mock"))
            self.assertGreaterEqual(result.evaluation.score_before, 0.0)
            self.assertIsNotNone(store.latest_agent_image("mock"))
            self.assertGreaterEqual(len(store.recent_evaluations()), 1)

    def test_mock_evolution_scores_change_across_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "selfplay.sqlite"
            store = GenomeStore(db)
            result = asyncio.run(OEDMSupervisor(store).run_evolution("写一个快速排序", cycles=3))
            scores = [item.evaluation.score_before for item in result.cycles]
            self.assertGreaterEqual(len(scores), 2)
            self.assertGreater(max(scores), min(scores))
            self.assertGreater(result.total_improvement, 0.0)


if __name__ == "__main__":
    unittest.main()
