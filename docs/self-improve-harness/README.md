# Self-improve harness — provenance

This directory preserves the real self-improvement work that fed Shannon v1.0.0,
plus the evidence captured while releasing v1.

## What's here

- `QA-01..QA-06-*.md` — the six QA improvements mined from the v7 prototype line
  (version reconciliation, skill-name/dir mismatches, stale validators, duplicate
  hooks, dead command refs, doctor check demotion). Each documents a real defect
  found by self-audit and the fix applied.
- `run-validation-v7-reference.py` — the v7 Iron-Rule validation harness, kept as
  a **reference only**. Its paths point at the v7 lineage repo
  (`/Users/nick/Desktop/shannon-framework`), not this repo — it does not run here.
  The v1 equivalents are `scripts/doctor.py` (mechanical contract) and
  `scripts/harness/load_check.py` (real Agent SDK load probe).
- `evidence/` — captured output from the v1.0.0 release:
  - `load-check-v1-PASS.json` — the real SDK load probe against v1.0.0
    (`verdict: PASS`, every command addressable).
  - `load-check-v7-cache-FAIL.json` — the same probe catching a stale v7 cache
    mispointing before the marketplace was repointed.

## The live harnesses (run these, not the reference)

```bash
python3 scripts/doctor.py                 # mechanical contract — 10/10
python3 scripts/harness/load_check.py     # real SDK load probe (inherits CLI auth)
```
