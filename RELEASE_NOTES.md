# Shannon v0.1.1 — Release notes

**Date**: 2026-05-28
**Status**: Release candidate (structural; brownfield-planning patch applied). User-action steps: see `RELEASE_CHECKLIST.md`.

## What is this release

Shannon v0.1.0 is the foundational scaffold of the framework — the smallest interesting surface that delivers the 5 pillars on disk:

1. Embedded sub-agent skills (Architecture C)
2. Orchestration (single-message multi-Task dispatch)
3. Iron Rule validation (no mocks, no stubs, no `*.test.*` files)
4. Meta-judge consensus (rubric YAML before any judge)
5. Self-instrumented (`scripts/doctor.py` mechanical contract check)

## What's in the box

| Layer | Count | Files |
|---|---|---|
| Skills | **32** | `skills/<name>/SKILL.md` + `references/*.md` |
| Agents | **9** | `agents/<name>/manifest.yml` + `AGENT.md` + `_built/skills/` |
| Commands | **20** | `commands/*.md` |
| Hooks | **7** | `hooks/*.js` + `hooks.json` + `_lib.js` |
| Build scripts | **3** | `build/embed-skills.py`, `build/verify-build.py`, `build/README.md` |
| Doctor | **1** | `scripts/doctor.py` |
| Harness | **5** | `scripts/harness/sdk_runner.py`, `tmux_runner.py`, `lib.py`, `run-all.sh`, `benchmarks/*.yml` (×5) |
| Docs | **8** | README.md + `docs/*.md` (INSTALL, QUICK_START, SKILLS_CATALOG, ARCHITECTURE, FUNCTIONAL_VALIDATION_GUIDE, CONTRIBUTING, DEV_HARNESS) |

## Headline metrics

- **34 embedding relationships** across the 9 agents (23 unique skills embedded)
- **0 cascade conflicts** — build uses straight copy + AGENT.md inlining
- **0 phantom references** across 19 commands × 31 skills × 9 agents × 7 hooks
- **0 doctor mismatches** (8/8 checks PASS)
- **5/5 pillar benchmark coverage** in harness
- **0 broken internal doc links**
- **0 forbidden Iron Rule patterns** (`*.test.*`, `mock_*`, etc.) in `scripts/harness/`

## Phase-by-phase build evidence

| Phase | Output | Verdict |
|---|---|---|
| 0 PRD approval | `docs/PRD-V1.md`, `DECISIONS.md`, `BRIEF.md`, `ROADMAP.md` | PASS |
| 1 Skill curation (67→31) | `skills/` (31 dirs); `cut-skills.md`; `KEEP_PROPOSAL.md` USER APPROVED | PASS |
| 2 Agent embedding (Architecture C) | `agents/` (9 manifests + AGENT.md + `_built/`); `build/embed-skills.py`; `embedding-map.md` APPROVED | PASS |
| 3 Command consolidation (27→19) | `commands/` (19); `cut-commands.md`; 0 phantom refs | PASS |
| 4 Hook curation (16→7) + contract | `hooks/` (7); `hooks.json`; 8 skills with `required_hooks`; `scripts/doctor.py` | PASS |
| 5 Validation harnesses | `scripts/harness/` (SDK + Tmux + 5 benchmarks); `docs/DEV_HARNESS.md` | PASS |
| 6 Documentation (8 docs) | `README.md` + `docs/*.md`; 0 broken links | PASS |
| 7 Release | (this file) + `RELEASE_CHECKLIST.md` + `FINAL_SUMMARY.md` | STRUCTURAL PASS |

Each phase's full validation evidence is in `.planning/phases/<phase>/PHASE-*-VALIDATION.md`.


## v0.1.1 brownfield-planning patch

After v0.1.0 structural PASS, the user surfaced a capability gap: brownfield projects need a deep code survey + skill-inventory pass before planning. This patch closes it:

- **New command `/shannon:scope`** — read-only brownfield reconnaissance. Runs `codebase-analysis` (5 parallel scientists) + `skill-inventory` (runtime MCP-tool discovery) + `observability-report` (recent session context) in parallel via `Task: team-builder`; synthesizes a `scope-report.md` for downstream planning.
- **New skill `skill-inventory`** — calls `mcp__skills__list_skills` + `mcp__plugins__list_plugins` at runtime; maps installed capabilities to the task at hand. Refuses to fabricate recommendations.
- **`/shannon:plan --mode brownfield`** — auto-runs `/shannon:scope` first; plan cites specific files + specific skills + specific proving-commands.
- **`/shannon:cook --brownfield`** — same flow at the cook level; recommended for any non-trivial change on existing code.
- **`planner` agent** — now embeds `codebase-analysis` + `skill-inventory` (5 → 7 embedded skills); brownfield-survey is in the agent's spawn context.
- **37 stale `/shannon:forge` references swept** — context-aware substitution across 14 source files; 0 forge mentions remain.

See `.planning/patches/01-brownfield-planning.md` for the patch detail.

## What's intentionally NOT in v0.1.x

These were considered and deferred:

- **3-oracle quorum review** — the pre-execution + post-execution review from legacy forge. Approximated by `Task: critic` in v0.1.x; true 3-oracle quorum deferred to v1.x.
- **Agents `coordinator`, `oracle`, `researcher`, `red-teamer`, `dispatch-judge`** — absorbed into existing v1 agents (e.g., critic covers oracle + red-teamer; team-builder covers coordinator + researcher).
- **Github-based marketplace publishing** — v0.1.0 supports local-directory marketplace install. v0.2+ may add GitHub marketplace flow once the API surface stabilizes.
- **MCP-required workflows** — Context7 and sequential-thinking are recommended but not required. Other MCPs are deferred.
- **Live runtime validation in CI** — Phase 5 harness covers dry-run validation in sandboxes; live runs require user-action with Anthropic API access.

## Known limitations

1. **Local marketplace only.** Publishing to a GitHub-hosted marketplace is a v0.2+ enhancement.
2. **Live harness requires user-action.** The sandbox where v0.1.0 was built has no API access, so the live-mode harness runs are deferred to user execution per `RELEASE_CHECKLIST.md`.
3. **The SKILLS_CATALOG.md is hand-regenerated.** The Phase 6 script regenerates it from disk; in v1.x this could be promoted to a `scripts/sync-catalog.py` that runs on every doctor invocation.
4. **No CI integration.** v0.1.0 ships with the harness; CI wiring (GitHub Actions calling `bash scripts/harness/run-all.sh --live`) is a v0.2+ task.

## How to install

```bash
# Local install:
/plugin marketplace add /path/to/shannon-framework
/plugin install shannon@shannon-framework

# Restart Claude Code
/shannon:enforce on
/shannon:doctor       # expect 0 mismatches
```

See `docs/INSTALL.md` for details.

## How to verify the release

```bash
cd v1/shannon
python3 build/embed-skills.py        # exit 0
python3 build/verify-build.py        # mismatches: 0
python3 scripts/doctor.py            # mismatches: 0
bash scripts/harness/run-all.sh --dry-run   # both runners exit 0
```

All four must exit 0 with 0 mismatches. The release-candidate evidence is at `.planning/phases/07-release/evidence/`.

## Next: v0.2 (planned)

- Live harness execution as a CI step
- GitHub-hosted marketplace publishing
- Promote SKILLS_CATALOG.md generation to `scripts/sync-catalog.py`
- Re-evaluate `forge` command based on user feedback
- Re-evaluate `coordinator`, `oracle`, `researcher`, `red-teamer` as standalone agents based on usage signals

## Credits

Architecture C is the user's central design insight. The 5 pillars + 7-phase ROADMAP are grounded in v5/v6/v7 prototypes shipped in this repo + Anthropic's ecosystem (anthropic-skills, claude-code-guide, sadd, oh-my-claudecode). The aggressive-merge pattern across all phases was authorized by the user with the clarifying directive: "You're allowed to merge what you're allowed to merge together."

## License

MIT.
