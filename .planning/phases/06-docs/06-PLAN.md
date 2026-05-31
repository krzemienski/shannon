# Plan 06: Documentation (8 docs per PRD Section 11)

> **This PLAN.md is the execution prompt.** Last writing-heavy phase before release. Same combined-plan pattern.

---

## Prerequisite check (BLOCKING)

```bash
test -f ../05-harnesses/PHASE-05-VALIDATION.md
grep -qE 'Verdict.*PASS' ../05-harnesses/PHASE-05-VALIDATION.md
python3 ../../../scripts/doctor.py | python3 -c "import json,sys; assert json.load(sys.stdin)['summary']['mismatches']==0"
```

---

## Mock detection preamble

REFUSED tasks:

- Writing a doc that references files/skills/agents/commands/hooks that don't exist in v1.
- Writing a doc that fabricates install steps that aren't proven on disk.
- Writing a doc that contradicts what the code/manifests/build script actually does.
- Producing stub docs with only headers and no content.

---

## Context

- **Phase**: 6 (Documentation)
- **Predecessor**: Phase 5 PASS (harnesses ready)
- **Goal**: write the 8 v1 docs per PRD Section 11. Replace any v5/v6/v7 historical clutter.
- **Inputs**: all v1 artifacts (31 skills, 9 agents, 19 commands, 7 hooks, build, scripts, harness)
- **Outputs** (8 files):
  - `README.md` — refresh (already drafted; update Phase status + add Quick Start link)
  - `docs/INSTALL.md`
  - `docs/QUICK_START.md`
  - `docs/SKILLS_CATALOG.md`
  - `docs/ARCHITECTURE.md`
  - `docs/FUNCTIONAL_VALIDATION_GUIDE.md`
  - `docs/CONTRIBUTING.md`
  - `docs/DEV_HARNESS.md` (already done in Phase 5; refine if needed)

## Phase-level regression check

```bash
test -f ../../BRIEF.md && test -f ../../ROADMAP.md
test -f ../01-curation/PHASE-01-VALIDATION.md && [ $(ls ../../../skills/ | wc -l) -eq 31 ]
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md && [ $(ls ../../../agents/ | wc -l) -eq 9 ]
test -f ../03-commands/PHASE-03-VALIDATION.md && [ $(ls ../../../commands/ | wc -l) -ge 13 ]
test -f ../04-hooks/PHASE-04-VALIDATION.md
test -f ../05-harnesses/PHASE-05-VALIDATION.md
test -f ../../../docs/DEV_HARNESS.md
python3 ../../../scripts/doctor.py | python3 -c "import json,sys; assert json.load(sys.stdin)['summary']['mismatches']==0"
```

## Plan gate (BLOCKING)

Phase 6 PASSes when:

1. ✅ All 8 docs exist
2. ✅ Every doc has H1 (`# `) and a Cross-references section
3. ✅ No doc references files that don't exist in v1 (broken-link check)
4. ✅ README install steps + quick start resolve to working commands
5. ✅ Phase 0+1+2+3+4+5 regression PASS

## Done condition

`PHASE-06-VALIDATION.md` with verdict=PASS. Phase 7 (Release) unblocked.

## Iron Rule restatement

- Doc content reflects what's actually on disk (no future-state claims, no aspirational examples that don't run).
- Every internal cross-reference resolves (link-validation evidence required).
- Examples in docs are run from this directory's actual contents.
