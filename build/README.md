# Shannon v1 build system

Architecture C (hybrid) requires a build step: skill content lives canonically in `skills/`, and each agent's `manifest.yml` declares which skills get embedded into the agent's `_built/skills/` payload. At spawn time, an agent's context includes its embedded SKILL.md content directly — no Skill-tool round-trip needed for those skills.

## Files

- `embed-skills.py` — reads every `agents/<name>/manifest.yml`, copies declared skills from `skills/` into `agents/<name>/_built/skills/`
- `verify-build.py` — sanity check that the `_built/` payload matches the manifest and the canonical source
- `README.md` — this file

## Usage

From the v1/shannon repo root:

```bash
python3 build/embed-skills.py    # build
python3 build/verify-build.py    # verify
```

Both are idempotent. Re-running `embed-skills.py` wipes and rebuilds each `_built/skills/` to match the current manifest. Re-running `verify-build.py` does not mutate state.

## Iron Rule discipline

- **No mock content.** If a manifest references a skill that doesn't exist in `skills/`, the build fails with a clear error. No silent substitution. No placeholder skill.
- **No fabricated PASS.** The verifier reads real disk every time. Output `Mismatches: 0` only happens when all checks really passed.
- **Empty manifests refused.** An agent with `embedded_skills: []` isn't doing Architecture C work and is rejected at build time.

## What gets copied

For each skill in `embedded_skills`:
- `skills/<skill>/SKILL.md` → `agents/<agent>/_built/skills/<skill>/SKILL.md`
- `skills/<skill>/references/*` → `agents/<agent>/_built/skills/<skill>/references/*` (whole directory)
- Anything else under `skills/<skill>/` (scripts, examples) — copied as-is
- `.DS_Store` and `__pycache__` ignored

## What does NOT get copied

- Skills NOT in `embedded_skills` for that agent. Those skills are still available via the `Skill: <name>` invocation at runtime — they just aren't bundled into the agent's spawn context.

## Cascade safety

Phase 02-01's cascade-conflict analysis confirmed no two embedded skills within the same agent share `references/` filenames. The build uses straight `shutil.copytree` with no prefix logic.

If a future change introduces cascade conflicts (two embedded skills both declare `references/notes.md`), `verify-build.py` will flag the mismatch and the build must be re-designed.

## Evidence

- `embed-skills.py` writes `.planning/phases/02-agent-embedding/evidence/build-skills.log`
- `verify-build.py` writes `.planning/phases/02-agent-embedding/evidence/verify-build.log`

These logs are the evidence cited by 02-02-VALIDATION.md (Plan 02-02 gate) and 02-03-VALIDATION.md (Plan 02-03 smoke test).
