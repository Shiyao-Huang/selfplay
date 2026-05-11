from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import AgentGenome, AgentImage, EvaluationRecord, RuntimeName, utc_now

SCHEMA = """
create table if not exists genomes (
  id text primary key,
  version integer not null,
  instructions text not null,
  parent_id text,
  created_at text not null
);
create table if not exists agent_images (
  id text primary key,
  version integer not null,
  runtime_adapter text not null,
  genome_json text not null,
  parent_id text,
  created_at text not null
);
create table if not exists evaluations (
  id integer primary key autoincrement,
  cycle integer not null,
  stage text not null,
  genome_id text not null,
  score_before real not null,
  score_after real,
  note text not null,
  created_at text not null
);
create table if not exists runtime_events (
  id integer primary key autoincrement,
  cycle integer not null,
  kind text not null,
  runtime text not null,
  content text not null,
  metadata_json text not null,
  created_at text not null
);
"""


class GenomeStore:
    def __init__(self, path: str | Path = "data/selfplay.sqlite") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)
        self._ensure_features_column()
        self._ensure_profile_columns()
        self.conn.commit()

    def _ensure_features_column(self) -> None:
        """Idempotent ALTER TABLE for features_json column."""
        cursor = self.conn.execute("PRAGMA table_info(evaluations)")
        columns = {row[1] for row in cursor.fetchall()}
        if "features_json" not in columns:
            self.conn.execute("ALTER TABLE evaluations ADD COLUMN features_json TEXT DEFAULT '[]'")

    def _ensure_profile_columns(self) -> None:
        """Idempotent ALTER TABLE for profile_id and profile_version columns."""
        cursor = self.conn.execute("PRAGMA table_info(evaluations)")
        columns = {row[1] for row in cursor.fetchall()}
        if "profile_id" not in columns:
            self.conn.execute("ALTER TABLE evaluations ADD COLUMN profile_id TEXT")
        if "profile_version" not in columns:
            self.conn.execute("ALTER TABLE evaluations ADD COLUMN profile_version INTEGER")

    def save_genome(self, genome: AgentGenome) -> None:
        self.conn.execute(
            "insert or replace into genomes values (?, ?, ?, ?, ?)",
            (genome.id, genome.version, genome.instructions, genome.parent_id, genome.created_at),
        )
        self.conn.commit()

    def save_agent_image(self, image: AgentImage) -> None:
        genome_json = json.dumps(image.to_genome(), ensure_ascii=False, sort_keys=True)
        self.conn.execute(
            """insert or replace into agent_images
            (id, version, runtime_adapter, genome_json, parent_id, created_at)
            values (?, ?, ?, ?, ?, ?)""",
            (image.id, image.version, image.runtime_adapter, genome_json, image.parent_id, image.created_at),
        )
        self.save_genome(AgentGenome(
            id=image.id.replace("image", "genome", 1),
            version=image.version,
            instructions=image.prompt,
            parent_id=image.parent_id,
            created_at=image.created_at,
        ))

    def save_evaluation(self, record: EvaluationRecord, features: list[dict] | None = None) -> None:
        features_json = json.dumps(features or [], ensure_ascii=False)
        self.conn.execute(
            """insert into evaluations
            (cycle, stage, genome_id, score_before, score_after, note, created_at, features_json,
             profile_id, profile_version)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.cycle,
                record.stage,
                record.genome_id,
                record.score_before,
                record.score_after,
                record.note,
                record.created_at,
                features_json,
                record.profile_id,
                record.profile_version,
            ),
        )
        self.conn.commit()

    def save_runtime_event(self, cycle: int, kind: str, runtime: str, content: str, metadata: dict) -> None:
        self.conn.execute(
            """insert into runtime_events
            (cycle, kind, runtime, content, metadata_json, created_at)
            values (?, ?, ?, ?, ?, ?)""",
            (cycle, kind, runtime, content, json.dumps(metadata, ensure_ascii=False), utc_now()),
        )
        self.conn.commit()

    def latest_genome(self) -> AgentGenome | None:
        row = self.conn.execute(
            "select id, version, instructions, parent_id, created_at from genomes order by version desc limit 1"
        ).fetchone()
        if not row:
            return None
        return AgentGenome(id=row[0], version=row[1], instructions=row[2], parent_id=row[3], created_at=row[4])

    def latest_agent_image(self, runtime_adapter: RuntimeName | None = None) -> AgentImage | None:
        if runtime_adapter:
            row = self.conn.execute(
                """select genome_json from agent_images
                where runtime_adapter = ? order by version desc limit 1""",
                (runtime_adapter,),
            ).fetchone()
        else:
            row = self.conn.execute(
                "select genome_json from agent_images order by version desc limit 1"
            ).fetchone()
        if row:
            return AgentImage.from_genome(json.loads(row[0]))
        if runtime_adapter:
            return None
        legacy = self.latest_genome()
        return legacy.to_agent_image("mock") if legacy else None

    def recent_agent_images(self, limit: int = 10) -> list[AgentImage]:
        rows = self.conn.execute(
            "select genome_json from agent_images order by version desc, created_at desc limit ?",
            (limit,),
        ).fetchall()
        return [AgentImage.from_genome(json.loads(row[0])) for row in rows]

    def recent_evaluations(self, limit: int = 10) -> list[dict[str, object]]:
        rows = self.conn.execute(
            """select cycle, stage, genome_id, score_before, score_after, note, created_at, features_json,
               profile_id, profile_version
            from evaluations order by id desc limit ?""",
            (limit,),
        ).fetchall()
        return [
            {
                "cycle": row[0],
                "stage": row[1],
                "genome_id": row[2],
                "score_before": row[3],
                "score_after": row[4],
                "note": row[5],
                "created_at": row[6],
                "features": json.loads(row[7] or "[]"),
                "profile_id": row[8],
                "profile_version": row[9],
            }
            for row in rows
        ]

    def summary(self) -> dict[str, object]:
        genomes = self.conn.execute("select count(*) from genomes").fetchone()[0]
        images = self.conn.execute("select count(*) from agent_images").fetchone()[0]
        evals = self.conn.execute("select count(*) from evaluations").fetchone()[0]
        events = self.conn.execute("select count(*) from runtime_events").fetchone()[0]
        latest_image = self.latest_agent_image()
        latest = self.latest_genome()
        return {
            "db": str(self.path),
            "genomes": genomes,
            "agent_images": images,
            "evaluations": evals,
            "runtime_events": events,
            "latest_image": latest_image.to_genome() if latest_image else None,
            "latest": latest.__dict__ if latest else None,
        }
