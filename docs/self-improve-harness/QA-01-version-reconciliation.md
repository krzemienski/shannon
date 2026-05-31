# QA-01 — Version drift reconciliation to single source of truth

## Finding
Version strings drifted across the plugin surface. `plugin.json` + `README.md` + `CHANGELOG.md` top entry already declared **7.0.0** and described the real v7 surface (67 skills, 14 agents, 4 new agent types, 12 orchestration improvements). Stale laggards still pointed at older versions:
- `.claude-plugin/marketplace.json` → `6.0.0`
- `commands/doctor.md` → `version=6.0.0` and "all 14 scripts"
- `CLAUDE.md` → `Shannon v5.6.0`
- `scripts/_validate-manifest.js` → expected `6.x`, and required a `hooks: ./hooks/hooks.json` declaration that plugin.json lacked → validator exited 1.

Live surface counts: 28 commands, 14 agents, 67 skills, 10 core layers, **16** hook scripts registered in `hooks/hooks.json`.

## Decision + rationale
Authoritative version = **7.0.0** (not 6.0.0). Rationale: the manifest (`plugin.json`), `README.md`, and the top `CHANGELOG.md` entry all already say 7.0.0 and describe the real v7 surface. Those are the canonical, user-facing artifacts. Reverting them down to 6.0.0 would contradict shipped release docs; promoting the laggards up to 7.0.0 makes every artifact agree with the canonical set. So the laggards were corrected upward.

context7 verified the plugin contract: the official "Complete Plugin Manifest Schema" lists `hooks` as a top-level field accepting a string path (e.g. `"hooks": "./config/hooks.json"`), so `"hooks": "./hooks/hooks.json"` is valid and supported. The validator's hooks-declaration check is reasonable; the real fix is declaring it in the manifest, not removing the check. Evidence: `.v7/runs/phase-6-qa-selfimprove/iter-1/context7-plugin-hooks.md`.

## Files changed (5)
1. `.claude-plugin/marketplace.json` — `plugins[0].version` 6.0.0 → 7.0.0; description updated to v7 framing.
2. `commands/doctor.md` — `version=6.0.0` → `version=7.0.0`; "all 14 scripts" → "all 16 scripts".
3. `CLAUDE.md` — "Current Version" line 5.6.0 → `Shannon v7.0.0 "Orchestration-First"` (version-identity line only; stale count text left for a separate P2 doc fix).
4. `scripts/_validate-manifest.js` — version expectation `/^6\./` → `/^7\./`.
5. `.claude-plugin/plugin.json` — added top-level `"hooks": "./hooks/hooks.json"` (after "license"); version unchanged at 7.0.0.

## BEFORE
```
plugin.json version: "version": "7.0.0",
marketplace version: 6.0.0
doctor.md: version=6.0.0
doctor.md: references all 14 scripts
CLAUDE.md: Shannon v5.6.0 "Comprehensive Quality & Intelligence"
_validate-manifest.js errors:
  - plugin.json version must be 6.x, got "7.0.0"
  - plugin.json must declare hooks: ./hooks/hooks.json
  ok: false   EXIT=1
```

## AFTER
```
plugin.json valid JSON
marketplace.json valid JSON
plugin.version=7.0.0
marketplace.version=7.0.0
plugin.hooks=./hooks/hooks.json
doctor.md: version=7.0.0
doctor.md: references all 16 scripts
CLAUDE.md: Shannon v7.0.0 "Orchestration-First"
_validate-manifest.js errors: []   ok: true   MANIFEST_EXIT=0
```

The manifest validator now exits 0 with zero errors.

Commit: ce479a2
