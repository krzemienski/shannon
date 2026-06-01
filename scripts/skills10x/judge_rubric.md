# Skills-10x Quality Rubric (8 dimensions)

Ported from `007-skills-10x-enhancement-do` `<quality_rubric>`. A fresh `Task`
sub-agent (one per skill) grades a single `SKILL.md` against these 8 dimensions,
each scored `0.0–1.0`. Score **conservatively**: `0.90+` means genuinely
excellent, not merely "fine."

The judge sub-agent is fed: the FULL `SKILL.md` text + this rubric + the
instruction to return **ONLY** strict JSON. It is grading DESIGN QUALITY against
Anthropic skill best-practices (name/description, progressive disclosure,
concrete triggers, examples, guardrails) — not whether the skill "looks nice."

## Dimensions + weights

| # | dimension (key) | weight | what 0.90+ looks like |
|---|-----------------|--------|------------------------|
| 1 | `description_quality`     | 0.18 | Third-person, directive, trigger-forward ("Use when…/ALWAYS use when…"); states WHAT it does AND WHEN to use it; names concrete trigger phrases; no vague fluff. |
| 2 | `trigger_coverage`        | 0.16 | A `triggers:` block with real, comprehensive phrasings users actually type (terse + natural); covers the skill's distinct intents; no junk/gaming; disambiguated from sibling skills. |
| 3 | `progressive_disclosure`  | 0.12 | `SKILL.md` is lean (heavy detail pushed to reference files); not a monolith; loads only what's needed. |
| 4 | `workflow_clarity`        | 0.14 | Ordered, actionable steps; decision points explicit; an executor could follow it without guessing. |
| 5 | `examples`                | 0.12 | Concrete, realistic examples incl. at least one edge case or before/after; not toy snippets. |
| 6 | `constraints_gates`       | 0.12 | Explicit MUST / MUST-NOT, validation/quality gates, and named anti-patterns. |
| 7 | `token_efficiency`        | 0.08 | Tight, high-signal prose; no filler, no repetition; every line earns its tokens. |
| 8 | `coherence_correctness`   | 0.08 | frontmatter `name` == dir; valid YAML; no broken reference links; body matches the description; version/refs accurate. |

Weights sum to `1.00`. The weighted sum is the **composite** (for the
scoreboard/trend). The **PASS test** is `min(dimension_scores) ≥ 0.90` (every
dimension), NOT the composite — see `skill_grade.py`.

## Required judge output (STRICT JSON, nothing else)

```json
{
  "dimensions": {
    "description_quality": 0.0,
    "trigger_coverage": 0.0,
    "progressive_disclosure": 0.0,
    "workflow_clarity": 0.0,
    "examples": 0.0,
    "constraints_gates": 0.0,
    "token_efficiency": 0.0,
    "coherence_correctness": 0.0
  },
  "min": 0.0,
  "composite": 0.0,
  "notes": "1-3 sentences: the single weakest dimension and why."
}
```

- `min` = the minimum of the 8 dimension scores.
- `composite` = weighted sum using the weights above (description_quality .18,
  trigger_coverage .16, progressive_disclosure .12, workflow_clarity .14,
  examples .12, constraints_gates .12, token_efficiency .08,
  coherence_correctness .08).
- The judge sub-agent must return the JSON as TEXT (Shannon hooks may block a
  sub-agent from writing report files); the orchestrator writes
  `.skills10x/<skill>/rubric-<phase>.json`, which `skill_grade.py` consumes.

## Dispatch note (headless `claude -p`)

The `Skill` tool is DISABLED in headless `claude -p`. Do NOT grade by invoking a
skill-judge skill. Grade via a `Task` sub-agent fed THIS rubric inline. Read 2–3
already-strong skills (e.g. `functional-validation`, `plan-author`) first to
calibrate the house style before judging.
