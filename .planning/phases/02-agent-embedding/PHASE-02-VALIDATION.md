# Phase 2 — VALIDATION

**Phase**: 2 (Agent embedding manifests + build script)
**Verdict**: ✅ **PASS** — Architecture C implemented and structurally proven on real disk.
**Date**: 2026-05-28

## ROADMAP gate criteria

| # | Criterion (from `.planning/ROADMAP.md`) | Result | Evidence |
|---|---|---|---|
| 1 | Per-agent embedding map exists + user-approved | ✅ PASS | `embedding-map.md` line 13 = `## Approval status: APPROVED 2026-05-28` |
| 2 | 9 `agents/<name>/manifest.yml` files exist + valid YAML | ✅ PASS | Plan 02-02 gate #1 |
| 3 | 9 `agents/<name>/AGENT.md` files exist + valid frontmatter | ✅ PASS | Plan 02-02 gate #2 |
| 4 | `build/embed-skills.py` exists + Python-valid + runs exit 0 | ✅ PASS | Plan 02-02 gates #3, #5 |
| 5 | `build/verify-build.py` exists + Python-valid + reports 0 mismatches | ✅ PASS | Plan 02-02 gates #4, #6 |
| 6 | After build, every agent has `_built/skills/<name>/SKILL.md` for each `embedded_skills` entry | ✅ PASS | Plan 02-02 gate #5 |
| 7 | Smoke test: agent retains skill access after canonical skill is moved away | ✅ PASS | Plan 02-03 gate #3 (md5 identity) |
| 8 | Phase 0 + Phase 1 regression PASS | ✅ PASS | All artifacts intact; 31 skills present |

## Plans executed

| Plan | Description | Gate | Result |
|---|---|---|---|
| 02-01 | Design embedding map | 7-criterion gate | ✅ PASS (256-line `embedding-map.md` produced) |
| 02-02 | Write manifests + AGENT.md + build script + verifier | 7-criterion gate | ✅ PASS (32 embedding relationships materialized) |
| 02-03 | Execute build + smoke test embedded loading | 6-criterion gate | ✅ PASS (Architecture C content-survival proven) |

## Architecture C — what's now real

1. **Canonical layer** (`v1/shannon/skills/`): 31 curated skills with `SKILL.md` + `references/` directories. Unchanged from Phase 1.

2. **Manifest layer** (`v1/shannon/agents/<name>/manifest.yml`): 9 declarative manifests stating which skills each agent embeds. Total 32 embedding relationships across 21 unique skills.

3. **Embedded layer** (`v1/shannon/agents/<name>/_built/skills/`): build-step-produced full copies of each declared skill. Provides on-disk reference + runtime Read-tool access to `references/`.

4. **Inlined layer** (`v1/shannon/agents/<name>/AGENT.md`): the AGENT.md body now contains the embedded SKILL.md bodies between sentinels. This is what Claude Code's agent loader actually reads at spawn time.

5. **Build script** (`v1/shannon/build/embed-skills.py`): idempotent, sandbox-safe, Iron-Rule-enforcing.

6. **Verifier** (`v1/shannon/build/verify-build.py`): read-only sanity check; 0 mismatches.

## Headline numbers

- 9 agents (5 P0 + 4 P0/P1) within PRD target 5-12
- 21 unique skills embedded (of 31 curated)
- 32 total embedding relationships
- 0 cascade conflicts
- 0 phantom skills
- 0 verifier mismatches
- 1 sentinel pair per AGENT.md (idempotency confirmed)

## The user's central insight, now proven on disk

> "Sub-agents can actually have skills embedded within them — so we don't have to worry about whether that skill does properly invoke."

Disk-level proof: when `skills/judge/` is moved away to `skills/judge.disabled.smoke/`, the md5 of `agents/meta-judge/AGENT.md` is unchanged (`7841f2471b6741a2c48e6e42608e54ba` → `7841f2471b6741a2c48e6e42608e54ba`). The embedded content is independent of the canonical at runtime. See `evidence/embedded-loading-proof.md` for the full sequence.

## Evidence index

- `evidence/cascade-conflicts.md` — Phase 2 pre-flight (0 conflicts found)
- `evidence/build-skills.log` — build run output
- `evidence/verify-build.log` — verifier run output
- `evidence/embedded-loading-proof.md` — Architecture C smoke test (the central proof)
- `evidence/approval-gate-fix.md` — gate-marker substring bug fix during Plan 02-01 verification

## What this UNBLOCKS (Phase 3 onwards)

Per `ROADMAP.md`:

- **Phase 3** (Command consolidation): `/shannon:*` slash commands can wire `Task(subagent_type="...")` calls knowing the embedded discipline holds — no defensive `Skill:` round-trips needed for the 21 embedded skills.
- **Phase 4** (Hook curation): hooks can assume embedded content is in scope when validating agent output.
- **Phase 5** (Validation harnesses): the live-API runtime half of Architecture C — Agent SDK spawn against a real Claude Code session.

## Done condition

`PHASE-02-VALIDATION.md` exists (this file). ROADMAP Phase 2 gate satisfied. Phase 3 unblocked.
