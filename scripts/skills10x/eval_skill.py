#!/usr/bin/env python3
"""
eval_skill.py — Per-skill activation eval from REAL claude -p probes.

Adapted from skill-sentinel/skills/skill-activation-audit/scripts/run_eval.py.
Self-contained inside this plugin repo — drives probe.sh (real headless claude
under tmux) + parse_probe.py. No external runner, no v6 native-activation regex
engine, no external-framework dependency.

For each target skill S it computes a real {recall, precision, fp, f1} from probes:

  - SHOULD-TRIGGER prompts: synthesized from S's own `triggers:` block (preferred)
    and its description's "Use when …" clause. A probe is a TRUE POSITIVE iff S
    actually activates (parse_probe verdict HEALTHY for --expect S).
  - CONTROL ("should NOT fire") prompts: synthesized from OTHER skills' triggers +
    a few neutral prompts. A control that activates S is a FALSE POSITIVE.

  recall    = TP / n_should_trigger
  precision = TP / (TP + FP)            (1.0 when TP==FP==0 and no should fired? guarded)
  f1        = 2*P*R / (P+R)

THE 4 TRIGGER-LESS SKILLS (create-meta-prompts, full-functional-audit, gepetto,
prompt-engineering-patterns) have NO `triggers:` block, so they cannot be probed
for activation honestly. Their f1 is recorded as 0.0 with benched=false and a
blocker "no triggers: block — author real triggers". We NEVER synthesize a
self-matching trigger to game the metric (007 operating principle 6).

NO MOCKS: every number comes from a real claude invocation against the real
canonical plugin. Zero skills or unauthenticated claude → the eval fails loudly.

Usage:
  eval_skill.py --outdir DIR [--only skill-a,skill-b] [--trials 3] [--controls 3]
                [--phase before|after] [--probe-args "..."]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe.sh"
PARSE = HERE / "parse_probe.py"
DISCOVER = HERE / "discover_skills.py"

# The 4 canonical trigger-less skills (verified against canonical skills/).
TRIGGERLESS = {
    "create-meta-prompts", "full-functional-audit", "gepetto",
    "prompt-engineering-patterns",
}


def discover():
    res = subprocess.run(["python3", str(DISCOVER)], capture_output=True, text=True, check=True)
    return json.loads(res.stdout)["skills"]


def read_skill_md(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def parse_triggers_block(skill_md_text):
    """Extract the YAML `triggers:` list items from a SKILL.md frontmatter.

    Returns [] when there is no triggers: block (the trigger-less case).
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", skill_md_text, re.DOTALL)
    fm = m.group(1) if m else skill_md_text
    out = []
    in_block = False
    for line in fm.splitlines():
        if re.match(r"^triggers:\s*$", line):
            in_block = True
            continue
        if in_block:
            # list item: "  - phrase" or '  - "phrase"'
            li = re.match(r"^\s*-\s*(.+?)\s*$", line)
            if li:
                val = li.group(1).strip()
                if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
                    val = val[1:-1]
                out.append(val)
                continue
            # any non-indented new key ends the block
            if re.match(r"^[A-Za-z0-9_-]+:", line):
                break
            if not line.strip():
                continue
            break
    return out


# A bare-deictic trigger ends in a dangling "this"/"it" with no specifying object
# ("plan this", "validate this", "remember this"). In a cold-start probe (no prior
# conversation) such a fragment has no antecedent, so the model answers with a
# CLARIFYING QUESTION ("this = what?") rather than an activation decision — a false
# 0/2 that looks like an activation gap but is a MEASUREMENT artifact. (Root-caused
# 2026-06-02: ~14 skills scored 0/2 this way; every one ALSO had a self-sufficient
# trigger that was simply never probed because synthesis iterated from index 0 and
# the bare-deictic phrasing happened to be first.) The proven-good counter-example:
# wave-execution's "run this plan by decomposing it into dependency-ordered waves"
# fired 10/10 despite containing "this plan" — because the verb+manner fully specify
# the capability; the deictic is not load-bearing.
#
# THE FIX IS SELECTION, NOT FABRICATION. The earlier CONTEXT_PREAMBLE attempt
# injected a fake repo-context antecedent; the probe model fact-checked it against
# the real repo and debunked it (self-defeating, reverted). Here we add ZERO claims:
# we simply PREFER the skill's own self-sufficient triggers over its bare-deictic
# ones. A skill with NO self-sufficient trigger surfaces that as a finding (its
# probes stay bare and it will still under-fire) — which is a real authoring gap to
# fix in the SKILL.md, not something to paper over here.
_BARE_DEICTIC = re.compile(r"\b(this|it)\s*$", re.IGNORECASE)


def _is_self_sufficient(phrase):
    """A trigger is self-sufficient if it specifies the capability without relying
    on a dangling deictic object — i.e. it does NOT end in a bare 'this'/'it', OR it
    is long enough (>=4 words) that the verb+manner carry the meaning regardless."""
    p = phrase.strip()
    if not p:
        return False
    if len(p.split()) >= 4:
        return True
    return not bool(_BARE_DEICTIC.search(p))


def synth_should_prompts(skill, trigger_phrases, n):
    """Natural should-trigger prompts. Prefer the author's own trigger phrases —
    SELF-SUFFICIENT ones first (see _is_self_sufficient + the note above) — falling
    back to bare-deictic triggers and the description's 'Use when …' clause only if
    needed. We never inject the skill NAME and never fabricate context: a healthy
    skill must fire from real task phrasing alone."""
    raw = [p.strip() for p in trigger_phrases if p and p.strip()]
    # Stable partition: self-sufficient triggers first, bare-deictic ones after,
    # preserving author order within each group. This is the load-bearing fix —
    # cold-start probes now lead with phrasings that elicit activation, not
    # clarification, WITHOUT adding any synthetic content.
    self_suff = [p for p in raw if _is_self_sufficient(p)]
    bare = [p for p in raw if not _is_self_sufficient(p)]
    prompts = self_suff + bare
    desc = skill.get("description", "") or ""
    m = re.search(r"[Uu]se (?:this )?(?:skill )?when (.+?)(?:\.|$)", desc)
    if m:
        clause = re.sub(r"^(the user|you)\s+(asks?|wants?|needs?)\s+(to\s+)?", "",
                        m.group(1).strip(), flags=re.IGNORECASE)
        prompts.append(f"I need to {clause}")
    if not prompts:
        return []
    # Pad/trim to n, varying surface form lightly. Self-sufficient triggers are
    # consumed first by construction.
    variants, i = [], 0
    while len(variants) < n:
        base = prompts[i % len(prompts)]
        prefix = ["", "Can you ", "Please ", "I'd like you to "][len(variants) % 4]
        variants.append((prefix + base).strip())
        i += 1
    return variants[:n]


def synth_control_prompts(target_name, all_skills, m):
    """Should-NOT-fire prompts drawn from OTHER skills' triggers + neutral asks."""
    controls = []
    neutral = [
        "What's the capital of France?",
        "Summarize the last paragraph I wrote.",
        "Convert 10 miles to kilometers.",
    ]
    for sk in all_skills:
        if (sk.get("name") or sk.get("dir_name")) == target_name:
            continue
        trigs = parse_triggers_block(read_skill_md(sk.get("path", "")))
        if trigs:
            controls.append(trigs[0])
        if len(controls) >= m:
            break
    while len(controls) < m:
        controls.append(neutral[len(controls) % len(neutral)])
    return controls[:m]


def run_probe(prompt, label, outdir, probe_args):
    cmd = ["bash", str(PROBE), "--prompt", prompt, "--label", label, "--outdir", outdir]
    if probe_args:
        cmd += ["--", *probe_args.split()]
    subprocess.run(cmd, check=False)
    dbg = Path(outdir) / f"{label}.debug.log"
    out = Path(outdir) / f"{label}.stdout"
    meta = Path(outdir) / f"{label}.meta.json"
    sess = ""
    if meta.is_file():
        try:
            sess = json.loads(meta.read_text()).get("session_jsonl", "") or ""
        except Exception:
            sess = ""
    return str(dbg), str(out), sess


def parse_expect(dbg, out, expect, sess):
    cmd = ["python3", str(PARSE), "--debug", dbg, "--stdout", out, "--expect", expect, "--json"]
    if sess:
        cmd += ["--session-jsonl", sess]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        return {"verdict": "PARSE_ERROR", "activated": None, "registered": None,
                "stderr": res.stderr}


def f1_score(tp, fp, n_should):
    recall = (tp / n_should) if n_should else 0.0
    precision = (tp / (tp + fp)) if (tp + fp) else (1.0 if tp == 0 and fp == 0 else 0.0)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return round(recall, 3), round(precision, 3), round(f1, 3)


def eval_one(skill, all_skills, outdir, trials, n_controls, phase, probe_args, use_controls):
    name = skill.get("name") or skill.get("dir_name")
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    skill_md = read_skill_md(skill.get("path", ""))
    trig_phrases = parse_triggers_block(skill_md)

    rec = {
        "skill": name,
        "phase": phase,
        "source": skill.get("source"),
        "path": skill.get("path"),
        "trigger_count": len(trig_phrases),
        "benched": bool(trig_phrases),
        "should_trials": [],
        "control_trials": [],
    }

    if not trig_phrases:
        # Trigger-less: cannot honestly probe activation. F1=0, never gamed.
        rec.update({
            "recall": 0.0, "precision": 0.0, "fp": 0, "f1": 0.0,
            "tp": 0, "n_should": 0, "n_controls": 0,
            "diagnosis": "NO_TRIGGERS",
            "blockers": ["no triggers: block — author real triggers before this skill can score F1>0"],
        })
        print(f"[{'NO_TRIGGERS':>16}] {name}: f1=0.0 (trigger-less; benched=false)")
        return rec

    should = synth_should_prompts(skill, trig_phrases, trials)
    tp = 0
    for i, prompt in enumerate(should):
        label = f"{phase}_{safe}_s{i}"
        dbg, out, sess = run_probe(prompt, label, outdir, probe_args)
        v = parse_expect(dbg, out, name, sess)
        fired = bool(v.get("activated"))
        if fired:
            tp += 1
        rec["should_trials"].append({
            "prompt": prompt, "label": label, "verdict": v.get("verdict"),
            "registered": v.get("registered"), "activated": v.get("activated"),
        })

    fp = 0
    controls = synth_control_prompts(name, all_skills, n_controls) if use_controls else []
    for i, prompt in enumerate(controls):
        label = f"{phase}_{safe}_c{i}"
        dbg, out, sess = run_probe(prompt, label, outdir, probe_args)
        v = parse_expect(dbg, out, name, sess)
        fired = bool(v.get("activated"))
        if fired:
            fp += 1
        rec["control_trials"].append({
            "prompt": prompt, "label": label, "verdict": v.get("verdict"),
            "activated_target": v.get("activated"),
        })

    recall, precision, f1 = f1_score(tp, fp, len(should))
    rec.update({
        "tp": tp, "fp": fp, "n_should": len(should), "n_controls": len(controls),
        "recall": recall, "precision": precision, "f1": f1,
        "diagnosis": ("ACTIVATION_FAILURE" if tp == 0 else "INTERMITTENT" if tp < len(should) else "HEALTHY"),
        "blockers": [] if f1 >= 0.90 else [f"f1 {f1} < 0.90"],
    })
    print(f"[{rec['diagnosis']:>16}] {name}: recall={recall} precision={precision} f1={f1} (tp={tp} fp={fp})")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--only", default="", help="comma-separated skill names to eval")
    ap.add_argument("--trials", type=int, default=3, help="should-trigger probes per skill")
    ap.add_argument("--controls", type=int, default=3, help="should-NOT-fire probes per skill (0=skip)")
    ap.add_argument("--no-controls", action="store_true", help="skip control probes (recall-only)")
    ap.add_argument("--phase", default="before", choices=["before", "after"])
    ap.add_argument("--probe-args", default="")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    skills = discover()
    if not skills:
        print("FATAL: no skills discovered. Nothing to evaluate.", file=sys.stderr)
        sys.exit(2)

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    targets = [s for s in skills if not only or (s.get("name") in only or s.get("dir_name") in only)]
    if only and not targets:
        print(f"FATAL: --only {sorted(only)} matched no discovered skill.", file=sys.stderr)
        sys.exit(2)

    use_controls = (not args.no_controls) and args.controls > 0
    report = {"phase": args.phase, "trials_per_skill": args.trials,
              "controls_per_skill": (args.controls if use_controls else 0), "skills": []}
    for skill in targets:
        report["skills"].append(
            eval_one(skill, skills, str(outdir), args.trials, args.controls,
                     args.phase, args.probe_args, use_controls)
        )

    benched = [s for s in report["skills"] if s["benched"]]
    n = len(benched) or 1
    report["summary"] = {
        "total_evaluated": len(report["skills"]),
        "benched": len(benched),
        "trigger_less": sum(1 for s in report["skills"] if not s["benched"]),
        "at_grade_f1": sum(1 for s in report["skills"] if s.get("f1", 0) >= 0.90),
        "mean_f1_benched": round(sum(s["f1"] for s in benched) / n, 3) if benched else 0.0,
    }
    # eval_skill.py is the SOLE activation-truth source for skill_grade.py:
    # it writes per_skill[].f1 rows in the shape skill_grade.py consumes.
    report["per_skill"] = [
        {"skill": s["skill"], "f1": s["f1"], "precision": s["precision"],
         "recall": s["recall"], "fp": s["fp"], "benched": s["benched"]}
        for s in report["skills"]
    ]

    only_tag = ("-" + "_".join(sorted(only))) if only else ""
    rp = outdir / f"eval_summary.{args.phase}{only_tag}.json"
    rp.write_text(json.dumps(report, indent=2))
    print(f"\nSummary: {rp}")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
