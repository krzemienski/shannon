#!/usr/bin/env python3
"""
Shannon v7 — Iron-Rule functional validation harness.

Runs the Agent SDK against the installed Shannon v7 plugin to validate each of
the 12 orchestration improvements (I-01 through I-12) by real-system execution.

Prerequisite:
  1. apply.sh has run successfully on host (dev branch created + landed)
  2. claude plugin marketplace add /Users/nick/Desktop/shannon-framework
  3. claude plugin install shannon@shannon-framework
  4. pip install claude-agent-sdk --break-system-packages

Usage:
  # validate one improvement:
  python3 run-validation.py I-01

  # validate all 12 sequentially:
  python3 run-validation.py --all

  # check evidence after a run:
  python3 run-validation.py --report I-01

Outputs land under /Users/nick/Desktop/shannon-framework/.evidence/I-XX/:
  - transcript.json     full Agent SDK message stream with timestamps
  - tool-calls.json     per-tool invocation counts (Task count = sub-agent count)
  - metadata.json       duration_sec, files_changed, exit_reason
  - validation-report.md PASS/FAIL verdict + per-check results
  - cheating-detected.md only if banned phrases or test-files appear

Iron Rule: every PASS must be backed by real captured transcripts. No mocks.
"""

import asyncio
import json
import subprocess
import sys
import time
import argparse
from pathlib import Path

REPO = Path("/Users/nick/Desktop/shannon-framework")
EVIDENCE_ROOT = REPO / ".evidence"

# ─────────────────────────────────────────────────────────────────────────
# The 12 Iron-Rule acceptance criteria, distilled from v7-plan.md Section D.
# Each entry specifies the prompt to send to the SDK and the expected evidence
# to assert against the captured transcript.
# ─────────────────────────────────────────────────────────────────────────

IMPROVEMENTS = {
    "I-01": {
        "title": "Parallel sub-agent dispatch with single-message + tier-routing",
        "prompt": (
            "/shannon:dispatch-parallel \"Investigate three competing approaches "
            "to in-process caching: (1) in-memory LRU, (2) Redis with TTL, "
            "(3) disk-backed BoltDB. Produce a single markdown comparison table "
            "covering latency, memory cost, durability, and operational complexity. "
            "Write the result to .evidence/I-01/synthesis.md.\""
        ),
        "expected_evidence": [
            ("synthesis.md exists",      lambda d, tr, tc: ((d / "synthesis.md").exists(), "synthesis.md present")),
            ("at least 3 Task calls",    lambda d, tr, tc: (tc.get("Task", 0) >= 3, f"Task count={tc.get('Task', 0)}")),
            ("single-message dispatch",  lambda d, tr, tc: (_check_single_message_dispatch(tr), "all Task calls in one assistant turn")),
            ("table has 3 rows",         lambda d, tr, tc: (_check_table_has_n_rows(d / "synthesis.md", 3), "table covers all 3 approaches")),
        ],
    },
    "I-02": {
        "title": "Multi-round judge-with-debate consensus engine",
        "prompt": (
            "/shannon:judge-with-debate \"Evaluate two competing rewrites of "
            "skills/critique/SKILL.md. Run a 3-round debate between 3 judges "
            "and write the consensus verdict to .evidence/I-02/consensus.md.\""
        ),
        "expected_evidence": [
            ("consensus.md exists",      lambda d, tr, tc: ((d / "consensus.md").exists(), "consensus.md present")),
            ("≥2 Task calls (judges)",   lambda d, tr, tc: (tc.get("Task", 0) >= 2, f"Task count={tc.get('Task', 0)}")),
            ("debate rounds in transcript", lambda d, tr, tc: (_count_phrase(tr, "round") >= 2, "≥2 rounds mentioned in transcript")),
        ],
    },
    "I-03": {
        "title": "Meta-judge primitive — rubric YAML generator",
        "prompt": (
            "/shannon:meta-judge \"Generate an evaluation rubric for a v7 skill "
            "rewrite artifact. Save the YAML to .v7/rubrics/. The rubric must "
            "have 4-7 weighted dimensions summing to 1.0, hidden overall "
            "threshold, and per-dimension acceptance bars.\""
        ),
        "expected_evidence": [
            ("rubric YAML created",      lambda d, tr, tc: (_find_rubric_file(), "rubric-*.yaml exists in .v7/rubrics/")),
            ("≥4 dimensions",            lambda d, tr, tc: (_rubric_dimensions_count() >= 4, f"dimensions count")),
            ("weights sum to 1.0",       lambda d, tr, tc: (_rubric_weights_sum_ok(), "weights ≈ 1.0")),
            ("hidden threshold present", lambda d, tr, tc: (_rubric_has_hidden_threshold(), "overall_pass.hidden_from_judge: true")),
        ],
    },
    "I-04": {
        "title": "Goal-condition engineering (4-part recipe)",
        "prompt": (
            "/shannon:goal-condition-architect \"Migrate the auth module from "
            "session cookies to JWT with httpOnly. Make every change reversible. "
            "All existing tests must continue to pass.\" Produce a /goal condition "
            "with end-state, check, constraints, bound. Save to .evidence/I-04/goal-condition.md."
        ),
        "expected_evidence": [
            ("goal-condition.md exists", lambda d, tr, tc: ((d / "goal-condition.md").exists(), "goal-condition.md present")),
            ("end-state defined",        lambda d, tr, tc: (_file_has_section(d / "goal-condition.md", "end-state"), "end-state section present")),
            ("check defined",            lambda d, tr, tc: (_file_has_section(d / "goal-condition.md", "check"), "check section present")),
            ("constraints defined",      lambda d, tr, tc: (_file_has_section(d / "goal-condition.md", "constraint"), "constraints section present")),
            ("bound defined",            lambda d, tr, tc: (_file_has_section(d / "goal-condition.md", "bound"), "bound section present")),
        ],
    },
    "I-05": {
        "title": "Iron-Rule transcript discipline across loops + gates",
        "prompt": (
            "/shannon:gate-validation-discipline \"Validate this completion claim: "
            "'I migrated the auth module and tests pass.' Without surfaced command "
            "output in the transcript, your verdict must be REFUSED. Write your "
            "verdict to .evidence/I-05/verdict.md.\""
        ),
        "expected_evidence": [
            ("verdict.md exists",        lambda d, tr, tc: ((d / "verdict.md").exists(), "verdict.md present")),
            ("verdict is REFUSED",       lambda d, tr, tc: (_file_contains(d / "verdict.md", "REFUSED"), "REFUSED verdict (no surfaced output)")),
            ("no Bash run for the test", lambda d, tr, tc: (tc.get("Bash", 0) <= 1, "didn't try to fabricate the test run")),
        ],
    },
    "I-06": {
        "title": "No-mocking/no-fakes guard with multi-language examples",
        "prompt": (
            "/shannon:no-mocking-validation-gates \"Show me 3 BAD-vs-GOOD examples "
            "of mock-temptation patterns in Python, TypeScript, and Swift. Save to "
            ".evidence/I-06/examples.md. Bonus: cite which rationalization each "
            "GOOD example refutes.\""
        ),
        "expected_evidence": [
            ("examples.md exists",       lambda d, tr, tc: ((d / "examples.md").exists(), "examples.md present")),
            ("3 languages covered",      lambda d, tr, tc: (_count_phrases(d / "examples.md", ["python", "typescript", "swift"]) >= 3, "Python+TS+Swift mentioned")),
            ("BAD and GOOD per example", lambda d, tr, tc: (_count_phrase_in_file(d / "examples.md", "BAD") >= 3 and _count_phrase_in_file(d / "examples.md", "GOOD") >= 3, "3 BAD + 3 GOOD blocks")),
        ],
    },
    "I-07": {
        "title": "Goal-loop autonomy with stall detection + preconditions",
        "prompt": (
            "/shannon:goal-loop-orchestrator \"Run this goal until convergence: "
            "'All pytest tests in skills/python-agent-sdk/ pass.' Max 3 iterations. "
            "If the same failure persists across 2 iterations, detect stall and "
            "exit with STALL_DETECTED. Write iteration log to .evidence/I-07/loop.log.\""
        ),
        "expected_evidence": [
            ("loop.log exists",          lambda d, tr, tc: ((d / "loop.log").exists(), "loop.log present")),
            ("≥1 iteration logged",      lambda d, tr, tc: (_count_phrase_in_file(d / "loop.log", "iteration") >= 1, "iterations recorded")),
            ("stall-detection check",    lambda d, tr, tc: (_count_phrase(tr, "stall") >= 1 or _count_phrase(tr, "converge") >= 1, "stall/converge mentioned")),
        ],
    },
    "I-08": {
        "title": "Subagent-driven development: code-review between tasks",
        "prompt": (
            "/shannon:subagent-driven-development \"Implement 3 small, independent "
            "function additions to skills/python-agent-sdk/. Between each, dispatch "
            "a code-review subagent. Write per-task and per-review summaries to "
            ".evidence/I-08/.\""
        ),
        "expected_evidence": [
            ("≥6 Task dispatches",       lambda d, tr, tc: (tc.get("Task", 0) >= 6, f"Task count={tc.get('Task', 0)} (3 impl + 3 review)")),
            ("per-task summaries",       lambda d, tr, tc: (len(list(d.glob("task-*.md"))) >= 3, "task-*.md files present")),
        ],
    },
    "I-09": {
        "title": "SDK functional-validation harness (ClaudeSDKClient + hooks)",
        "prompt": (
            "/shannon:python-agent-sdk \"Demonstrate the ClaudeSDKClient pattern "
            "with pre/post hooks and session_id management. Write a runnable demo "
            "script to .evidence/I-09/demo.py. Don't actually run it — Phase 5 "
            "validation script will. Just produce the file.\""
        ),
        "expected_evidence": [
            ("demo.py exists",           lambda d, tr, tc: ((d / "demo.py").exists(), "demo.py present")),
            ("uses ClaudeSDKClient",     lambda d, tr, tc: (_file_contains(d / "demo.py", "ClaudeSDKClient"), "ClaudeSDKClient referenced")),
            ("session_id managed",       lambda d, tr, tc: (_file_contains(d / "demo.py", "session_id"), "session_id referenced")),
            ("hooks present",            lambda d, tr, tc: (_file_contains(d / "demo.py", "hook"), "hooks referenced")),
        ],
    },
    "I-10": {
        "title": "Tree-of-thoughts exploration with proposal/pruning phases",
        "prompt": (
            "/shannon:tree-of-thoughts \"Explore 3 architectural approaches to "
            "Shannon's run-state persistence: filesystem-as-medium, SQLite, JSONL "
            "append-log. Run proposal → pruning → expansion phases. Save the "
            "decision tree and verdict to .evidence/I-10/.\""
        ),
        "expected_evidence": [
            ("≥3 Task dispatches",       lambda d, tr, tc: (tc.get("Task", 0) >= 3, f"Task count={tc.get('Task', 0)}")),
            ("tree.md exists",           lambda d, tr, tc: ((d / "tree.md").exists() or (d / "decision-tree.md").exists(), "tree.md/decision-tree.md present")),
            ("phases referenced",        lambda d, tr, tc: (_count_phrases_in_transcript(tr, ["proposal", "prun", "expan"]) >= 2, "≥2 phases mentioned")),
        ],
    },
    "I-11": {
        "title": "Pre-plan interview/intake step with intent-based depth",
        "prompt": (
            "/shannon:interview-framework \"User wants to add a 'live status' "
            "feature to Shannon. Conduct intake: 3-phase algorithm (Understand → "
            "Propose Approaches → Confirm and Store). Save the interview transcript "
            "and stored intent to .evidence/I-11/.\""
        ),
        "expected_evidence": [
            ("intent.md exists",         lambda d, tr, tc: ((d / "intent.md").exists() or (d / "intake.md").exists(), "intent/intake.md present")),
            ("3-phase structure",        lambda d, tr, tc: (_count_phrases_in_transcript(tr, ["understand", "propose", "confirm"]) >= 2, "phases mentioned")),
        ],
    },
    "I-12": {
        "title": "Worktree merge validation closing parallel orchestration loop",
        "prompt": (
            "/shannon:worktree-merge-validate \"Simulate validating a worktree "
            "merge: read git status, identify which files were touched by a "
            "hypothetical feature-branch merge, and run functional-validation on "
            "each touched module. Write the validation summary to "
            ".evidence/I-12/merge-validation.md.\""
        ),
        "expected_evidence": [
            ("merge-validation.md exists", lambda d, tr, tc: ((d / "merge-validation.md").exists(), "merge-validation.md present")),
            ("git status was read",        lambda d, tr, tc: (tc.get("Bash", 0) >= 1 or _count_phrase(tr, "git status") >= 1, "git status invoked")),
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────
# Cheating detection — banned phrases / patterns / file writes
# ─────────────────────────────────────────────────────────────────────────

BANNED_TRANSCRIPT_PHRASES = [
    "in a real implementation we would",
    "for demonstration purposes",
    "stub for now",
    "i'll mock this",
    "let me add a mock",
    "fake_data =",
]

BANNED_FILE_PATTERNS = [
    "test_", "_test.py", ".test.ts", ".test.tsx", "_spec.rb", "mock_",
]


def detect_cheating(transcript: list, files_changed: list) -> list:
    issues = []
    blob = " ".join(json.dumps(e, default=str).lower() for e in transcript)
    for phrase in BANNED_TRANSCRIPT_PHRASES:
        if phrase in blob:
            # Allow if it appears inside a quoted "no mocking" instruction
            if "no mocking" not in blob:
                issues.append(f"banned phrase: '{phrase}'")
    for f in files_changed:
        for pat in BANNED_FILE_PATTERNS:
            if pat in f:
                issues.append(f"banned file pattern '{pat}' written to {f}")
    return issues


# ─────────────────────────────────────────────────────────────────────────
# Helper assertions
# ─────────────────────────────────────────────────────────────────────────

def _check_single_message_dispatch(transcript: list) -> bool:
    # Look for multiple Task tool uses within a single assistant message
    # Heuristic: any single transcript entry containing "Task(" >=2 times
    for entry in transcript:
        text = str(entry).lower()
        if text.count("task(") >= 2:
            return True
    return False


def _check_table_has_n_rows(path: Path, n: int) -> bool:
    if not path.exists():
        return False
    body = path.read_text()
    # Count markdown table data rows (lines starting with | that aren't separators)
    rows = [ln for ln in body.split("\n") if ln.strip().startswith("|") and "---" not in ln]
    # First row is usually header
    return len(rows) >= n + 1


def _find_rubric_file() -> bool:
    rubrics_dir = REPO / ".v7" / "rubrics"
    return rubrics_dir.exists() and any(rubrics_dir.glob("rubric-*.yaml"))


def _rubric_dimensions_count() -> int:
    rubrics_dir = REPO / ".v7" / "rubrics"
    files = list(rubrics_dir.glob("rubric-*.yaml")) if rubrics_dir.exists() else []
    if not files:
        return 0
    try:
        import yaml
        data = yaml.safe_load(files[-1].read_text())
        return len(data.get("dimensions", []))
    except Exception:
        return 0


def _rubric_weights_sum_ok() -> bool:
    rubrics_dir = REPO / ".v7" / "rubrics"
    files = list(rubrics_dir.glob("rubric-*.yaml")) if rubrics_dir.exists() else []
    if not files:
        return False
    try:
        import yaml
        data = yaml.safe_load(files[-1].read_text())
        total = sum(d.get("weight", 0) for d in data.get("dimensions", []))
        return abs(total - 1.0) < 0.01
    except Exception:
        return False


def _rubric_has_hidden_threshold() -> bool:
    rubrics_dir = REPO / ".v7" / "rubrics"
    files = list(rubrics_dir.glob("rubric-*.yaml")) if rubrics_dir.exists() else []
    if not files:
        return False
    return "hidden_from_judge" in files[-1].read_text().lower()


def _file_has_section(path: Path, keyword: str) -> bool:
    if not path.exists():
        return False
    return keyword.lower() in path.read_text().lower()


def _file_contains(path: Path, text: str) -> bool:
    return path.exists() and text in path.read_text()


def _count_phrase(transcript: list, phrase: str) -> int:
    return sum(str(e).lower().count(phrase.lower()) for e in transcript)


def _count_phrase_in_file(path: Path, phrase: str) -> int:
    if not path.exists():
        return 0
    return path.read_text().lower().count(phrase.lower())


def _count_phrases(path: Path, phrases: list) -> int:
    if not path.exists():
        return 0
    text = path.read_text().lower()
    return sum(1 for p in phrases if p.lower() in text)


def _count_phrases_in_transcript(transcript: list, phrases: list) -> int:
    text = " ".join(str(e).lower() for e in transcript)
    return sum(1 for p in phrases if p.lower() in text)


# ─────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────

async def run_one(improvement_id: str) -> dict:
    if improvement_id not in IMPROVEMENTS:
        raise ValueError(f"Unknown improvement {improvement_id}. Choose from {list(IMPROVEMENTS)}")

    spec = IMPROVEMENTS[improvement_id]
    evidence_dir = EVIDENCE_ROOT / improvement_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Snapshot before
    before = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=str(REPO), text=True
    )

    # Import SDK at runtime so the script can be inspected without the SDK installed
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print("ERROR: claude_agent_sdk not installed. Run:")
        print("  pip install claude-agent-sdk --break-system-packages")
        sys.exit(2)

    options = ClaudeAgentOptions(
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        cwd=str(REPO),
        allowed_tools=[
            "Skill", "Task", "Read", "Write", "Edit",
            "Bash", "Grep", "Glob"
        ],
    )

    transcript = []
    tool_calls = {}
    start = time.time()
    error_msg = None

    try:
        async for message in query(prompt=spec["prompt"], options=options):
            entry = {"ts": round(time.time() - start, 2), "msg": str(message)}
            transcript.append(entry)
            # Track tool calls (best-effort textual match)
            for tname in ["Task", "Skill", "Read", "Write", "Edit", "Bash", "Grep", "Glob"]:
                marker = f"{tname}("
                if marker in str(message):
                    tool_calls[tname] = tool_calls.get(tname, 0) + str(message).count(marker)
    except Exception as e:
        error_msg = str(e)
        transcript.append({"ts": round(time.time() - start, 2), "error": error_msg})

    duration = round(time.time() - start, 2)

    after = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=str(REPO), text=True
    )
    files_changed = [ln[3:] for ln in after.split("\n") if ln and ln not in before]

    # Write evidence artifacts
    (evidence_dir / "transcript.json").write_text(
        json.dumps(transcript, indent=2, default=str)
    )
    (evidence_dir / "tool-calls.json").write_text(
        json.dumps(tool_calls, indent=2)
    )
    (evidence_dir / "metadata.json").write_text(json.dumps({
        "improvement_id": improvement_id,
        "title": spec["title"],
        "duration_sec": duration,
        "tool_call_total": sum(tool_calls.values()),
        "sub_agent_count": tool_calls.get("Task", 0),
        "files_changed": files_changed,
        "exit_reason": "completed" if error_msg is None else f"error: {error_msg}",
    }, indent=2))

    # Cheating detection
    cheating = detect_cheating(transcript, files_changed)
    if cheating:
        (evidence_dir / "cheating-detected.md").write_text(
            "# Cheating detected\n\n" + "\n".join(f"- {c}" for c in cheating)
        )

    # Run acceptance checks
    check_results = []
    for name, check_fn in spec["expected_evidence"]:
        try:
            ok, msg = check_fn(evidence_dir, transcript, tool_calls)
        except Exception as e:
            ok, msg = False, f"check raised {type(e).__name__}: {e}"
        check_results.append({"name": name, "pass": bool(ok), "message": msg})

    verdict = "PASS"
    if cheating:
        verdict = "FINAL_FAIL_CHEATING"
    elif not all(r["pass"] for r in check_results):
        verdict = "FAIL"
    elif error_msg:
        verdict = "FAIL_ERROR"

    # Write per-improvement validation report
    lines = [
        f"# Validation report — {improvement_id}",
        "",
        f"**Title**: {spec['title']}",
        f"**Verdict**: {verdict}",
        f"**Duration**: {duration}s",
        f"**Total tool calls**: {sum(tool_calls.values())}",
        f"**Sub-agent dispatches (Task)**: {tool_calls.get('Task', 0)}",
        f"**Files changed**: {len(files_changed)}",
        f"**Error**: {error_msg or 'none'}",
        f"**Cheating detected**: {'YES — see cheating-detected.md' if cheating else 'no'}",
        "",
        "## Per-check results",
        "",
    ]
    for r in check_results:
        mark = "✅" if r["pass"] else "❌"
        lines.append(f"- {mark} {r['name']}: {r['message']}")
    lines.append("")
    lines.append("## Acceptance prompt (verbatim)")
    lines.append("")
    lines.append("```")
    lines.append(spec["prompt"])
    lines.append("```")
    lines.append("")
    lines.append("## Evidence artifacts")
    lines.append("")
    lines.append(f"- transcript.json ({len(transcript)} entries)")
    lines.append("- tool-calls.json")
    lines.append("- metadata.json")
    if cheating:
        lines.append("- cheating-detected.md")

    (evidence_dir / "validation-report.md").write_text("\n".join(lines))

    return {
        "improvement_id": improvement_id,
        "verdict": verdict,
        "duration_sec": duration,
        "tool_calls": tool_calls,
        "files_changed": len(files_changed),
        "cheating": cheating,
        "checks_pass": sum(1 for r in check_results if r["pass"]),
        "checks_total": len(check_results),
    }


async def run_all() -> list:
    results = []
    for imp_id in sorted(IMPROVEMENTS.keys()):
        print(f"\n══════ Running {imp_id} ══════")
        try:
            result = await run_one(imp_id)
        except Exception as e:
            result = {"improvement_id": imp_id, "verdict": f"HARNESS_ERROR: {e}"}
        results.append(result)
        print(f"  → {result['verdict']}")

    # Consolidated report
    consolidated = REPO / ".prompts" / "004-shannon-v7-functional-validation-do" / "VALIDATION_REPORT.md"
    consolidated.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Shannon v7 — Functional Validation Report (consolidated)",
        "",
        f"**Generated**: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        "",
        "| ID | Title | Verdict | Duration | Tool calls | Sub-agents |",
        "|----|-------|---------|----------|-----------:|-----------:|",
    ]
    for r in results:
        imp = IMPROVEMENTS.get(r["improvement_id"], {})
        lines.append(
            f"| {r['improvement_id']} "
            f"| {imp.get('title', '?')[:60]} "
            f"| {r.get('verdict', '?')} "
            f"| {r.get('duration_sec', 0)}s "
            f"| {sum(r.get('tool_calls', {}).values())} "
            f"| {r.get('tool_calls', {}).get('Task', 0)} |"
        )
    pass_count = sum(1 for r in results if r.get('verdict') == 'PASS')
    lines += [
        "",
        f"**Overall**: {pass_count}/{len(results)} PASS",
        "",
        ("**Recommendation**: READY_TO_RELEASE" if pass_count == len(results)
         else "**Recommendation**: RELEASE_WITH_NOTED_GAPS or BLOCK_RELEASE — see per-improvement reports"),
    ]
    consolidated.write_text("\n".join(lines))
    print(f"\n→ Consolidated report: {consolidated}")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Shannon v7 Iron-Rule functional validation harness"
    )
    parser.add_argument(
        "improvement",
        nargs="?",
        help="Improvement ID (I-01 .. I-12) or --all",
    )
    parser.add_argument("--all", action="store_true", help="Run all 12 improvements sequentially")
    parser.add_argument("--report", help="Print the validation-report.md for improvement <id>")
    parser.add_argument("--list", action="store_true", help="List all improvements")
    args = parser.parse_args()

    if args.list:
        for imp_id in sorted(IMPROVEMENTS):
            print(f"  {imp_id}  {IMPROVEMENTS[imp_id]['title']}")
        return

    if args.report:
        report_path = EVIDENCE_ROOT / args.report / "validation-report.md"
        if report_path.exists():
            print(report_path.read_text())
        else:
            print(f"No report yet for {args.report}: run validation first")
        return

    if args.all or args.improvement == "--all":
        asyncio.run(run_all())
    elif args.improvement and args.improvement.startswith("I-"):
        asyncio.run(run_one(args.improvement))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
