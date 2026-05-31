# QA-02 — Skill frontmatter `name` did not match directory (3 skills)

## Finding
3 of 67 skills declared a frontmatter `name:` that did not equal their directory
name. The other 64 skills use bare `name == dir`. Claude Code resolves a skill by
its directory; a divergent frontmatter `name` is dead metadata that can confuse
tooling and any cross-reference that assumes `name == dir`.

| Directory             | Old name              | New name      |
|-----------------------|-----------------------|---------------|
| `skills/brainstorm`   | `sdd:brainstorm`      | `brainstorm`  |
| `skills/create-ideas` | `sdd:create-ideas`    | `create-ideas`|
| `skills/prd-clarity`  | `requirements-clarity`| `prd-clarity` |

Fix = align `name` to dir (least disruptive — no directory moves, matches the
other 64).

## References updated (live surface only)
Step-A grep found stale references to the old `requirements-clarity` name in live
trees; both updated to point at the real dir/name:
- `skills/prompt-improver/references/question-patterns.md:185` — `skills/requirements-clarity/` → `skills/prd-clarity/`
- `docs/BENCHMARKS.md:447` — skills-exercised list `requirements-clarity` → `prd-clarity`

Left untouched per scope: `.v7/` planning docs, `.prompts/` prompt history, and
`v1/` (gitignored "Old V1 artifacts — out of scope").

## Evidence
BEFORE (`QA-02-before.log`):
```
brainstorm   -> name: sdd:brainstorm
create-ideas -> name: sdd:create-ideas
prd-clarity  -> name: requirements-clarity
```
AFTER (`QA-02-after.log`):
```
brainstorm   -> name: brainstorm
create-ideas -> name: create-ideas
prd-clarity  -> name: prd-clarity
remaining name!=dir mismatches: (none — clean)
```
Refs grep: `QA-02-refs-before.log`.

Commit: aa67076
