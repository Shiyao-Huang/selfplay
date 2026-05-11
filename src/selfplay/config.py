from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .models import DEFAULT_MAX_PROMPT_LENGTH


@dataclass
class EvaluationDimension:
    """A single configurable evaluation dimension."""

    id: str
    label: str = ""
    pattern: str = ""
    keywords: list[str] = field(default_factory=list)
    weight: float = 0.10
    enabled: bool = True
    type: str = "keyword"  # "keyword" | "pattern" | "length"
    min_length: int = 80  # only used when type="length"


@dataclass
class EvaluationProfile:
    """Named set of evaluation dimensions for a specific runtime context."""

    id: str
    version: int = 1
    dimensions: list[EvaluationDimension] = field(default_factory=list)

    def resolve_dimensions(
        self, fallback: list[EvaluationDimension] | None = None
    ) -> list[EvaluationDimension]:
        if self.dimensions:
            return self.dimensions
        return fallback or []


@dataclass
class SelfPlayConfig:
    runtime: str = "mock"
    threshold: float = 0.9
    database: str = "data/selfplay.sqlite"
    cycles: int = 3
    max_prompt_length: int = DEFAULT_MAX_PROMPT_LENGTH
    dimensions: list[EvaluationDimension] = field(default_factory=list)
    profiles: dict[str, EvaluationProfile] = field(default_factory=dict)
    profile: str | None = None  # selected profile id

    @classmethod
    def default(cls) -> "SelfPlayConfig":
        return cls()

    @classmethod
    def load(
        cls,
        path: str | Path = "selfplay.yaml",
        overrides: dict[str, Any] | None = None,
    ) -> "SelfPlayConfig":
        data = asdict(cls.default())
        del data["dimensions"]
        config_path = Path(path)
        raw_text = ""
        if config_path.exists():
            raw_text = config_path.read_text(encoding="utf-8")
            data.update(_parse_flat_yaml(raw_text))
        for key, value in (overrides or {}).items():
            if value is not None and key in data:
                data[key] = value
        dimensions = _parse_dimensions(raw_text) if raw_text else []
        profiles = _parse_profiles(raw_text) if raw_text else {}
        profile_override = (overrides or {}).pop("profile", None)
        return cls(
            runtime=str(data["runtime"]),
            threshold=float(data["threshold"]),
            database=str(data["database"]),
            cycles=int(data["cycles"]),
            max_prompt_length=int(data["max_prompt_length"]),
            dimensions=dimensions,
            profiles=profiles,
            profile=profile_override,
        )

    def to_yaml(self) -> str:
        return (
            f"runtime: {self.runtime}\n"
            f"threshold: {self.threshold}\n"
            f"database: {self.database}\n"
            f"cycles: {self.cycles}\n"
            f"max_prompt_length: {self.max_prompt_length}\n"
        )

    def resolve_profile(self, runtime: str = "") -> EvaluationProfile | None:
        """Return the profile matching runtime or explicit --profile override."""
        if self.profile and self.profile in self.profiles:
            return self.profiles[self.profile]
        rt = runtime or self.runtime
        if rt in self.profiles:
            return self.profiles[rt]
        # fallback: first profile with matching key or "default"
        for key in (rt, "default"):
            if key in self.profiles:
                return self.profiles[key]
        return None


def _parse_dimensions(text: str) -> list[EvaluationDimension]:
    """Parse evaluation.dimensions from YAML. Requires pyyaml optional dependency."""
    try:
        import yaml
    except ImportError:
        return []
    try:
        data = yaml.safe_load(text) or {}
    except Exception:
        return []
    dims = data.get("evaluation", {}).get("dimensions", [])
    result: list[EvaluationDimension] = []
    for d in dims:
        if not isinstance(d, dict) or not d.get("id"):
            continue
        if not d.get("enabled", True):
            continue
        result.append(EvaluationDimension(
            id=str(d["id"]),
            label=str(d.get("label", d["id"])),
            pattern=str(d.get("pattern", "")),
            keywords=list(d.get("keywords", [])),
            weight=float(d.get("weight", 0.10)),
            enabled=True,
            type=str(d.get("type", "keyword" if d.get("keywords") else ("pattern" if d.get("pattern") else "keyword"))),
            min_length=int(d.get("min_length", 80)),
        ))
    return result


def _parse_profiles(text: str) -> dict[str, EvaluationProfile]:
    """Parse evaluation.profiles from YAML. Each profile is keyed by runtime name."""
    try:
        import yaml
    except ImportError:
        return {}
    try:
        data = yaml.safe_load(text) or {}
    except Exception:
        return {}
    profiles_raw = data.get("evaluation", {}).get("profiles", {})
    if not isinstance(profiles_raw, dict):
        return {}
    result: dict[str, EvaluationProfile] = {}
    for key, val in profiles_raw.items():
        if not isinstance(val, dict):
            continue
        dims_raw = val.get("dimensions", [])
        dims = []
        for d in dims_raw:
            if not isinstance(d, dict) or not d.get("id"):
                continue
            if not d.get("enabled", True):
                continue
            dims.append(EvaluationDimension(
                id=str(d["id"]),
                label=str(d.get("label", d["id"])),
                pattern=str(d.get("pattern", "")),
                keywords=list(d.get("keywords", [])),
                weight=float(d.get("weight", 0.10)),
                enabled=True,
                type=str(d.get("type", "keyword" if d.get("keywords") else ("pattern" if d.get("pattern") else "keyword"))),
                min_length=int(d.get("min_length", 80)),
            ))
        profile_id = str(val.get("id", key))
        profile_version = int(val.get("version", 1))
        result[key] = EvaluationProfile(id=profile_id, version=profile_version, dimensions=dims)
    return result


def _parse_flat_yaml(text: str) -> dict[str, Any]:
    """Parse the tiny flat YAML subset SelfPlay writes; keeps mock mode dependency-free."""
    result: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = _coerce_scalar(value.strip().strip('"\''))
    return result


def _coerce_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
