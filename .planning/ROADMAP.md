# Shannon v1 — ROADMAP

> 7 phases with blocking validation gates between each. Per `anthropic-skills:create-validation-plan` discipline: every phase has specific testable gate criteria; Phase N+1 prerequisites include "Phase N still passes" (regression check).

> **Iron Rule**: every gate is satisfied by real-system evidence captured to `.shannon/runs/<phase>/`. Mocks / stubs / test files explicitly prohibited.

---

## Phase 0 — PRD approval ✓ COMPLETE

**Goal**: Lock the architecture, decisions, and constraints before any code work.

### Tasks
- 0-01: Write PRD (`docs/PRD-V1.md` in parent)
- 0-02: Write competitive analysis (`docs/COMPETITIVE_ANALYSIS.md` in parent)
- 0-03: Capture user decisions (`DECISIONS.md`)
- 0-04: Scaffold v1 directory (this file is part of the scaffold)

### Phase 0 gate (PASS criteria)
- [x] PRD exists with all 15 sections complete
- [x] Competitive analysis covers all 5 ecosystem categories
- [x] DECISIONS.md captures 5 user calls (Architecture C, accept reductions, no Memory MCP, full Tmux coverage, keep `shannon` name + v0.x)
- [x] BRIEF.md grounds the work in the 5 pillars
- [x] This ROADMAP.md exists

### Evidence
- `../docs/PRD-V1.md` (469 lines)
- `../docs/COMPETITIVE_ANALYSIS.md` (413 lines)
- `DECISIONS.md` (captures the 5 calls)
- `BRIEF.md` (this directory)
- `ROADMAP.md` (this file)

**Verdict: PASS** ✓

---

## Phase 1 — Skill curation (67 → ~30)

**Goal**: Reduce the inherited 67 skills to the load-bearing ~30. Use the v7 audit (gap matrix, source provenance, cascade depth) as input.

### Tasks
- 1-01: Read `../docs/SKILLS_CATALOG.md` + `../.v7/skill-registry.json`; categorize each of the 67
- 1-02: Apply WINNING filter (load-bearing for v1 pillars vs noise)
- 1-03: Copy curated set from `../skills/<name>/` to `skills/<name>/` (this directory)
- 1-04: For each kept skill, update cascade `references/*.md` if any path references changed
- 1-05: Archive cut skills' metadata to `.planning/phases/01-curation/cut-skills.md` with rationale per skill

### Phase 1 gate (PASS criteria)
- [ ] `skills/` count is 25-35 (range; refined target)
- [ ] Every kept skill has valid YAML frontmatter (verified via the same Python check used in V7_FUNCTIONAL_VALIDATION.md Criterion 2)
- [ ] Every kept skill's cascade references resolve (verified via the same check used in Criterion 3)
- [ ] `cut-skills.md` documents removal rationale per cut skill
- [ ] Sample of 5 curated skills (functional-validation, meta-judge prep, python-agent-sdk, dispatch-parallel, plan-author) hand-reviewed for correctness
- [ ] **Regression**: Phase 0 evidence files still exist + still valid

### Evidence required at `.shannon/runs/phase-1/`
- `validate-skills.log` (YAML + cascade check output)
- `curation-report.md` (kept vs cut with rationale)
- `hand-review.md` (5-skill manual review)

---

## Phase 2 — Agent embedding manifests + build script

**Goal**: Implement Architecture C. Each kept agent gets a `manifest.yml` listing embedded skills. Build script (`build/embed-skills.py`) reads manifests + canonical skills, produces `agents/<name>/_built/skills/`. Spawn-time loading uses `_built/`.

### Tasks
- 2-01: For each of 8-12 target agents, decide which skills to embed (write `agents/<name>/manifest.yml`)
- 2-02: Write `build/embed-skills.py` (~50-100 lines of Python: read manifest, copy skills with optional adaptation, write to `_built/`)
- 2-03: Run build script; verify every agent's `_built/` is generated correctly
- 2-04: Write `build/verify-build.py` — verifies `_built/` matches manifest declarations (no missing skills, no extra files)
- 2-05: Add `agents/*/_built/` to `.gitignore` (already done in scaffold)

### Phase 2 gate (PASS criteria)
- [ ] Every agent has a `manifest.yml` listing 1-N embedded skills
- [ ] `build/embed-skills.py` exists and is Python-syntax-valid
- [ ] Running `python3 build/embed-skills.py` exits 0 and produces `_built/` directories
- [ ] `python3 build/verify-build.py` reports every agent's `_built/` matches its manifest
- [ ] Spawning an agent (via SDK harness) succeeds even after deleting the standalone `skills/<X>/SKILL.md` for an embedded skill X (proves embedding works as designed)
- [ ] **Regression**: Phase 1 (skill curation) still passes after build script runs

### Evidence required at `.shannon/runs/phase-2/`
- `build.log` (build script execution)
- `verify-build.log` (verifier output)
- `embedded-loading-proof.md` (the delete-standalone-then-spawn test result)

---

## Phase 3 — Command consolidation (27 → 15-18)

**Goal**: Reduce slash commands to the curated set. Remove duplicates. Each remaining command invokes a clear path through the agent/skill layer.

### Tasks
- 3-01: List current 27 commands; categorize (entry-point vs internal vs deprecated)
- 3-02: Identify duplicates (e.g., `dispatch` vs `dispatch-parallel` vs `dispatch-competitive`)
- 3-03: Write the v1 command surface (target 15-18)
- 3-04: For each kept command, ensure body invokes a real agent / skill that still exists in v1
- 3-05: Archive cut commands to `.planning/phases/03-commands/cut-commands.md`

### Phase 3 gate
- [ ] `commands/` count is 13-20 (range)
- [ ] Every kept command file references skills/agents that exist in v1
- [ ] No command file is empty or stub-only
- [ ] **Regression**: Phases 1+2 still pass

### Evidence at `.shannon/runs/phase-3/`
- `command-curation.md`
- `command-resolution.log` (verification that every command body's references resolve)

---

## Phase 4 — Hook curation (14 → 6-8) + contract declaration

**Goal**: Reduce hooks to the load-bearing set. Add the `required_hooks` field to skill frontmatter declaring which hooks each skill depends on. Build `/shannon:doctor` to verify the contract.

### Tasks
- 4-01: List current 14 hooks; identify the load-bearing 6-8
- 4-02: For each kept hook, add a META export declaring `name`, `event`, `consumed_by_skills`
- 4-03: For each skill that depends on a hook, add `required_hooks: [name]` to frontmatter
- 4-04: Write `scripts/doctor.py` — reads skills' `required_hooks` declarations, cross-checks against `hooks.json`, reports mismatches
- 4-05: Add `commands/doctor.md` invoking the doctor script

### Phase 4 gate
- [ ] `hooks/` count is 5-9
- [ ] Every kept hook has a META export
- [ ] Every skill that depends on a hook declares it in `required_hooks`
- [ ] `python3 scripts/doctor.py` exits 0 (no mismatches)
- [ ] `/shannon:doctor` returns a structured report
- [ ] **Regression**: Phases 1+2+3 still pass

### Evidence at `.shannon/runs/phase-4/`
- `hook-curation.md`
- `doctor-output.json`

---

## Phase 5 — Validation harnesses (SDK + Tmux)

**Goal**: Build both harnesses to full coverage of the 5 pillars.

### Tasks
- 5-01: Evolve existing `run-validation.py` (from `../`) into `scripts/harness/sdk_runner.py` for v1's surface
- 5-02: Write `scripts/harness/tmux_runner.py` — spawns Claude Code in tmux, sends slash commands, captures output
- 5-03: For each of the 5 pillars, write ≥1 SDK benchmark + ≥1 Tmux benchmark
- 5-04: Wire both into `scripts/harness/run-all.sh` (the release-gate script)
- 5-05: Write `docs/DEV_HARNESS.md` documenting how contributors run the harnesses locally

### Phase 5 gate
- [ ] SDK harness exists, Python-syntax-valid, covers 5 pillars (≥5 benchmarks)
- [ ] Tmux harness exists, Python-syntax-valid, covers 5 pillars (≥5 benchmarks)
- [ ] `scripts/harness/run-all.sh` exits 0 on a clean v1 install
- [ ] Iron Rule applied: zero `mock_*`, zero `test_*.py`, zero stubs in harness code
- [ ] **Regression**: Phases 1+2+3+4 still pass

### Evidence at `.shannon/runs/phase-5/`
- `sdk-harness-run.log` (full output of `run-all.sh --sdk`)
- `tmux-harness-run.log` (full output of `run-all.sh --tmux`)
- `harness-coverage.md` (pillar-to-benchmark mapping)

---

## Phase 6 — Documentation

**Goal**: Write the 8 v1 docs (Section 11 of PRD). Replace the v5/v6/v7 historical clutter.

### Tasks
- 6-01: README.md (already drafted in scaffold; refine if needed)
- 6-02: docs/INSTALL.md (platform-specific install steps)
- 6-03: docs/QUICK_START.md (10-minute path to first successful workflow)
- 6-04: docs/SKILLS_CATALOG.md (the curated ~30 skills with descriptions, triggers, related)
- 6-05: docs/ARCHITECTURE.md (5 pillars + Architecture C internals + 7-layer system + embedded-skill mechanic)
- 6-06: docs/FUNCTIONAL_VALIDATION_GUIDE.md (Iron Rule + writing benchmarks + harness usage)
- 6-07: docs/CONTRIBUTING.md (how to add a skill / agent / hook / command)
- 6-08: docs/DEV_HARNESS.md (drafted in Phase 5; refine)

### Phase 6 gate
- [ ] All 8 docs exist
- [ ] Every doc has H1 + Cross-references section
- [ ] No doc references files that don't exist in v1
- [ ] README has install steps + quick start that resolve to working commands
- [ ] **Regression**: Phases 1+2+3+4+5 still pass

### Evidence at `.shannon/runs/phase-6/`
- `doc-completeness.md` (per-doc check)
- `link-validation.log` (broken-link check across all v1 docs)

---

## Phase 7 — Release v0.1.0 (first public)

**Goal**: Tag v0.1.0; publish to marketplace; verify install + first-user flow end-to-end.

### Tasks
- 7-01: Run `scripts/harness/run-all.sh` for release-candidate verification
- 7-02: Verify Phase 6 docs render correctly on GitHub
- 7-03: Tag `v0.1.0` (git tag -a)
- 7-04: Push to public GitHub repo
- 7-05: Submit to Claude Code marketplace (if marketplace API exists; else document local install path)
- 7-06: Run Tmux harness against the marketplace-installed version (full first-user simulation)

### Phase 7 gate
- [ ] `scripts/harness/run-all.sh` exits 0 on release candidate
- [ ] Git tag `v0.1.0` exists
- [ ] Public GitHub repo accessible
- [ ] Tmux harness passes against marketplace-installed version (this is the most important regression check)
- [ ] **Regression**: All prior phases (1-6) still pass on the released artifact

### Evidence at `.shannon/runs/phase-7/`
- `release-candidate-run.log` (full harness output)
- `marketplace-install-tmux.log` (real-user simulation)
- `release-summary.md` (what shipped, what didn't, known issues)

---

## Gate enforcement protocol

For every phase:

1. Pre-execution: read this ROADMAP's gate criteria for the phase
2. During execution: capture evidence into `.shannon/runs/<phase>/`
3. Pre-completion: run `scripts/harness/verify-phase.py <phase-id>` (built in Phase 5 — interim hand-verify for earlier phases)
4. **Cannot transition to next phase without PASS verdict in `.shannon/runs/<phase>/VALIDATION.md`**
5. **Each phase's gate verifies prior phases STILL pass** — this catches regressions

## Iron Rule across all phases

- No `mock_*`, no `stub_*`, no `test_*.py` anywhere in `v1/shannon/`
- Every verdict cites specific evidence file paths
- "Tests pass" is not a verdict — the test command's actual output appears in the transcript
- A claim of completion without surfaced output = REFUSED (per gate-validation-discipline)

## What this ROADMAP doesn't lock in

- Per-phase tasks may add or remove items as work surfaces what's needed
- Component counts (skills, agents, etc.) are TARGETS not requirements; refined during Phase 1
- Phase order may interleave (e.g., partial Phase 2 + Phase 1 retry) if dependencies emerge
- v0.2 and beyond are out of scope for this ROADMAP
