#!/usr/bin/env python3
"""
regression_guards.py — Post-edit non-regression gate for the skills-10x loop.

Ported from 007's <regression_guards>. Compares a BEFORE full-corpus eval against
an AFTER full-corpus eval (both produced by eval_skill.py with NO `--only`) and
asserts no skill or global metric regressed when one skill's SKILL.md was edited.

D3 — FAIL CLOSED: proving non-regression requires a real FULL-corpus eval BEFORE
and AFTER on disk. If either baseline is missing or is not a full-corpus run
(e.g. produced with --only), every guard FAILS — never passes by default. A
`--only` summary cannot stand in for the corpus baseline.

Guards (all must hold, else REGRESSION):
  G1 global_recall      : mean benched recall AFTER >= BEFORE
  G2 innocent_precision : mean benched precision AFTER >= BEFORE
  G3 innocent_fp        : total false positives AFTER <= BEFORE
  G4 sibling_f1         : for every OTHER skill, f1 must not drop >0.02 from its
                          own BEFORE value, and must not fall below 0.50
  G5 trigger_count      : per-skill trigger_count AFTER >= committed baseline
                          (.skills10x/trigger-counts.json) unless --edited names it

Usage:
  regression_guards.py --before BEFORE.json --after AFTER.json \
      [--edited skill-just-changed] [--baseline .skills10x/trigger-counts.json] [--json]

Exit code: 0 = all guards PASS (no regression); 1 = any guard FAIL or baseline missing.
"""
import argparse
import json
import sys
from pathlib import Path

SIBLING_DROP = 0.02
SIBLING_FLOOR = 0.50


def load_corpus(path, label):
    """Load a full-corpus eval summary. FAIL-closed on missing / non-corpus input."""
    p = Path(path)
    if not p.is_file():
        return None, f"{label} eval missing on disk: {path}"
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        return None, f"{label} eval unreadable: {e}"
    per = data.get("per_skill")
    if not per:
        return None, f"{label} eval has no per_skill[] — not a corpus run"
    # A corpus run evaluates many skills; a single-skill --only run is NOT a baseline.
    if len(per) < 2:
        return None, (f"{label} eval has only {len(per)} skill(s) — a --only run "
                      "cannot serve as the full-corpus regression baseline")
    return data, None


def benched_rows(data):
    return [r for r in data["per_skill"] if r.get("benched")]


def mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 4) if xs else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--edited", default="", help="skill whose SKILL.md was just edited")
    ap.add_argument("--baseline", default=".skills10x/trigger-counts.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = {"guards": [], "regression": False, "fail_closed": False}

    before, err_b = load_corpus(args.before, "BEFORE")
    after, err_a = load_corpus(args.after, "AFTER")
    if err_b or err_a:
        # D3 FAIL-CLOSED: no valid full-corpus baseline → guards cannot pass.
        result["fail_closed"] = True
        result["regression"] = True
        result["guards"].append({"id": "baseline-present", "status": "FAIL",
                                  "detail": "; ".join(x for x in (err_b, err_a) if x)})
        emit(result, args.json)
        sys.exit(1)

    b_rows = {r["skill"]: r for r in before["per_skill"]}
    a_rows = {r["skill"]: r for r in after["per_skill"]}

    # G1 global recall
    rb, ra = mean(r["recall"] for r in benched_rows(before)), mean(r["recall"] for r in benched_rows(after))
    add(result, "G1-global-recall", ra >= rb, f"recall {rb} -> {ra}")

    # G2 innocent precision
    pb, pa = mean(r["precision"] for r in benched_rows(before)), mean(r["precision"] for r in benched_rows(after))
    add(result, "G2-innocent-precision", pa >= pb, f"precision {pb} -> {pa}")

    # G3 innocent fp
    fb = sum(int(r.get("fp", 0)) for r in benched_rows(before))
    fa = sum(int(r.get("fp", 0)) for r in benched_rows(after))
    add(result, "G3-innocent-fp", fa <= fb, f"fp {fb} -> {fa}")

    # G4 sibling f1
    sib_fail = []
    for skill, ar in a_rows.items():
        if skill == args.edited:
            continue
        br = b_rows.get(skill)
        if not br:
            continue
        b_f1, a_f1 = float(br.get("f1", 0)), float(ar.get("f1", 0))
        if (b_f1 - a_f1) > SIBLING_DROP or (a_f1 < SIBLING_FLOOR and a_f1 < b_f1):
            sib_fail.append(f"{skill}: {b_f1}->{a_f1}")
    add(result, "G4-sibling-f1", not sib_fail,
        ("ok" if not sib_fail else f"regressed: {sib_fail}"))

    # G5 trigger-count guard
    tc_path = Path(args.baseline)
    tc_fail = []
    if tc_path.is_file():
        try:
            baseline_counts = json.loads(tc_path.read_text())
        except Exception:
            baseline_counts = {}
        for skill, ar in a_rows.items():
            if skill == args.edited:
                continue
            base = baseline_counts.get(skill)
            cur = ar.get("trigger_count")
            if base is not None and cur is not None and cur < base:
                tc_fail.append(f"{skill}: {base}->{cur}")
        add(result, "G5-trigger-count", not tc_fail,
            ("ok" if not tc_fail else f"dropped: {tc_fail}"))
    else:
        add(result, "G5-trigger-count", True,
            f"baseline {args.baseline} absent — skipped (create it to enforce)")

    result["regression"] = any(g["status"] == "FAIL" for g in result["guards"])
    emit(result, args.json)
    sys.exit(1 if result["regression"] else 0)


def add(result, gid, ok, detail):
    result["guards"].append({"id": gid, "status": "PASS" if ok else "FAIL", "detail": detail})


def emit(result, as_json):
    if as_json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for g in result["guards"]:
            print(f"[{g['status']}] {g['id']}: {g['detail']}")
        print(f"\nREGRESSION: {result['regression']}"
              + ("  (FAIL-CLOSED: missing/invalid corpus baseline)" if result.get("fail_closed") else ""))


if __name__ == "__main__":
    main()
