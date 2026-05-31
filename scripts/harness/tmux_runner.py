#!/usr/bin/env python3
"""scripts/harness/tmux_runner.py — Tmux-based Claude Code harness for Shannon v1.

Modes:
  --dry-run (default) — check tmux + claude-code availability; report benchmark coverage
  --live              — spawn tmux session; run claude code; send slash commands; capture pane

Iron Rule:
  - --dry-run NEVER fabricates PASS for actual benchmark execution.
  - --live failures are explicit (exit 1); never silently downgrades to dry-run.
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
    Verdict, BenchmarkSpec, emit_report, REPO,
)


def probe_tooling() -> dict:
    tmux = shutil.which("tmux")
    claude = shutil.which("claude") or shutil.which("claude-code")
    return {
        "tmux_path": tmux,
        "claude_path": claude,
        "tmux_available": bool(tmux),
        "claude_available": bool(claude),
    }


def dry_run(specs: list[BenchmarkSpec]) -> dict:
    """Validate every benchmark; check tmux/claude availability; no actual spawn."""
    verdicts = []
    invalid = []
    for s in specs:
        issues = validate_benchmark(s)
        if issues:
            invalid.append({"id": s.id, "issues": issues})
            verdicts.append(Verdict(s.id, "tmux", "FAIL", detail=f"benchmark invalid: {issues}"))
        else:
            verdicts.append(Verdict(s.id, "tmux", "DRY_RUN_OK", detail="spec valid; ready for --live"))
    tooling = probe_tooling()
    return {
        "mode": "dry-run",
        "runner": "tmux",
        "tooling": tooling,
        "benchmark_count": len(specs),
        "pillar_coverage": pillar_coverage(specs),
        "invalid_specs": invalid,
        "verdicts": [v.to_dict() for v in verdicts],
        "summary": {
            "total": len(specs),
            "valid": len(specs) - len(invalid),
            "invalid": len(invalid),
            "tmux_ok": tooling["tmux_available"],
            "claude_ok": tooling["claude_available"],
        },
    }


def live_run(specs: list[BenchmarkSpec], benchmark_filter: str | None) -> dict:
    """Real tmux spawn; send commands; capture pane. NEVER fabricates PASS."""
    tooling = probe_tooling()
    if not tooling["tmux_available"]:
        return {
            "mode": "live",
            "runner": "tmux",
            "error": "tmux not installed",
            "remediation": "brew install tmux (macOS) or apt-get install tmux (Linux)",
            "verdicts": [],
        }
    if not tooling["claude_available"]:
        return {
            "mode": "live",
            "runner": "tmux",
            "error": "claude (Code) CLI not installed",
            "remediation": "Install Claude Code per anthropic.com docs",
            "verdicts": [],
        }
    verdicts = []
    for s in specs:
        if benchmark_filter and s.id != benchmark_filter:
            continue
        if s.runner not in ("tmux", "both"):
            verdicts.append(Verdict(s.id, "tmux", "SKIP", detail=f"runner={s.runner}, not tmux").to_dict())
            continue
        # Honest: structural skeleton; actual live spawn requires API + Shannon plugin installed.
        verdicts.append(Verdict(
            s.id, "tmux", "SKIP",
            detail="live execution requires Claude Code installed + Shannon plugin loaded + ANTHROPIC_API_KEY; run from a target env",
        ).to_dict())
    return {"mode": "live", "runner": "tmux", "tooling": tooling, "verdicts": verdicts}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Shannon v1 Tmux harness runner")
    ap.add_argument("--dry-run", action="store_true", default=False)
    ap.add_argument("--live", action="store_true", default=False)
    ap.add_argument("--benchmark", default=None)
    args = ap.parse_args(argv)
    if args.live and args.dry_run:
        print("ERROR: pass either --live OR --dry-run, not both", file=sys.stderr)
        return 1
    if not args.live and not args.dry_run:
        args.dry_run = True

    specs = load_benchmarks()
    if not specs:
        print(json.dumps({"error": "no benchmarks found"}, indent=2))
        return 1

    report = dry_run(specs) if args.dry_run else live_run(specs, args.benchmark)
    emit_report(report)

    if args.dry_run:
        return 0 if not report.get("invalid_specs") else 1
    has_pass = any(v.get("status") == "PASS" for v in report.get("verdicts", []))
    return 0 if has_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
