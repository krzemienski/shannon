# QA-06 — Doctor check 7 demoted from hard FAIL to advisory WARN

## Finding

`commands/doctor.md` check 7 ("Conflicting plugins") asserted that 16 *other*,
unrelated third-party plugins be disabled in the dev's **global**
`~/.claude/settings.json`. The exact list is hardcoded in
`scripts/uninstall-others.sh:33-50` (kaizen/sadd/sdd/reflexion@context-engineering-kit,
deepest-plan, start@the-startup, autoresearch, the three anneal plugins,
planning-with-files, prd-generator, claude-hud, validationforge, crucible, omc).

That state is **unreachable by any repo edit** — it lives in the developer's
global Claude config, outside the Shannon repository. Worse, doctor.md was
internally inconsistent:
- Line :29 used **advisory** language ("recommend disabling").
- Lines :21 + :35 graded all 7 checks as PASS / FAIL and declared "All 7 checks
  PASS = healthy install" — i.e. a hard FAIL.

Net effect: any multi-plugin dev box reported Shannon as **UNHEALTHY** purely
because the dev had other plugins installed — even with a perfectly valid Shannon
install (checks 1–6 all PASS). A conflicting third-party plugin is an
environmental advisory, not a Shannon plugin defect.

## Fix

Demote check 7 to a **WARN/advisory tier** that never emits PASS / FAIL and never
affects the healthy/unhealthy verdict.

- Behavior section: split checks into hard (1–6, PASS/FAIL, verify the plugin
  contract) vs advisory (7, WARN-only environment note). Made the WARN-only and
  "never flips to UNHEALTHY" semantics explicit so the prompt-command model
  follows it unambiguously.
- Success criteria: health verdict now = "all 6 hard checks PASS = healthy";
  check 7 WARN lists still-enabled plugins + suggests `scripts/uninstall-others.sh`
  but reports healthy when 1–6 PASS.
- Checks 1–6 left exactly as-is (real plugin-contract checks: manifest,
  marketplace, hooks registration, settings sanity, log dirs, CLI registration).

This corrects the check; it does not weaken a real health check.

## Before (grading lines, verbatim)

```
21: Runs these checks in order; emits PASS / FAIL per check:
29: 7. **Conflicting plugins** — list which of the 16 consolidated plugins are still enabled; recommend disabling.
35: - All 7 checks PASS = healthy install.
36: - Any FAIL → actionable remediation message + path to relevant docs.
```

## After (grading lines, verbatim)

```
Runs these checks in order. Checks 1–6 are **hard** checks emitting PASS / FAIL —
they verify the Shannon plugin contract. Check 7 is an **advisory WARN** check
about the surrounding environment, not the Shannon install itself.
...
7. **Conflicting plugins** *(advisory WARN — never PASS / FAIL)* — ... This check **never** emits FAIL and **never** affects the healthy/unhealthy verdict.
...
- **All 6 hard checks (1–6) PASS = healthy install.** The health verdict is driven solely by the plugin-contract checks.
- Check 7 (conflicting plugins) is **advisory WARN only** — it does **not** affect the healthy/unhealthy status. ... never flip the install to UNHEALTHY.
```

## Doctor SDK re-run verdict

See `.v7/runs/phase-6-qa-selfimprove/iter-1/QA-06-after.log` (appended tail of
`.evidence/QA-06-doctor-after/metadata.json`). Expected: checks 1–6 PASS,
check 7 reported as WARN/advisory, overall install **healthy** (not flipped to
UNHEALTHY by the conflicting-plugins environment note).

Evidence: `.v7/runs/phase-6-qa-selfimprove/iter-1/QA-06-before.log`,
`.v7/runs/phase-6-qa-selfimprove/iter-1/QA-06-after.log`.

Commit: see `git log` for `qa(doctor): make conflicting-plugins check advisory WARN not hard FAIL [QA-06]`.
