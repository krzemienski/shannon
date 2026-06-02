# Shannon v1.2.0 — Usage Guide (forge · DeepPlan · self-improve harness)

How to invoke the v1.2 additions and how the subsystems connect. For the full component list see `docs/registry.md`; for install see `docs/INSTALL.md` / `docs/QUICK_START.md`.

## 1. The completion pipelines — `cook` vs `forge`

Shannon has two end-to-end pipelines. Pick by rigor:

| | `/shannon:cook` | `/shannon:forge` |
|---|---|---|
| Phases | 5 (plan → execute → validate → gate) | 10 (adds docs-research, oracle plan-review, evidence-indexing, reviewer consensus, oracle quorum) |
| Gates | evidence-gate + completion-gate | + oracle quorum (pre & post) + reviewer consensus |
| Use when | normal feature work | high-stakes / must survive adversarial audit |
| Refusal | yes | yes (no `--force`) |

```bash
/shannon:cook "Add rate-limiting to the API"
/shannon:forge "Add OAuth2 with PKCE to web client" --mode consensus
/shannon:forge plans/260523-feature-x/        # run a pre-authored plan dir
```

**forge data flow:** `codebase-analysis` → `documentation-research` → `plan-author` → `oracle-review` (plan, quorum ≥2/3) → `executor` agent → `functional-validation` → `evidence-indexing` → 3× `reviewer` (consensus) → `oracle-review` (evidence, quorum) → `completion-gate` → `evidence/completion-gate/report.json`. Any cited blocker → `refusal-discipline` writes `REFUSAL.md` and stops.

## 2. DeepPlan — `/shannon:plan --mode deep`

Restores the wave-orchestration planning depth. Flow:

```bash
/shannon:plan "Real-time collab editing with CRDT + presence" --mode deep
```

1. `deepplan-architect` agent runs `codebase-analysis` + `skill-inventory` (brownfield grounding).
2. `plan-author` produces the hierarchical phase plan.
3. tournament (N candidates) → converge (refine vs critic) → validation-gate injection.
4. `wave-execution` partitions the final plan into **dependency waves** (each wave = tasks whose `blockedBy` is satisfied).
5. `/shannon:cook` / `executor` then spawns each wave's agents **in one message** for true parallelism; a synthesis gate runs between waves.

Context is shared through the evidence tree + `.shannon/state/wave-context.md` (no Serena/Memory MCP — D3). Other modes: `linear` (default), `converge`, `tournament`.

## 3. Self-improve harness — `scripts/skills10x/`

Grades every skill with **real `claude -p` activation probes** + a judge sub-agent, improves the real `SKILL.md`, proves non-regression, and atomically commits each genuine win onto `skills/10x-<date>` (never main, never pushed).

```bash
cd /Users/nick/Documents/shannon
bash scripts/skills10x/run-skills10x.sh --dry-run            # baseline worst-first SCOREBOARD
bash scripts/skills10x/run-skills10x.sh --only <skill>       # one skill end-to-end
bash scripts/skills10x/run-skills10x.sh --max-global-passes 3  # full loop
```

A pass is accepted only when `f1≥0.90 AND rubric_min≥0.90 AND benched AND lift≥0.10 AND regression_guards==PASS AND diff touches only that SKILL.md`. Else: revert + retry. Full protocol: `scripts/skills10x/RUNBOOK.md`. State lands in gitignored `.skills10x/`.

## 4. Activation benchmark harness — `scripts/harness/`

Proves the opt-in skill-activation gate in real headless sessions:

```bash
SHANNON_DIR="$(pwd)" scripts/harness/drive-tests.sh
```

Per fixture it spawns a real `claude -p --plugin-dir` session and diffs `~/.claude/logs/shannon/hooks.jsonl`: `enabled` (`.shannon/active`) must FIRE; `unset`/`disabled` must NOT. `drive-tests-csd.sh` is the richer claude-session-driver variant. See `benchmarks/README.md`.

## 5. How the subsystems connect

```
commands/  →  agents/ (native skills:)  →  skills/  →  hooks/ (enforce)
   plan ──────→ deepplan-architect ──────→ wave-execution ─┐
   forge ─────→ executor + reviewer + ────→ oracle-review ──┤→ evidence/ ──→ completion-gate
                critic + validator         consensus-engine ┘        ↑
   (every TaskUpdate→completed) ── evidence-gate hook ───────────────┘
   (every Write/Edit) ── block-fab-files hook (Iron Rule: no test/mock files)
```

- **Agents** carry their skills via native `skills:` frontmatter (D8) — they cannot fail to load them.
- **Hooks** enforce the Iron Rule at the tool boundary (`block-fab-files` rejects `*.test.*`, mocks, stubs in scope).
- **Evidence** is the shared state: `/shannon:resume` reads the evidence tree to continue a halted forge/autopilot run; no separate state file.
- **skills10x** closes the loop — it grades and improves the very skills the agents inherit.
