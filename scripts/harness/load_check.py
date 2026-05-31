#!/usr/bin/env python3
"""scripts/harness/load_check.py — real SDK load probe for Shannon v1.

Confirms every Shannon command is addressable when the plugin loads, by issuing
a real Claude Agent SDK query and reading the init SystemMessage (slash_commands
list). No API key required — the SDK inherits the Claude Code CLI's own
authentication, so this runs wherever `claude` is logged in.

Usage:
  python3 scripts/harness/load_check.py            # human-readable summary
  python3 scripts/harness/load_check.py --json     # machine-readable report

Iron Rule: the verdict is computed only from the real init payload the running
plugin returns. If the SDK is unreachable, the probe FAILS loudly (exit 1) and
never invents a passing result.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# The 20 commands Shannon v1 ships under commands/*.md. The probe checks every
# one is addressable as a `shannon:<name>` slash command in the loaded plugin.
EXPECTED_COMMANDS = sorted(p.stem for p in (REPO / "commands").glob("*.md"))


async def _probe() -> dict:
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions, SystemMessage
    except ImportError as e:
        return {
            "error": f"claude_agent_sdk not importable: {e}",
            "remediation": "pip install claude-agent-sdk --break-system-packages",
        }

    opts = ClaudeAgentOptions(
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        cwd=str(REPO),
        allowed_tools=["Read"],
        max_turns=1,
    )

    init_data = None
    async for msg in query(prompt="respond with the single word: ready", options=opts):
        if isinstance(msg, SystemMessage):
            data = getattr(msg, "data", None) or {}
            if getattr(msg, "subtype", None) == "init" or "slash_commands" in data:
                init_data = data

    if init_data is None:
        return {"error": "no init SystemMessage captured from SDK"}

    slash = [str(c) for c in (init_data.get("slash_commands", []) or [])]
    shannon_cmds = sorted(
        c.split(":", 1)[1] if ":" in c else c
        for c in slash
        if c.startswith("shannon:") or c.startswith("/shannon:")
    )
    missing = sorted(set(EXPECTED_COMMANDS) - set(shannon_cmds))
    extra = sorted(set(shannon_cmds) - set(EXPECTED_COMMANDS))

    return {
        "total_slash_commands": len(slash),
        "shannon_commands_loaded": len(shannon_cmds),
        "expected_commands": len(EXPECTED_COMMANDS),
        "missing_commands": missing,
        "unexpected_commands": extra,
        "shannon_commands": shannon_cmds,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Shannon v1 SDK load probe")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args(argv)

    report = asyncio.run(_probe())

    if "error" in report:
        report["verdict"] = "FAIL"
    else:
        report["verdict"] = "PASS" if not report["missing_commands"] else "FAIL"

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"verdict: {report['verdict']}")
        if "error" in report:
            print(f"  error: {report['error']}")
            if "remediation" in report:
                print(f"  remediation: {report['remediation']}")
        else:
            print(f"  slash commands total: {report['total_slash_commands']}")
            print(
                f"  shannon commands loaded: {report['shannon_commands_loaded']}"
                f" / {report['expected_commands']} expected"
            )
            if report["missing_commands"]:
                print(f"  MISSING: {', '.join(report['missing_commands'])}")
            if report["unexpected_commands"]:
                print(f"  unexpected: {', '.join(report['unexpected_commands'])}")

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
