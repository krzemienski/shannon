# Shannon v1.2.0 — Component Registry

> Full enumeration of commands, agents, and skills with the skill-inheritance map.
> Counts verified live against disk 2026-06-02: **21 commands · 11 agents · 36 skills · 8 hooks**.

## Commands (21)

`audit · autopilot · cook · dispatch · doctor · enforce · fix · forge ★ · install · loop · plan · prd · reflect · research · resume · retro · scope · team · trace · validate · why`

★ `forge` = added in v1.2.0 (10-phase evidence-gated pipeline). `plan` carries `--mode linear|converge|tournament|deep`; `deep` invokes `deepplan-architect` + `wave-execution`.

## Agents (11) + skill-inheritance map

All agents use native `skills:` frontmatter (D8). **Inheritance resolution: 0 dangling — every declared skill resolves to `skills/<name>/SKILL.md`.**

| Agent | Inherited skills | New in v1.2 |
|---|---|---|
| critic | judge, evidence-gate | |
| **deepplan-architect** | plan-author, codebase-analysis, skill-inventory, wave-execution | ★ |
| executor | dispatch-parallel, functional-validation, reflect, codebase-analysis | |
| meta-judge | judge, consensus-engine | |
| planner | plan-author, interview-framework, goal-condition-architect, spec-workflow, create-meta-prompts, codebase-analysis, skill-inventory, library-docs-fetch | |
| researcher | library-docs-fetch, codebase-analysis, observability-report | (D9) |
| reviewer | judge, codebase-analysis, root-cause-tracing | |
| team-builder | dispatch-parallel, multi-agent-patterns, team-coordinator | |
| team-qa | functional-validation, no-fakes-discipline, completion-gate, evidence-gate | |
| team-validator | judge, functional-validation, consensus-engine, visual-inspection, full-functional-audit | |
| validator | functional-validation, evidence-gate, evidence-indexing, refusal-discipline | |

## Skills (36)

New in v1.2.0 (★): `documentation-research`, `oracle-review`, `wave-execution`.

Planning: plan-author · goal-condition-architect · goal-loop-orchestrator · interview-framework · gepetto · spec-workflow · skill-inventory · create-meta-prompts · **wave-execution ★**
Completion/gates: completion-gate · evidence-gate · evidence-indexing · refusal-discipline · functional-validation · no-fakes-discipline · consensus-engine · **oracle-review ★**
Dispatch/teams: dispatch-parallel · multi-agent-patterns · team-coordinator · judge
Research/analysis: codebase-analysis · library-docs-fetch · observability-report · **documentation-research ★** · root-cause-tracing
Reflection: reflect · memorize · session-handoff
Audit/QA: full-functional-audit · visual-inspection
Patterns/runners: prompt-engineering-patterns · tree-of-thoughts · autopilot-runner · loop-runner · python-agent-sdk

## Hooks (8)

`block-fab-files · evidence-gate · observability · post-action-discipline · pre-edit-discipline · stop-semantics · subagent-governance` + `_lib.js` (shared). Registered via `hooks/hooks.json`.

## forge skill dependency chain (all resolvable)

`forge` → codebase-analysis ✓ · documentation-research ✓★ · plan-author ✓ · oracle-review ✓★ · functional-validation ✓ · evidence-indexing ✓ · consensus-engine ✓ · completion-gate ✓ · refusal-discipline ✓ · (executor agent for execute phase ✓)
