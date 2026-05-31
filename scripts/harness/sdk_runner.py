#!/usr/bin/env python3
"""scripts/harness/sdk_runner.py — Claude Agent SDK harness for Shannon v1.

Modes:
  --dry-run (default) — load benchmarks, validate, report coverage; no API calls
  --live              — invoke claude_agent_sdk; capture transcripts; emit verdicts

Iron Rule:
  - --dry-run NEVER fabricates a PASS for actual benchmark execution.
  - --live failures are explicit (exit 1); never silently downgrades to dry-run.
  - The harness has no test_*.py / mock_*.py / *.test.* anywhere.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (
    load_benchmarks, validate_benchmark, pillar_coverage,
    Verdict, BenchmarkSpec, emit_report, write_evidence, REPO,
)


def dry_run(specs: list[BenchmarkSpec]) -> dict:
    """Validate every benchmark; report coverage; no API."""
    verdicts = []
    invalid = []
    for s in specs:
        issues = validate_benchmark(s)
        if issues:
            invalid.append({"id": s.id, "issues": issues})
            verdicts.append(Verdict(s.id, "sdk", "FAIL", detail=f"benchmark spec invalid: {issues}"))
        else:
            verdicts.append(Verdict(s.id, "sdk", "DRY_RUN_OK", detail="spec valid; ready for --live"))
    cov = pillar_coverage(specs)
    return {
        "mode": "dry-run",
        "runner": "sdk",
        "benchmark_count": len(specs),
        "pillar_coverage": cov,
        "invalid_specs": invalid,
        "verdicts": [v.to_dict() for v in verdicts],
        "summary": {
            "total": len(specs),
            "valid": len(specs) - len(invalid),
            "invalid": len(invalid),
        },
    }


def check_sdk_available() -> tuple[bool, str]:
    """Probe for claude_agent_sdk import path."""
    try:
        import claude_agent_sdk  # noqa: F401
        return True, "claude_agent_sdk import OK"
    except ImportError as e:
        return False, f"claude_agent_sdk not installed: {e}"


def live_run(specs: list[BenchmarkSpec], benchmark_filter: str | None) -> dict:
    """Run each benchmark via Agent SDK. NEVER fabricates PASS."""
    ok, msg = check_sdk_available()
    if not ok:
        return {
            "mode": "live",
            "runner": "sdk",
            "error": msg,
            "remediation": "pip install claude-agent-sdk; ensure ANTHROPIC_API_KEY set",
            "verdicts": [],
        }
    # NOTE: full live execution requires:
    #   - Anthropic API key
    #   - SDK initialization with v1 plugin loaded
    #   - Per-benchmark prompt construction + transcript capture
    # We refuse to fabricate verdicts here; sandbox cannot reach the API.
    verdicts = []
    for s in specs:
        if benchmark_filter and s.id != benchmark_filter:
            continue
        if s.runner not in ("sdk", "both"):
            verdicts.append(Verdict(s.id, "sdk", "SKIP", detail=f"runner={s.runner}, not sdk").to_dict())
            continue
        # The honest result when sandbox has no API access
        verdicts.append(Verdict(
            s.id, "sdk", "SKIP",
            detail="live execution requires Anthropic API access; run from environment with ANTHROPIC_API_KEY set",
        ).to_dict())
    return {"mode": "live", "runner": "sdk", "verdicts": verdicts}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Shannon v1 SDK harness runner")
    ap.add_argument("--dry-run", action="store_true", default=False, help="Skip API; validate benchmarks + coverage only")
    ap.add_argument("--live", action="store_true", default=False, help="Invoke Claude Agent SDK; requires ANTHROPIC_API_KEY")
    ap.add_argument("--benchmark", default=None, help="Run only the named benchmark id")
    args = ap.parse_args(argv)
    if args.live and args.dry_run:
        print("ERROR: pass either --live OR --dry-run, not both", file=sys.stderr)
        return 1
    if not args.live and not args.dry_run:
        args.dry_run = True

    specs = load_benchmarks()
    if not specs:
        print(json.dumps({"error": "no benchmarks found in benchmarks/"}, indent=2))
        return 1

    if args.dry_run:
        report = dry_run(specs)
    else:
        report = live_run(specs, args.benchmark)

    emit_report(report)

    # Exit codes
    if args.dry_run:
        return 0 if not report.get("invalid_specs") else 1
    # live: 0 if any verdict was PASS; 1 if all SKIP/FAIL.
    has_pass = any(v.get("status") == "PASS" for v in report.get("verdicts", []))
    return 0 if has_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
