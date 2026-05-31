# QA-04 — Drop default-path hooks declaration that broke plugin loading

## Regression
QA-01 (commit ce479a2) added `"hooks": "./hooks/hooks.json"` to `.claude-plugin/plugin.json`
to satisfy `scripts/_validate-manifest.js`. But Claude Code auto-discovers the conventional
`hooks/hooks.json`. Declaring that same default path made CC abort on load with
"Duplicate hooks file detected" → plugin status `✘ failed to load`. The validator's
requirement was wrong for a conventional layout.

## Real-runtime evidence
**BEFORE** (`.v7/runs/phase-6-qa-selfimprove/iter-1/QA-04-before.log`):
```
$ jq -r '.hooks' .claude-plugin/plugin.json
./hooks/hooks.json
$ claude plugin list | grep -i shannon
  ❯ shannon@shannon-local
    Error: Hook load failed: Duplicate hooks file detected: ./hooks/hooks.json
    resolves to already-loaded file .../hooks/hooks.json. The standard hooks/hooks.json
    is loaded automatically, so manifest.hooks should only reference additional hook files.
```
`/shannon:doctor` (SDK, `.evidence/QA-04-doctor-before/`): hooks check reported the
duplicate-hooks failure.

**AFTER** (`.v7/runs/phase-6-qa-selfimprove/iter-1/QA-04-after.log`):
```
plugin.json valid JSON
hooks key: ABSENT
MANIFEST_EXIT=0          # node scripts/_validate-manifest.js → errors: [], ok: true
$ claude plugin install shannon@shannon-local → ✔ Successfully installed
$ claude plugin list | grep -i shannon
  ❯ shannon@shannon-local        # no error line — loads clean
```
`/shannon:doctor` (SDK, `.evidence/QA-04-doctor-after/`):
```
| 1 | Plugin manifest              | ✅ PASS — v7.0.0, fields complete |
| 3 | Hooks registration           | ✅ PASS — 16 refs, 16 on disk, 0 missing |
| 6 | CLI marketplace registration | ✅ PASS — shannon@shannon-local enabled |
```
No duplicate-hooks failure anywhere. (Only remaining FAIL is check 7 — 12 conflicting
legacy plugins — an unrelated concern, not this fix.)

## context7 confirmation
`/anthropics/claude-code` plugin-structure docs: `hooks` manifest field
**Default `"./hooks/hooks.json"`**; "Registration: Hooks register automatically when
plugin enables." The string-path form is for NON-default locations
(docs example `"./config/hooks.json"`). Declaring the default duplicates the auto-load.
Full citation: `.v7/runs/phase-6-qa-selfimprove/iter-1/QA-04-context7.md`.

## Files changed
1. `.claude-plugin/plugin.json` — removed `"hooks": "./hooks/hooks.json"` (version stays 7.0.0).
2. `scripts/_validate-manifest.js` — inverted the hooks check: require the conventional
   `hooks/hooks.json` on disk; do NOT require a manifest declaration; if a `hooks` path IS
   declared it must point to an existing file AND must not be the default path (which would
   re-introduce the duplicate-load abort). Inline-object hooks allowed.

## No-regression
`python3 tests/validate_skills.py` → s=0 (All skills valid).
`python3 validate_shannon_v5.py` → v=0 (properly configured).

Commit: see git log [QA-04].
