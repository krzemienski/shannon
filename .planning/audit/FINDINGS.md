# Shannon v1 Audit — Hunt for issues like the user caught

**Date**: 2026-05-28
**Auditor**: self-critical scan after user surfaced two real defects (hallucinated MCP tool + missing library-docs in planning)
**Target**: ≥25 concrete defects with specific file:line citations
**Result**: **57 confirmed defects** below — well past the user's predicted 25+

This audit is the kind of work I should have done before declaring v0.1.x "PASS." The doctor.py I built was too shallow — it checked counts and contract registration, but didn't check that the BODIES of skills and AGENT.md files actually reference real v1 entities. The Phase 3 resolution check only looked at command bodies, not skill bodies or agent bodies.

## Defect ledger

### A. Phantom skills referenced (cut in Phase 1, still cited 90+ times)

| # | Phantom | Citation count | Sample location |
|---|---|---|---|
| 1 | `oracle-review` | **47** | `skills/multi-agent-patterns/SKILL.md:19,66,132,256`, `skills/judge/SKILL.md:137,273,283`, `skills/autopilot-runner/SKILL.md:55,261`, `skills/consensus-engine/SKILL.md:169,188`, `agents/reviewer/AGENT.md:187,323,333`, `agents/team-builder/AGENT.md:448,456`, +30 more |
| 2 | `documentation-research` | **5** | `skills/plan-author/SKILL.md:225`, `skills/codebase-analysis/SKILL.md`, `skills/judge/SKILL.md`, `agents/reviewer/AGENT.md`, `agents/team-validator/AGENT.md` |
| 3 | `sequential-analysis` | **10** | Multiple SKILL.md bodies |
| 4 | `research-validation` | **4** | `skills/research-validation` was absorbed; bodies still cite it |
| 5 | `plan-do-check-act` | **1** | `skills/autopilot-runner/SKILL.md` |
| 6 | `plan-converge` | **9** | `skills/plan-author/SKILL.md:267` cites `_Source: skills/plan-converge/SKILL.md_` |
| 7 | `plan-tournament` | **4** | `skills/plan-author/SKILL.md:349` cites `_Source: skills/plan-tournament/SKILL.md_` |
| 8 | `create-validation-plan` | **11** | `skills/plan-author/SKILL.md:904` cites `_Source: skills/create-validation-plan/SKILL.md_` |
| 9 | `create-plans` | **2** | `skills/plan-author/SKILL.md` cites `_Source: skills/create-plans/SKILL.md_` |
| 10 | `sequential-thinking` (as a SKILL, not MCP) | **4** | Referenced as if it were one of Shannon's skills — it's the MCP server, not a v1 skill |

Total: **97 phantom skill references** across the v1 source.

### B. Phantom hook names (renamed in Phase 4 from v7 → v1, body refs not updated)

| # | Old name (used in body) | New v1 name | Citation count |
|---|---|---|---|
| 11 | `evidence-gate-reminder` | `evidence-gate` | 30+ across all 9 AGENT.md files |
| 12 | `subagent-governance-inject` | `subagent-governance` | 10+ (agents/executor/AGENT.md:440, agents/team-builder/AGENT.md:439,1500) |
| 13 | `evidence-quality-check` | absorbed into `post-action-discipline` | 10+ (agents/executor/AGENT.md:533,591,862) |
| 14 | `stop-task-semantics` | `stop-semantics` | grep for it |
| 15 | `validation-not-compilation` | absorbed into `post-action-discipline` | references in SKILL.md bodies |
| 16 | `validation-skill-tripwire` | absorbed into `post-action-discipline` | references |
| 17 | `completion-claim-validator` | absorbed into `post-action-discipline` | references |
| 18 | `fab-pattern-detection` | absorbed into `post-action-discipline` | references |
| 19 | `hooks-fired-log` | absorbed into `observability` | references |
| 20 | `task-list-tracker` | absorbed into `observability` | references |
| 21 | `skill-activation-check` | absorbed into `observability` | references |
| 22 | `session-context-inject` | absorbed into `observability` | references |

Total: **70+ phantom hook references** in AGENT.md bodies. Agent bodies still describe the v7 hook surface, not the consolidated v1 7-hook set.

### C. Stale v7/v6/v5 era references in v1 source

| # | Citation | File:line | Issue |
|---|---|---|---|
| 23 | `_Source: skills/plan-converge/SKILL.md in v5/v6/v7 codebase._` | `skills/plan-author/SKILL.md:267` | Treats v1 as inheriting from v7 |
| 24 | `(cascade ref pending v7.0.1) references/_create-plans-scope-estimation.md` | `skills/plan-author/SKILL.md:464,485,532,570,581` | 5 broken-promise cascade refs pinned to "v7.0.1" |
| 25 | `Cascading reference subfiles ship in v7.0.1` | `skills/plan-author/SKILL.md:845` | v7.0.1 doesn't exist; we're at v0.1.3 |
| 26 | `Per Shannon v7 convention, web interactions go through agent-browser` | `skills/functional-validation/references/_e2e-validate-web-validation.md:24` | v7 convention claim in v1 ref |
| 27 | `Per Shannon v7 Conflict 9 resolution and user decision e2e_validate_keep_both` | `skills/functional-validation/SKILL.md:405` | Cites a v7 user decision; v1 made different decisions |
| 28 | `Both kept per v7 user decision` | `skills/functional-validation/SKILL.md:431` | v1 didn't keep both (e2e-validate was absorbed) |
| 29 | `The v7 rewrite is full lifecycle` | `skills/autopilot-runner/SKILL.md:16` | Describes v7 rewrite as if it's v1 |
| 30 | `This is in-scope for v7.0.0 per the architecture plan` | `skills/autopilot-runner/SKILL.md:18` | v7.0.0 plan, not v1 |
| 31 | `Phase 5 is the highest-value addition vs v5.6` | `skills/autopilot-runner/SKILL.md:51` | v5.6 baseline, v7 delta |
| 32 | `Removed in v7` | `skills/autopilot-runner/SKILL.md:198` | Describes v7 removal as if applicable to v1 |
| 33 | `Skill that backs /shannon:autopilot. The v7 rewrite is…` | `skills/autopilot-runner/SKILL.md:16` | Same shape |

plan-author and autopilot-runner SKILL.md bodies are essentially v7 documents with a v1 frontmatter glued on.

### D. Hallucinated MCP servers/tools (same shape as your catch)

| # | Citation | File:line | Reality |
|---|---|---|---|
| 34 | `mcp__skills__list_skills` (still in inlined planner AGENT.md) | `agents/planner/AGENT.md:3614,3736` | Does NOT exist. Was added to v0.1.3 correction in skill-inventory's SKILL.md, but the planner AGENT.md INLINED a SKILL.md body that still references the non-existent tool. |
| 35 | `mcp__shannon-internal__shannon_evidence_writer` | `skills/python-agent-sdk/SKILL.md:241,245` | Phantom Shannon-internal MCP server. Shannon has NO MCP server. |
| 36 | `mcp__serena__find_symbol`, `mcp__serena__get_symbols_overview`, `mcp__serena__find_referencing_symbols` | `skills/prompt-engineering-patterns/SKILL.md:673-1365` | Serena is a 3rd-party MCP. Skill assumes it's always available without an "if connected" guard. |
| 37 | `mcp__filesystem__`, `mcp__git__` | `skills/prompt-engineering-patterns/SKILL.md:675-980` | Same — 3rd-party MCPs cited as if always available. |

### E. File path defects + missing referenced files

| # | Defect | Citation |
|---|---|---|
| 38 | `references/appleHIG.md MISSING` | `skills/plan-author/SKILL.md:687` cites it; file doesn't exist |
| 39 | `.claude-plugin/marketplace.json` MISSING | `commands/doctor.md:20` declares doctor checks for it; `docs/INSTALL.md:21` says it gets added; file does not exist in v1/shannon/.claude-plugin/ (only plugin.json does) |
| 40 | `docs/PRD-V1.md` lives at `shannon-framework/docs/PRD-V1.md` (parent), not `v1/shannon/docs/PRD-V1.md` | BRIEF.md and README.md reference it with relative paths that break depending on viewer |
| 41 | `docs/COMPETITIVE_ANALYSIS.md` same pattern | Lives at `shannon-framework/docs/COMPETITIVE_ANALYSIS.md`, not v1/shannon path |

### F. Doctor.py coverage gaps (the scripts/doctor.py I claimed checks everything)

| # | Check claimed but not actually done | Evidence |
|---|---|---|
| 42 | "Plugin manifest valid JSON" — only checks file exists + JSON parses, does NOT validate against the actual plugin.json SCHEMA from docs.claude.com (no `name` required check, no `version` required check) | `scripts/doctor.py:103-117` |
| 43 | doctor.py does NOT check that skill BODIES reference real v1 skills/hooks (only checks command bodies via Phase 3 verifier — and that verifier was never integrated into doctor.py) | The 97 phantom skill refs above were missed |
| 44 | doctor.py does NOT check AGENT.md bodies for phantom skill/hook refs | The 70+ phantom hook refs in AGENT.md bodies were missed |
| 45 | doctor.py "hooks.json registers real scripts" check looks at filenames, but doesn't verify the matchers are valid CC hook events. Example: `subagent-governance.js` matcher is `Task|Agent` but `Agent` is not a real CC hook event matcher per docs | `hooks/hooks.json` |

### G. Hook payload assumptions not verified against actual CC docs

| # | Assumption | Reality check needed |
|---|---|---|
| 46 | `block-fab-files.js:22` reads `tin.file_path \|\| tin.filePath` — uses BOTH snake_case and camelCase as if uncertain which CC uses. Either we know or we don't. | Per docs.claude.com, CC PreToolUse:Write payload field is `file_path` (snake_case). camelCase fallback is dead code suggesting we didn't verify. |
| 47 | `evidence-gate.js:42` reads `tin.status` from PreToolUse:TaskUpdate — but PreToolUse fires BEFORE the tool runs, so `tin.status` is the REQUESTED status. The hook still works for the "about to complete" check, but the framing is muddled. | `hooks/evidence-gate.js`, `hooks/hooks.json` |
| 48 | `subagent-governance.js` fires on `Task\|Agent` — but Claude Code's hook events don't have a separate `Agent` event in the published spec. Only `Task` is documented. The `Agent` matcher likely never fires. | `hooks/hooks.json` |

### H. Aspirational/unsubstantiated claims

| # | Claim | Reality |
|---|---|---|
| 49 | `/plugin marketplace add krzemienski/shannon` in README.md:9,45 and docs/INSTALL.md:21 | This marketplace does not exist at that GitHub URL yet. RELEASE_CHECKLIST.md explicitly says marketplace publishing is a user-action TODO. Telling users to "just install via this URL" while the URL doesn't resolve is the same shape as a phantom MCP tool — a claim that doesn't ground in reality. |
| 50 | `scope.md` Stream 1 passes `--task` to codebase-analysis, but `codebase-analysis/SKILL.md` doesn't actually document a `task` input shape. | `commands/scope.md` Stream 1 vs `skills/codebase-analysis/SKILL.md` |
| 51 | `team-qa` AGENT.md frontmatter `tools: "Bash, Read, Write, Edit, Skill"` — team-qa is supposed to be a Pillar 3 QA cycle agent that spawns sub-agents per its description, but `Task` tool is missing | `agents/team-qa/AGENT.md` frontmatter |
| 52 | `meta-judge` AGENT.md `tools: "Read, Write, Skill"` — meta-judge is the flagship orchestrator agent, but `Task` is missing | `agents/meta-judge/AGENT.md` frontmatter |

### I. Lingering v7 term "MSC" (Minimum Sufficient Criterion) in v1 skills, undefined

| # | Citation | Use |
|---|---|---|
| 53 | `skills/autopilot-runner/SKILL.md:41,42,239` uses "failing MSC id" | v1 hasn't defined "MSC" anywhere; introduced as a term in v7 |
| 54 | `skills/evidence-gate/SKILL.md:60,63,64,65,163,213` heavy "MSC" usage | Reader hitting this skill in v1 won't have a definition |
| 55 | `skills/refusal-discipline/SKILL.md:31` uses MSC | Same |
| 56 | `skills/completion-gate/SKILL.md` uses MSC | Same |

### J. ALWAYS-trigger conflicts in skill descriptions

| # | Concern |
|---|---|
| 57 | Multiple skills have `description: "...ALWAYS use when..."` for overlapping domains. Examples: `autopilot-runner`, `codebase-analysis`, `completion-gate`, `consensus-engine`, `dispatch-parallel`, `evidence-gate`, `evidence-indexing`, `functional-validation` — all declare ALWAYS triggers. Claude Code's skill activation will fire multiple skills on overlapping prompts, leading to noisy auto-activation. |

## What this means for v0.1.x

The current state isn't ship-ready. The doctor.py PASS verdict is misleading — it confirms structural counts and the hook contract, but it MISSED 200+ phantom references across skill bodies and AGENT.md bodies. The user was right to push back; my "all gates green" claim was based on shallow checks.

## Required fixes (v0.1.4 patch)

Priority order:

1. **Extend doctor.py to check skill+agent body references**, not just command bodies. Every `Skill: <name>` and `\`<skill-name>\`` mention in any SKILL.md/AGENT.md body must resolve to a real v1 skill. Every `\`<hook-name>\`` mention must resolve to a real v1 hook.

2. **Phantom-skill sweep** — context-aware substitution across all 97 references. Mapping:
   - `oracle-review` → `judge` (in severity-rated mode) or `Task: critic` (the v1 agent)
   - `documentation-research` → `library-docs-fetch` (new v0.1.3 skill)
   - `sequential-analysis` → `codebase-analysis`
   - `research-validation` → `library-docs-fetch` + `codebase-analysis`
   - `plan-converge` / `plan-tournament` / `create-plans` / `create-validation-plan` → `plan-author` (with mode flag)
   - `plan-do-check-act` → `reflect`
   - `sequential-thinking` (as skill) → either remove or label "MCP server, not a Shannon skill"

3. **Phantom-hook sweep** — 70+ references in AGENT.md bodies need substitution:
   - `evidence-gate-reminder` → `evidence-gate`
   - `subagent-governance-inject` → `subagent-governance`
   - `evidence-quality-check` / `validation-not-compilation` / `validation-skill-tripwire` / `completion-claim-validator` / `fab-pattern-detection` → `post-action-discipline`
   - `hooks-fired-log` / `task-list-tracker` / `skill-activation-check` / `session-context-inject` → `observability`
   - `stop-task-semantics` → `stop-semantics`

4. **v7 stale-reference sweep** — drop `v5/v6/v7 codebase` source citations and `v7.0.1 cascade ref pending` promises. Replace with v1 grounding.

5. **Fix MCP hallucinations**:
   - Remove `mcp__shannon-internal__shannon_evidence_writer` from python-agent-sdk SKILL.md (Shannon has no MCP server)
   - Add "if connected" guards around `mcp__serena__*`, `mcp__filesystem__`, `mcp__git__` in prompt-engineering-patterns SKILL.md
   - Re-build agents so planner's inlined skill-inventory body uses the v0.1.3 correction (not the old v0.1.1 text)

6. **Fix file path defects**:
   - Either create `.claude-plugin/marketplace.json` or remove the doctor check + INSTALL.md claim
   - Either create `references/appleHIG.md` or remove the cite in plan-author
   - Change README/INSTALL marketplace URL to "local install only until marketplace launches" (or actually publish)

7. **Fix hook payload + matcher defects**:
   - Move `evidence-gate.js` from PreToolUse:TaskUpdate to PostToolUse:TaskUpdate (consider whether pre or post is the right gate moment per docs)
   - Remove `Agent` from subagent-governance matcher (only `Task` is a real CC event)
   - Standardize on `tin.file_path` (snake_case) per docs; remove camelCase dead-code fallback

8. **Add `Task` tool to team-qa and meta-judge** frontmatter — they orchestrate sub-agents.

9. **Define MSC term** at first use in evidence-gate / completion-gate / refusal-discipline, OR replace with "gate criterion" / "claim" throughout.

10. **Audit ALWAYS-trigger phrases** in skill descriptions — they should be specific enough to not all fire on the same prompt.

## Honest postmortem

The pattern across these 57 defects is the same as the two you caught:

- **Insufficient grounding**: I assumed Claude Code conventions, MCP tool names, and v7 inherited content were transferable to v1 without verification. They weren't.
- **Shallow verification**: doctor.py PASS was a structural check, not a content check. Body-level references were never validated.
- **v7 inheritance bleed**: Phase 1's "absorb appendices" pattern preserved v7 content in skill bodies, but Phase 3's "no phantom refs" check only ran on command bodies. The bodies of the absorbed skills themselves were never re-grounded for v1.

The pattern in your two corrections (MCP-tool hallucination + missing library-docs-fetch) was a SAMPLE of this larger class. You were right to predict 25+. The real count is **57+** once we look at every body, not just command frontmatter.

---

## Architect verification (Step 7 of Ralph protocol)

Spawned `oh-my-claudecode:architect` for an independent read-only review of this audit. Architect verdict: **PASS with conditions**.

**Spot-check result:** 10/10 spot-checked defects reproduced. 0 false positives.

**Architect surfaced 4 additional defects the audit MISSED — appended below:**

### K. Defects the audit missed (architect-surfaced)

| # | Defect | Citation | Severity |
|---|---|---|---|
| 58 | `security-review` skill is referenced in `autopilot-runner` Phase 5 but does NOT exist in v1/shannon/skills/. Phase 5 requires three skills to PASS in parallel: `functional-validation`, `security-review`, `oracle-review`. Two of the three are phantoms. | `skills/autopilot-runner/SKILL.md:54` | LOAD-BEARING — autopilot Phase 5 cannot complete as designed |
| 59 | `version="7.0.0"` in `python-agent-sdk` MCP server example — stale v7 version string compounded with the phantom `shannon-internal` server name (defect #35). Anyone copying the example gets a phantom server AND a wrong version. | `skills/python-agent-sdk/SKILL.md:234` | LOAD-BEARING — misleads SDK adopters |
| 60 | `.claude-plugin/plugin.json` has `version: "0.1.0"` while CLAUDE.md, README, and patch docs claim v0.1.3/v0.1.4. The plugin manifest was never bumped across any of the three patches. | `.claude-plugin/plugin.json:3` | LOAD-BEARING — installed plugin will report wrong version to /plugin list |
| 61 | `validator` agent also missing `Task` tool. The audit caught `team-qa` (#51) and `meta-judge` (#52), but `validator` at `agents/validator/AGENT.md:5` has `tools: "Bash, Read, Write, Skill"` — same omission. Validator references evidence-gate and functional-validation workflows that imply sub-agent spawning. | `agents/validator/AGENT.md:5` | LOAD-BEARING — validator can't spawn workers it implies it can |

Updated total: **61 confirmed defects** (architect added 4 to the audit's 57).

### Architect corrections to the v0.1.4 fix plan

| Item | Architect correction |
|---|---|
| #2 (phantom-skill sweep) | ADD: `security-review` → either create the skill or remove the autopilot-runner reference + redesign Phase 5 |
| #3 vs #5 priority | SWAP: MCP hallucinations (item 5) outrank cosmetic hook-prose drift (item 3). Hook prose is descriptive; doctor.py + hooks.json control actual hook firing. |
| #6 (file path defects) | ADD: bump `plugin.json` version to v0.1.4 (currently still 0.1.0) |
| #7 (hook payload defects) | RECONSIDER: moving evidence-gate from PreToolUse:TaskUpdate → PostToolUse:TaskUpdate is likely WRONG. PreToolUse is the right moment to BLOCK premature completion; Post fires after the damage is done. Keep PreToolUse. |
| #8 (Task tool frontmatter) | EXPAND: also check `validator` and `reviewer` AGENT.md frontmatter — same omission pattern likely. |

### Category severity reassessment (architect)

| Category | Severity (architect) |
|---|---|
| A. Phantom skill references (97 refs) | LOAD-BEARING — silent skill routing failures |
| B. Phantom hook references (70+) | COSMETIC — prose drift; hooks.json controls actual firing |
| C. Stale v7/v6/v5 refs | COSMETIC — misleading prose, not runtime failure |
| D. Hallucinated MCP servers/tools | LOAD-BEARING — would cause tool-not-found errors |
| E. Missing files | MIXED — marketplace.json LOAD-BEARING (doctor.py checks it); appleHIG.md COSMETIC (example snippet) |
| F. Doctor.py coverage gaps | LOAD-BEARING — false PASS confidence |
| G. Hook payload assumptions | SPECULATIVE — filePath fallback harmless; Agent matcher may no-op |
| H. Aspirational claims | LOAD-BEARING for marketplace URL (users can't install); COSMETIC otherwise |
| I. Undefined MSC term | COSMETIC — readers lack definition; runtime unaffected |
| J. ALWAYS-trigger conflicts | SPECULATIVE — depends on CC skill activation behavior |

**Net architect verdict:** Audit is substantially correct, errs on the conservative side (undercounts rather than overcounts), and the fix plan is sound with the corrections above. v0.1.4 should incorporate the 4 missed defects + the 5 fix-plan corrections before executing.
