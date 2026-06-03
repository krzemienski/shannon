#!/usr/bin/env python3
"""
parse_probe.py — Extract skill load + activation evidence from a claude --debug run.

Vendored from skill-sentinel/skills/skill-activation-audit/scripts/parse_debug_log.py.
Self-contained, pure stdlib — no external runner, no v6 native-activation
regex engine, no external-framework dependency.

Reads a probe's debug log + stdout (+ session JSONL) and answers two questions:

  1. REGISTRATION: did the skill even load into the session? (token-budget overflow,
     bad YAML, wrong directory all cause silent non-registration)
  2. ACTIVATION:   given it loaded, did THIS run actually invoke it?

Because Claude Code's debug format has shifted across versions, this parser is
signal-based and defensive: it matches multiple known phrasings and also reads the
authoritative Skill tool_use events from the session JSONL (claude 2.1.x). It never
assumes a fixed log schema.

Usage:
  parse_probe.py --debug DEBUG.log --stdout OUT.stdout [--session-jsonl S.jsonl]
                 [--expect skill-name] [--json] [--raw] [--context-lines N]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Known phrasings for "skills were loaded / registered" across versions.
LOAD_COUNT_PATTERNS = [
    re.compile(r"[Ll]oaded\s+(\d+)\s+(?:unique\s+)?skills?"),
    re.compile(r"(\d+)\s+skills?\s+(?:loaded|registered|available|discovered)"),
    re.compile(r"[Ss]kill\s+registry[^0-9]*(\d+)"),
]


def skill_registered_patterns(name):
    n = re.escape(name)
    bare = name.split(":")[-1] if ":" in name else name
    b = re.escape(bare)
    return [
        re.compile(rf"(?:[Ll]oaded|[Rr]egistered|[Dd]iscovered)\s+skill[^A-Za-z0-9]*{n}\b"),
        re.compile(rf"skill[^A-Za-z0-9]+{n}\b.*(?:loaded|registered|available)"),
        re.compile(rf"\b{n}\b.*SKILL\.md"),
        re.compile(rf"SKILL\.md.*\b{n}\b"),
        re.compile(rf"skills?[/\\]{b}[/\\]SKILL\.md"),
        re.compile(rf"skills?[/\\]{b}\b"),
        re.compile(rf"[Pp]rocessing\s+\d+\s+skill\s+paths?\s+for\s+plugin\s+{b}\b"),
        re.compile(rf"plugin\s+{b}\b.*skills"),
        re.compile(rf"Skill\([^)]*\b{b}\b[^)]*\)"),
    ]


def skill_activated_patterns(name):
    n = re.escape(name)
    return [
        re.compile(rf"(?:[Ii]nvoking|[Aa]ctivating|[Uu]sing|[Cc]alling)\s+[Ss]kill[^A-Za-z0-9]*{n}\b"),
        re.compile(rf"[Ss]kill\s*\(\s*{n}\s*\)"),
        re.compile(rf"tool[_\s]*use.*\b{n}\b.*skill", re.IGNORECASE),
        re.compile(rf"\bRead\b.*{n}/SKILL\.md"),
        re.compile(rf"\b{n}\b.*(?:triggered|activated|invoked)"),
    ]


GENERIC_ACTIVATION = [
    re.compile(r"[Ii]nvoking skill"),
    re.compile(r"[Ss]kill\([^)]+\)"),
    re.compile(r"Read .*/SKILL\.md"),
    re.compile(r"[Aa]ctivating skill"),
]

ERROR_SIGNALS = [
    re.compile(r"(?:YAML|frontmatter|yaml)\s+(?:parse|parsing)?\s*error", re.IGNORECASE),
    re.compile(r"failed to (?:parse|load) skill", re.IGNORECASE),
    re.compile(r"skill[^\n]*budget[^\n]*exceeded", re.IGNORECASE),
    re.compile(r"char(?:acter)?\s*budget", re.IGNORECASE),
    re.compile(r"[Uu]nknown skill"),
    re.compile(r"can only be invoked by Claude"),
]


def read_text(p):
    if not p:
        return ""
    path = Path(p)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def first_match(patterns, text):
    for pat in patterns:
        m = pat.search(text)
        if m:
            return m.group(0)
    return None


def matched_lines(patterns, text, context=1):
    """Return full log lines (with N lines of context) where any pattern hit."""
    lines = text.splitlines()
    hits = []
    seen = set()
    for i, line in enumerate(lines):
        for pat in patterns:
            if pat.search(line):
                lo = max(0, i - context)
                hi = min(len(lines), i + context + 1)
                block_key = (lo, hi)
                if block_key in seen:
                    continue
                seen.add(block_key)
                hits.append({
                    "line_no": i + 1,
                    "pattern": pat.pattern,
                    "context": [lines[j] for j in range(lo, hi)],
                })
                break
    return hits


def read_session_skill_invocations(session_jsonl_path):
    """Read a claude --session-id transcript; return list of Skill names invoked.

    The transcript is JSONL; Skill activations appear as tool_use blocks with
    name='Skill'. The skill identifier lives under input.command in current
    claude builds (e.g. {"command": "shannon:wave-execution"}); older/synthetic
    payloads used input.skill or input.name. We read all three keys so a real
    activation is never missed. This JSONL signal is AUTHORITATIVE — the debug
    log no longer emits per-skill dispatch lines, and the text fallback below
    (skill_activated_patterns) false-positives on a plain Read/Glob of SKILL.md.
    """
    if not session_jsonl_path:
        return []
    p = Path(session_jsonl_path)
    if not p.is_file():
        return []
    invoked = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        msg = rec.get("message") or {}
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                inp = block.get("input") or {}
                sk = inp.get("command") or inp.get("skill") or inp.get("name")
                if sk:
                    invoked.append(sk)
    return invoked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug", required=True)
    ap.add_argument("--stdout", default="")
    ap.add_argument("--session-jsonl", default="",
                    help="path to the probe's session JSONL (read Skill tool_use events)")
    ap.add_argument("--expect", default="", help="skill name expected to activate")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--raw", action="store_true",
                    help="surface the actual matched debug-log lines (with context) for calibration")
    ap.add_argument("--context-lines", type=int, default=1)
    args = ap.parse_args()

    debug = read_text(args.debug)
    out = read_text(args.stdout)
    combined = debug + "\n" + out

    load_count = None
    for pat in LOAD_COUNT_PATTERNS:
        m = pat.search(debug)
        if m:
            load_count = int(m.group(1))
            break

    errors = [m.group(0) for pat in ERROR_SIGNALS for m in [pat.search(combined)] if m]

    result = {
        "debug_file": args.debug,
        "loaded_skill_count": load_count,
        "error_signals": sorted(set(errors)),
        "expected_skill": args.expect or None,
    }

    invoked = read_session_skill_invocations(args.session_jsonl) if args.session_jsonl else []
    result["session_skill_invocations"] = invoked

    if args.expect:
        reg = first_match(skill_registered_patterns(args.expect), combined)
        bare = args.expect.split(":")[-1]
        act_jsonl = any(
            sk == args.expect or sk == bare or sk.split(":")[-1] == bare
            for sk in invoked
        )
        # AUTHORITATIVE-FIRST activation. When a session JSONL is present we trust
        # ONLY the real Skill tool_use it records. The text-pattern check
        # (skill_activated_patterns) matches lines like
        # `Read .../wave-execution/SKILL.md` that the model emits while EXPLORING
        # the repo, not while activating the skill. In an in-repo probe that text
        # signal yields false HEALTHY verdicts (proven 2026-06-02: zero real
        # activations, two HEALTHY at f1=0.8, each traced to a Glob of the
        # SKILL.md path). Consult the text signal ONLY when no JSONL exists.
        have_jsonl = bool(args.session_jsonl) and Path(args.session_jsonl).is_file()
        act_log = None if have_jsonl else first_match(skill_activated_patterns(args.expect), combined)
        act = act_jsonl or bool(act_log)
        # Registration is a PRECONDITION of activation: a skill cannot emit a Skill
        # tool_use unless it was registered. So when activation is proven by the
        # authoritative JSONL signal, registration is proven transitively — even
        # though the debug-log text pattern (`reg`) is dead in claude 2.1.x (it no
        # longer prints per-skill "N skills loaded" dispatch lines; see
        # read_session_skill_invocations docstring). Gating the verdict on the dead
        # text pattern stamped REGISTRATION_FAILURE on genuinely-HEALTHY probes
        # (proven 2026-06-03 smoke: 1 real Skill tool_use, f1=1.0, yet
        # verdict=REGISTRATION_FAILURE). The f1 gate reads `activated` and was always
        # correct; this only repairs the human-facing verdict label + `registered`.
        registered = bool(reg) or act_jsonl
        result.update({
            "registered": registered,
            "registered_evidence": (
                reg if reg
                else (f"transitive: Skill tool_use proves registration ({args.expect})"
                      if act_jsonl else None)
            ),
            "activated": act,
            "activated_evidence": (
                f"session-jsonl Skill tool_use: {args.expect}" if act_jsonl else act_log
            ),
            "verdict": (
                "REGISTRATION_FAILURE" if not registered
                else "ACTIVATION_FAILURE" if not act
                else "HEALTHY"
            ),
            "activation_source": "session_jsonl" if act_jsonl else ("debug_log" if act_log else None),
            "activation_signal_mode": "jsonl_only" if have_jsonl else "text_pattern",
        })
        if args.raw:
            result["raw"] = {
                "registration_matches": matched_lines(
                    skill_registered_patterns(args.expect), combined, args.context_lines),
                "activation_matches": matched_lines(
                    skill_activated_patterns(args.expect), combined, args.context_lines),
                "error_matches": matched_lines(ERROR_SIGNALS, combined, args.context_lines),
            }
    else:
        generic = first_match(GENERIC_ACTIVATION, combined)
        result.update({
            "any_skill_activated": bool(generic),
            "any_activation_evidence": generic,
        })
        if args.raw:
            result["raw"] = {
                "activation_matches": matched_lines(GENERIC_ACTIVATION, combined, args.context_lines),
                "error_matches": matched_lines(ERROR_SIGNALS, combined, args.context_lines),
            }

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        raw = result.pop("raw", None)
        for k, v in result.items():
            print(f"{k}: {v}")
        if raw:
            print("\n--- raw matched log lines (calibration view) ---")
            for group, hits in raw.items():
                print(f"\n[{group}] {len(hits)} match block(s):")
                if not hits:
                    print("    (none — parser found no matching lines)")
                for h in hits:
                    print(f"    L{h['line_no']}  /{h['pattern']}/")
                    for cl in h["context"]:
                        print(f"      | {cl}")

    if args.expect:
        sys.exit(0 if result.get("verdict") == "HEALTHY" else 3)


if __name__ == "__main__":
    main()
