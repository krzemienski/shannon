# Plan 07: Release v0.1.0

> **This PLAN.md is the execution prompt.** The release-candidate phase. Structural completeness from this phase + user-action steps documented for final ship.

---

## Prerequisite check (BLOCKING)

```bash
test -f ../06-docs/PHASE-06-VALIDATION.md
grep -qE 'Verdict.*PASS' ../06-docs/PHASE-06-VALIDATION.md
python3 ../../../scripts/doctor.py | python3 -c "import json,sys; assert json.load(sys.stdin)['summary']['mismatches']==0"
bash ../../../scripts/harness/run-all.sh --dry-run > /dev/null 2>&1
```

---

## Mock detection preamble

REFUSED tasks:

- Fabricating a successful release-candidate harness run when the sandbox can't actually reach the API.
- Claiming `git tag v0.1.0` was created when the sandbox can't write to `.git/`.
- Producing a release-summary that contradicts the on-disk artifact state.

---

## Context

- **Phase**: 7 (Release v0.1.0)
- **Predecessor**: Phase 6 PASS (8 docs, 0 broken links, doctor green)
- **Goal**: produce the release-candidate artifact + the user-action checklist for the final ship steps that require host-side access

## Honest split: sandbox vs user-action

| Step | Sandbox-provable | User-action required |
|---|---|---|
| 7-01 Run `scripts/harness/run-all.sh` for release-candidate verification | ✓ `--dry-run` mode passes; structural | ✗ `--live` mode requires API + Claude Code CLI |
| 7-02 Verify Phase 6 docs render correctly on GitHub | ✓ Markdown structure validates | ✗ Render on actual GitHub host requires push |
| 7-03 Tag v0.1.0 (`git tag -a`) | ✗ Sandbox can't write to `.git/` | ✓ User runs `git tag -a v0.1.0` |
| 7-04 Push to public GitHub repo | ✗ Sandbox has no network to remote | ✓ User runs `git push --tags` |
| 7-05 Submit to marketplace (if API) / document local install | ✓ Local install path documented | ✗ Marketplace API requires host-side credentials |
| 7-06 Tmux harness against marketplace-installed | ✗ Requires installed plugin on host | ✓ User runs `bash scripts/harness/run-all.sh --live --tmux` |

This Phase 7 produces the **release-candidate** artifact and the user-action runbook. Final ship steps land in the user's local execution per the checklist below.

## Tasks

### Task 1 — Release-candidate verification (structural)

Re-run the full verifier chain from the sandbox:

```bash
python3 build/embed-skills.py
python3 build/verify-build.py
python3 scripts/doctor.py
bash scripts/harness/run-all.sh --dry-run
```

All four must exit 0 with 0 mismatches.

### Task 2 — Write release artifacts

Three documents:

1. `RELEASE_NOTES.md` — v0.1.0 notes for users (what's in this release; known limitations)
2. `RELEASE_CHECKLIST.md` — explicit user-action steps for git tag + push + marketplace
3. `PHASE-07-VALIDATION.md` — phase gate

### Task 3 — Final summary across all 7 phases

`FINAL_SUMMARY.md` — recap of every phase's headline numbers + cross-link to its VALIDATION.md.

## Phase-level regression check

```bash
test -f ../../BRIEF.md && test -f ../../ROADMAP.md
test -f ../01-curation/PHASE-01-VALIDATION.md && [ $(ls ../../../skills/ | wc -l) -eq 31 ]
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md && [ $(ls ../../../agents/ | wc -l) -eq 9 ]
test -f ../03-commands/PHASE-03-VALIDATION.md && [ $(ls ../../../commands/ | wc -l) -ge 13 ]
test -f ../04-hooks/PHASE-04-VALIDATION.md
test -f ../05-harnesses/PHASE-05-VALIDATION.md
test -f ../06-docs/PHASE-06-VALIDATION.md
python3 ../../../scripts/doctor.py | python3 -c "import json,sys; assert json.load(sys.stdin)['summary']['mismatches']==0"
bash ../../../scripts/harness/run-all.sh --dry-run > /dev/null 2>&1
```

## Plan gate (BLOCKING)

Phase 7 (structural) PASSes when:

1. ✅ Release-candidate verification chain exits 0 end-to-end
2. ✅ `RELEASE_NOTES.md` exists with what's in v0.1.0
3. ✅ `RELEASE_CHECKLIST.md` documents user-action steps for tag/push/marketplace
4. ✅ `FINAL_SUMMARY.md` exists
5. ✅ All prior phases' VALIDATION.md present + verdict=PASS
6. ✅ doctor.py + verify-build.py + harness --dry-run all green

## Done condition

`PHASE-07-VALIDATION.md` with verdict=PASS (structural). User-action checklist handed off to release operator.

## Iron Rule restatement

- The Phase 7 gate covers only what the sandbox can prove. User-action steps are explicitly called out, not claimed as complete.
- No fabricated marketplace submission verdict. No fabricated git tag presence. Sandbox limits are honored.
