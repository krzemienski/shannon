"""scripts/harness/lib.py — shared harness utilities."""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)

HARNESS_DIR = Path(__file__).resolve().parent
REPO = HARNESS_DIR.parent.parent
BENCHMARKS_DIR = HARNESS_DIR / "benchmarks"
EVIDENCE_DIR = REPO / ".planning" / "phases" / "05-harnesses" / "evidence"


@dataclass
class BenchmarkSpec:
    id: str
    pillar: str
    goal: str
    setup: list[str] = field(default_factory=list)
    action: dict = field(default_factory=dict)
    expected_evidence: list[str] = field(default_factory=list)
    gate_criteria: list[str] = field(default_factory=list)
    runner: str = "both"  # sdk | tmux | both
    source_path: Optional[str] = None


@dataclass
class Verdict:
    benchmark_id: str
    runner: str
    status: str  # PASS | FAIL | DRY_RUN_OK | SKIP
    evidence_path: Optional[str] = None
    detail: str = ""

    def to_dict(self):
        return asdict(self)


def load_benchmarks() -> list[BenchmarkSpec]:
    """Load every benchmark YAML from benchmarks/."""
    specs = []
    for p in sorted(BENCHMARKS_DIR.glob("*.yml")):
        data = yaml.safe_load(p.read_text())
        if not isinstance(data, dict):
            continue
        data["source_path"] = str(p.relative_to(REPO))
        specs.append(BenchmarkSpec(**data))
    return specs


def validate_benchmark(spec: BenchmarkSpec) -> list[str]:
    """Return list of validation issues; empty = valid."""
    issues = []
    if not spec.id:
        issues.append("missing id")
    if not spec.pillar:
        issues.append("missing pillar")
    if not spec.goal:
        issues.append("missing goal")
    if not spec.action:
        issues.append("missing action")
    if not spec.gate_criteria:
        issues.append("missing gate_criteria")
    if spec.runner not in ("sdk", "tmux", "both"):
        issues.append(f"invalid runner={spec.runner}")
    return issues


def write_evidence(rel_path: str, content: str) -> Path:
    """Write content to evidence/<rel_path>; create parents."""
    out = EVIDENCE_DIR / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    return out


def pillar_coverage(specs: list[BenchmarkSpec]) -> dict:
    """Return {pillar_id: [benchmark_ids]} mapping."""
    from collections import defaultdict
    cov = defaultdict(list)
    for s in specs:
        cov[s.pillar].append(s.id)
    return dict(cov)


def emit_report(report: dict) -> None:
    """Print structured JSON report to stdout."""
    print(json.dumps(report, indent=2))
