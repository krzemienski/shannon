# Shannon v0.1.0 — Skill Curation Proposal (REVISED — AGGRESSIVE MERGE)

## Approval marker

**USER APPROVED 2026-05-28** — "You're allowed to merge what you're allowed to merge together."

Aggressive merge pass absorbing additional duplicate clusters. Decisions:
- Prompt-engineering: collapse to `prompt-engineering-patterns` ✓
- Goal-*: collapse to `goal-condition-architect` + `goal-loop-orchestrator` ✓
- iOS-validation-runner: CUT (domain-specific) ✓
- Adjacent-aggressiveness: resolved via merge instead of cut ✓
- Final count: 31 (in BRIEF range 25-35) ✓

Status: ✅ APPROVED — Plan 01-03 executes against this proposal

---

## Summary

- Total inherited: 67
- KEEP survivors (absorb others): 17
- KEEP pure (no absorbing): 14
- KEEP total: **31**
- CUT: 4
- Absorbed via MERGE: 32
- Sum: 67 = 67 ✓
- vs BRIEF target (25-35): ✅ in range

---

## MERGE table (17 survivor groups, 32 absorbed)

| survivor | absorbs | rationale |
|---|---|---|
| `autopilot-runner` | `autopilot` | absorbs autopilot mode-variant |
| `codebase-analysis` | `sequential-analysis`, `research-validation`, `documentation-research` | absorbs sequential + research + docs analysis |
| `completion-gate` | `transform-validation-prompt` | absorbs prompt-injection gate variant |
| `create-meta-prompts` | `deepen-prompt-plan` | absorbs deepen variant |
| `evidence-gate` | `verification-before-completion`, `reality-verification`, `gate-validation-discipline` | absorbs verification + reality + gate-discipline into canonical gate |
| `full-functional-audit` | `full-ui-experience-audit` | absorbs UI-specific audit |
| `functional-validation` | `e2e-validate` | absorbs e2e-validate (platform-routing variant) |
| `goal-condition-architect` | `northstar`, `goal-engineering`, `condition-library` | absorbs northstar + goal-engineering + condition-library |
| `goal-loop-orchestrator` | `goal-orchestration`, `goal-workflow` | absorbs goal-orchestration + goal-workflow |
| `judge` | `critique`, `oracle-review` | absorbs critique (severity) + oracle (pre-execution) as modes |
| `loop-runner` | `ralph`, `plan-do-check-act` | absorbs ralph + PDCA pattern |
| `memorize` | `consolidate-memory`, `lesson-learned` | absorbs consolidate-memory + lesson-learned |
| `multi-agent-patterns` | `subagent-driven-development` | absorbs subagent-driven-dev discipline |
| `no-fakes-discipline` | `no-mocking-validation-gates` | absorbs validation-gates variant |
| `plan-author` | `plan-converge`, `plan-tournament`, `create-plans`, `create-validation-plan` | absorbs converge/tournament/create/validation-plan variants |
| `prompt-engineering-patterns` | `prompt-engineer`, `prompt-improver`, `optimize-prompt` | canonical reference; absorbs 3 single-prompt variants |
| `spec-workflow` | `prd-clarity` | absorbs prd-clarity |

## Pure KEEPs (14)

| skill | why |
|---|---|
| `consensus-engine` | 5-state synthesis table; distinct from judge |
| `dispatch-parallel` | single-message multi-Task enforcer; canonical |
| `evidence-indexing` | Shannon-unique INDEX.md traversal; no overlap |
| `gepetto` | multi-LLM external review; unique |
| `interview-framework` | 3-phase intake; pairs with autopilot |
| `observability-report` | /shannon:trace + doctor entry-point |
| `python-agent-sdk` | foundational SDK for harnesses |
| `reflect` | meta-skill; distinct from learner/memorize |
| `refusal-discipline` | Shannon-unique REFUSAL.md artifact; no overlap |
| `root-cause-tracing` | 5-whys + Ishikawa; distinct from codebase-analysis |
| `session-handoff` | cross-session continuity; distinct |
| `team-coordinator` | staged team pipeline; canonical |
| `tree-of-thoughts` | 8-phase exploration; distinct pattern |
| `visual-inspection` | WCAG/HIG checklist; distinct from validation |

## CUT (4)

| skill | reason |
|---|---|
| `ios-validation-runner` | iOS-specific; defer to v1.x |
| `communication-style` | niche style guide; absorb into docs if needed |
| `brainstorm` | adjacent ideation; not a pillar |
| `create-ideas` | duplicate of brainstorm |

## Reversibility

All CUT and absorbed skills remain in `shannon-framework/skills/` (parent). Plan 01-03 copies KEEPs to `v1/shannon/skills/`. Absorbed bodies appended as `## Absorbed from <name>` sections for Phase 2 canonical-merge work.
