#!/usr/bin/env python3
"""
skill_grade.py — Merge objective activation F1 + a quality-rubric score into one grade.

ACTIVATION-TRUTH SOURCE (D0): the activation F1 comes from eval_skill.py's
`eval_summary.<phase>.json` (its `per_skill[].f1` rows), produced by REAL
`claude -p` probes. It does NOT come from any v6 native-activation regex engine —
there is exactly ONE source of activation truth in this harness, and it is
eval_skill.py. Adapted from 007's skill_grade.py, with the activation source
re-pointed to eval_skill.py (real probes) per the locked v1-native decision —
the v6 native-activation regex engine is deliberately NOT consulted.

PASS gate (all three conjuncts must hold on the post-edit measurement):
  activation_f1 >= 0.90  AND  rubric_min >= 0.90  AND  benched == true

`benched == false` means the skill has no `triggers:` block and was not probed —
it cannot PASS until real triggers are authored (the 4 trigger-less skills).

Usage:
  skill_grade.py <skill> <eval_summary.json> <rubric.json> <out.json>

  <eval_summary.json> : an eval_skill.py output (has per_skill[] with f1/precision/recall/fp/benched)
  <rubric.json>       : a judge sub-agent's STRICT JSON {dimensions, min, composite, notes}
  <out.json>          : where to write the merged grade
"""
import sys
import json
import pathlib

# Rubric weights (mirror judge_rubric.md) for the recorded composite.
WEIGHTS = {
    "description_quality": 0.18, "trigger_coverage": 0.16,
    "progressive_disclosure": 0.12, "workflow_clarity": 0.14,
    "examples": 0.12, "constraints_gates": 0.12,
    "token_efficiency": 0.08, "coherence_correctness": 0.08,
}


def weighted_composite(dims):
    if set(dims) == set(WEIGHTS):
        return round(sum(dims[k] * WEIGHTS[k] for k in WEIGHTS), 4)
    # Unknown dimension set: fall back to a flat mean so the number is still defined.
    return round(sum(dims.values()) / len(dims), 4) if dims else 0.0


def main(skill, summary_path, rubric_path, out_path):
    summ = json.load(open(summary_path))
    # eval_skill.py is the activation-truth source: read its per_skill row.
    row = next((r for r in summ.get("per_skill", []) if r["skill"] == skill), None)
    activation_f1 = float(row["f1"]) if row else 0.0
    precision = float(row.get("precision", 0.0)) if row else 0.0
    recall = float(row.get("recall", 0.0)) if row else 0.0
    fp = int(row.get("fp", 0)) if row else 0
    # benched: the skill was actually probed (has a triggers: block). Honor the
    # eval_skill.py flag if present; otherwise a missing row means not benched.
    benched = bool(row.get("benched")) if row else False

    rubric = json.load(open(rubric_path))
    dims = rubric["dimensions"]
    dim_min = min(dims.values()) if dims else 0.0
    composite = weighted_composite(dims)

    passes = (activation_f1 >= 0.90) and (dim_min >= 0.90) and benched
    grade = {
        "skill": skill,
        "benched": benched,
        "activation_source": "eval_skill.py (real claude -p probes)",
        "activation": {"f1": activation_f1, "precision": precision,
                       "recall": recall, "fp": fp},
        "rubric": {"dimensions": dims, "min": round(dim_min, 4),
                   "composite": composite, "notes": rubric.get("notes", "")},
        "grade_pass": bool(passes),
        "blockers": (
            ([] if benched else ["no triggers in eval — not benched (author real triggers)"])
            + ([] if activation_f1 >= 0.90 else [f"activation_f1 {activation_f1} < 0.90"])
            + ([] if dim_min >= 0.90 else [f"rubric min {round(dim_min, 4)} < 0.90"])
        ),
    }
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    json.dump(grade, open(out_path, "w"), indent=2)
    print(json.dumps({"skill": skill, "f1": activation_f1, "rubric_min": round(dim_min, 4),
                      "benched": benched, "pass": bool(passes),
                      "blockers": grade["blockers"]}))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("usage: skill_grade.py <skill> <eval_summary.json> <rubric.json> <out.json>",
              file=sys.stderr)
        sys.exit(64)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
