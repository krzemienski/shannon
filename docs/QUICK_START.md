# Quick Start

Get from zero to first successful Shannon workflow in 10 minutes.

## Prereqs (~3 min)

1. Claude Code installed and running
2. This repo accessible at a local path (or installed from marketplace once published)
3. Python 3.10+ and Node 18+ on PATH

## Step 1: install + activate (~2 min)

```bash
# In Claude Code:
/plugin marketplace add /path/to/shannon-framework
/plugin install shannon@shannon-framework
```

Restart Claude Code, then:

```bash
/shannon:enforce on
/shannon:doctor
```

You should see all 8 checks PASS with `mismatches: 0`.

If not, see [docs/INSTALL.md#troubleshooting](INSTALL.md#troubleshooting).

## Step 2: write a small plan (~2 min)

```bash
/shannon:plan "Add a /health endpoint to the example service"
```

Shannon will:

1. Interview you briefly (3-phase intake from `interview-framework` skill)
2. Spawn the `planner` agent (which has `plan-author`, `interview-framework`, `goal-condition-architect`, `spec-workflow`, `create-meta-prompts`, `gepetto` embedded)
3. Write `plans/<date>-add-health-endpoint/plan.md` + `phase-01-*.md` files
4. Final phase is a validation phase with cited PASS criteria

## Step 3: execute the plan (~3 min)

```bash
/shannon:cook plans/<date>-add-health-endpoint/
```

Shannon will:

1. Spawn the `executor` agent (with `dispatch-parallel`, `functional-validation`, `reflect`, `codebase-analysis` embedded)
2. Per phase, route through `team-qa` for build/lint/test cycles
3. Capture evidence under `e2e-evidence/<run-id>/<journey>/`
4. Run the `evidence-gate` skill before claiming complete
5. Run the `completion-gate` skill as the final mechanical check

If any gate fails, you'll see a `REFUSAL.md` with specific blockers — never a fabricated PASS.

## What just happened?

Shannon's 5 pillars in one workflow:

1. **Embedded sub-agent skills** — `planner` and `executor` had their skill content baked into AGENT.md by `build/embed-skills.py`. They didn't need to invoke `Skill: plan-author` at runtime — the content was already in their spawn context.
2. **Orchestration** — `cook` routes through `planner` → `executor` → `team-qa` → `evidence-gate`. Each handoff uses single-message dispatch.
3. **Iron Rule validation** — `block-fab-files` refused any `tests/foo.test.js` Write your work might have attempted. `post-action-discipline` flagged any 0-byte evidence files. `post-action-discipline` reminded that build success ≠ functional pass.
4. **Meta-judge consensus** — `cook` didn't engage it directly, but `/shannon:plan --mode tournament` would have spawned `meta-judge` to generate the rubric for ranking plan candidates.
5. **Self-instrumented** — `/shannon:doctor` validates the contract; `/shannon:trace` shows you the timeline.

## Next steps

- Read [docs/ARCHITECTURE.md](ARCHITECTURE.md) to understand Architecture C and the 5 layers.
- Read [docs/FUNCTIONAL_VALIDATION_GUIDE.md](FUNCTIONAL_VALIDATION_GUIDE.md) to understand the Iron Rule deeply.
- Browse [docs/SKILLS_CATALOG.md](SKILLS_CATALOG.md) to see the 33 curated skills and when they activate.
- For your next plan, try `/shannon:plan --mode converge` (iterative refinement) or `/shannon:plan --mode tournament` (multi-perspective candidates).

## When Shannon refuses

Shannon will refuse to claim COMPLETE if:

- Any gate (`evidence-gate`, `completion-gate`) cannot find specific cited evidence
- Any tool call attempted to create a test file or mock (`block-fab-files` blocks)
- Any TaskUpdate to `status=completed` happens without fresh evidence in the last 30 min

These are features, not bugs. If you're stuck:

1. `cat REFUSAL.md` to see exactly what blocker the gate cited
2. Add the missing evidence (real screenshot, real curl output, real CLI run)
3. Re-run the failing phase

## Common patterns

| Want to... | Try... |
|---|---|
| Brainstorm a feature before planning | `/shannon:prd "feature description"` |
| Validate an existing feature works | `/shannon:validate --mode standard` |
| Find why something broke | `/shannon:why "symptom description"` |
| Audit current code state vs plan claims | `/shannon:audit --scope drift --days 7` |
| Recover from a halted cook run | `/shannon:resume --run-id <id>` |
| Get a weekly retrospective | `/shannon:retro --days 7` |
| Trace what hooks fired in this session | `/shannon:trace` |

## Cross-references

- [docs/INSTALL.md](INSTALL.md) — prerequisites + install
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — how it works internally
- [docs/SKILLS_CATALOG.md](SKILLS_CATALOG.md) — every skill, indexed
- [docs/FUNCTIONAL_VALIDATION_GUIDE.md](FUNCTIONAL_VALIDATION_GUIDE.md) — Iron Rule
