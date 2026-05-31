# QA-03 — Modernize two stale validators to the v7 contract

## Finding
Both repo validators enforced a schema ~6 months older than the current
67-skill / 28-command surface. They failed every run not because the surface was
broken, but because the *checks* were dead. The CHANGELOG implied the old schema
was archived; the validators were never updated to match.

- `tests/validate_skills.py` enforced a **V4** schema: a `skill-type` enum
  (QUANTITATIVE/RIGID/PROTOCOL/FLEXIBLE) plus a heavyweight section grid
  (`## Inputs`, `## Outputs`, `## Success Criteria` with `assert`/`validate`,
  two `### Example N:` blocks, `## Common Pitfalls`). Live skills carry none of
  this → all 67 failed.
- `validate_shannon_v5.py` required a **V5** `usage:` frontmatter field on every
  command. v7 commands use `argument-hint`, not `usage:` → all 28 failed.

Correcting the checks to the real contract is fixing the validator, not
weakening it.

## Checks DROPPED (dead pre-v7 schema)
validate_skills.py:
- `skill-type` required field + enum validation
- section grid: `## Inputs`, `## Outputs`, `## Workflow/## Process` requirement,
  `## When to Use`, `## Purpose/## Overview`
- `## Success Criteria` must contain `assert`/`validate`
- minimum-2 `### Example N:` blocks
- `## Common Pitfalls` required for RIGID/QUANTITATIVE

validate_shannon_v5.py:
- command `usage:` frontmatter requirement

## Checks KEPT / STRENGTHENED (real contract — still hard-fail)
validate_skills.py:
- frontmatter present + parseable YAML
- `name` and `description` present
- **`name` == directory name** (new hard fail; also covers flat `*.md` → stem)
- description length floor (>= 20 chars)
- `triggers` presence → **soft warning only** (non-blocking)

validate_shannon_v5.py:
- plugin.json / marketplace.json sanity
- command `name` == filename, command `description` present
- skill `name` == directory, skill `description` present
- `@skill` references resolve to existing skills
- `required-sub-skills:` dependencies resolve to existing skills

## Evidence
BEFORE (failing on dead schema):
- `QA-03-validate_skills-before.log` → skills_exit=1 (67 files w/ errors)
- `QA-03-validate_v5-before.log` → v5_exit=1 (28 commands "Missing usage")

AFTER (against the QA-02-corrected surface):
- `QA-03-validate_skills-after.log` → skills_exit=0 (✅ all valid; soft trigger warnings only)
- `QA-03-validate_v5-after.log` → v5_exit=0 (28 commands, 67 skills, 0 issues)
- `node scripts/_validate-manifest.js` → manifest_exit=0 (ok:true) — no regression

## Validators still fail on genuine defects (proven)
Throwaway probe (temp dir, not committed):
- skill missing `description` → REJECTED
- skill `name` != directory → REJECTED
- command `name` != filename + missing description → REJECTED
- valid skill → PASS
Both probes exited 1 as expected. No blanket "pass everything" was introduced.

Commit: 4e79c7d
