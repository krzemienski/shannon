# Summary — Plan 02-01

**Output**: `embedding-map.md` — the central design decision for Architecture C.

## Headline

- **9 agents** for v0.1.0 with explicit role + priority per agent
- **21 unique embedded skills** (of 31 curated set)
- **32 total embedding relationships** across the 9 agents
- **0 cascade conflicts** — simplifies build script (Plan 02-02)
- **10 skills remain standalone-only** — invokable via `Skill:` but not in any agent's `_built/` payload

## Surprises

1. **Zero cascade conflicts** — Phase 1's prefix-rewrite logic isn't needed at the build-script level. The 76 prefix-rewritten refs from Phase 1 were APPENDIX-internal (within a single survivor SKILL.md). At the agent-build level, each agent embeds disjoint skill sets that don't share `references/` filenames.

2. **Duplication is concentrated** — only 6 of 21 unique embedded skills appear in 2+ agents. The rest are single-agent. Total agent context budget impact is bounded.

3. **meta-judge needs only 2 embedded skills** — the agent body itself carries the rubric-generation logic; embedded skills are just for the downstream judge/consensus operations the agent invokes. This is intentional Architecture C minimalism.

## Where Plan 02-01 stops

Plan 02-01 produces a DECISION DOCUMENT. It does NOT:
- Write `manifest.yml` per agent (Plan 02-02)
- Write `build/embed-skills.py` (Plan 02-02)
- Create `agents/<name>/_built/` directories (Plan 02-03)
- Mutate any file under `agents/` (deferred to Plan 02-02+)

This is intentional — Architecture C decisions are high-leverage and should not be applied without explicit user approval.

## What unblocks Plan 02-02

User reviews `embedding-map.md` and either:

**Approve as-is** — replace `## Approval status: PENDING` with `## Approval status: APPROVED 2026-MM-DD`. Plan 02-02 starts.

**Adjust specific decisions** — name which of Q1-Q5 you want to change:
- Q1: agent set (9 kept; consider 7 lean or 10 bold)
- Q2: meta-judge minimal embedding (2 skills)
- Q3: team-validator vs validator overlap
- Q4: standalone-only set (10 skills, including loop-runner/autopilot-runner)
- Q5: duplication acceptability (~50KB per agent's _built/)

**Ask for more analysis** — loop back into Plan 02-01 with specific questions

## Done condition met

✓ embedding-map.md on disk (256 lines, 9 agents, 32 embed relationships, 0 conflicts)
✓ All 7 gate criteria PASS
✓ Open questions surface user-decision points
✓ Plan 02-02 correctly blocked pending user approval

## Forward-looking notes for Plan 02-02

When user approves and Plan 02-02 starts, the work is:
1. For each of 9 agents, write `agents/<name>/manifest.yml` per the approved map
2. Write `build/embed-skills.py` — straight copy (no prefix logic needed per cascade-conflicts finding)
3. Write `build/verify-build.py` — sanity check
4. Test on one agent (meta-judge — simplest, 2 skills) before running all

Plan 02-03 then executes the build for all 9 agents + smoke test (delete a standalone skill, spawn agent, verify it still has its skills).

Estimated effort for Plans 02-02 + 02-03: similar to Plan 01-03 (substantial but mechanical).
