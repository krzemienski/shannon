# Git Integration

> How plans interact with git: when to commit, branch strategy, commit message conventions, and the rule that not every plan artifact gets committed.

## What gets committed vs. not

Committed:
- Code changes
- Configuration changes
- Documentation that ships with the codebase
- `.planning/BRIEF.md`, `.planning/ROADMAP.md` (long-lived plan artifacts)
- `.planning/phases/NN/NN-NN-SUMMARY.md` (one per completed phase)

NOT committed:
- `.planning/phases/NN/NN-NN-PLAN.md` (intermediate; phase exit produces SUMMARY)
- `.planning/phases/NN/NN-NN-RESEARCH.md` / `FINDINGS.md` (intermediate)
- `.continue-here.md` (transient handoff)
- `.planning/scratchpad/` (working files)

The principle: commit OUTCOMES, not PROCESS. PLAN.md is process; SUMMARY.md is outcome.

Add to `.gitignore`:
```
.planning/phases/**/PLAN.md
.planning/phases/**/RESEARCH.md
.planning/phases/**/FINDINGS.md
.planning/scratchpad/
.continue-here*.md
```

Keep:
```
.planning/BRIEF.md
.planning/ROADMAP.md
.planning/MILESTONES.md
.planning/ISSUES.md
.planning/phases/**/SUMMARY.md
```

## When to commit during a phase

Three legitimate commit points within a phase:

1. **Phase initialization** — when the planning structure is established
2. **Phase completion** — when SUMMARY.md is written
3. **Handoff** — when `.continue-here.md` is created (the handoff itself, not the plan)

Don't commit per-task. Tasks accumulate into a phase; the phase commits as a unit.

Exception: long phases (>4 hours of work) can interim-commit with `wip:` prefix; squash before final commit.

## Branch strategy

For solo-dev + Claude:

- Work on `main` for trivial / fast-iteration phases
- Work on a feature branch for phases that need review or might be reverted

The branch decision is per-phase:

```
Phase 01: simple type fix → main, single commit
Phase 02: new feature (auth) → branch feature/auth, ~10 commits, PR before merge
Phase 03: another fix → main
```

Don't force every phase into a branch.

## Commit message convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

Where:
- type: `feat | fix | refactor | docs | test | chore | perf | style`
- scope: optional, narrows to module/area
- subject: imperative, < 72 chars
- body: WHY (the what is in the diff)
- footer: refs (issue numbers, plan files)

Examples:

```
feat(auth): JWT-based authentication with httpOnly cookies

Replaces session-based auth. Refresh rotation per OWASP.
Library: jose (chosen over jsonwebtoken for better TS support).

Refs: .planning/phases/02-auth/02-01-SUMMARY.md
```

```
fix(dashboard): contain filter dropdown within viewport

Used clamp() instead of right:0 — was overflowing on narrow widths.

Refs: audit-evidence/cycle-02 finding F-c02-008
```

The body answers WHY the change was made; the diff already shows WHAT.

## Atomic commits

One logical change per commit:

✓ "feat: add login endpoint" + "test: validate login flow"
✗ "feat: add login + fix unrelated bug + style cleanup"

Each commit should be revertable independently. If reverting "feat: add login" would also break "fix unrelated bug," they're not atomic.

When tempted to bundle: stage the unrelated changes separately, commit separately. `git add -p` is your friend.

## Co-authorship credit

When Claude does substantial work on a commit, include a co-author trailer:

```
Co-authored-by: Claude <noreply@anthropic.com>
```

This makes the contribution visible in `git shortlog` / GitHub stats. Some teams prefer this; others don't. Match the project's convention.

## Pushing

For solo work, push frequently (after each phase). For shared branches, push when ready for review.

`git push --force-with-lease` for rebases on branches you own. Never `--force` on shared branches.

## Reverting

If a phase ships and turns out to be wrong:

```
# Identify the phase commit(s)
git log --oneline | head -20

# Revert (creates a new commit)
git revert <sha>

# OR roll back (rewrites history — only on private branches)
git reset --hard <previous-sha>

# Document in MILESTONES.md or a new SUMMARY.md
```

The SUMMARY.md of a reverted phase stays in git history but is updated to note the revert.

## Pre-commit hooks

If the project has pre-commit hooks (linting, formatting, type-checking), respect them.

```bash
# Check what hooks exist
ls -la .git/hooks/
cat .pre-commit-config.yaml 2>/dev/null

# Run them manually:
pre-commit run --all-files
```

Don't bypass with `--no-verify` unless you have a specific reason documented in the commit message.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Commit every PLAN.md / RESEARCH.md | Pollutes history with intermediate artifacts | .gitignore intermediate; commit SUMMARY |
| Single huge commit at end of phase | Can't review or revert sub-parts | Atomic commits per logical change |
| Force-pushing shared branches | Destroys collaborators' work | --force-with-lease, only on private |
| Bypassing pre-commit hooks | Skipping team conventions | Run hooks; fix issues if they fail |
| Vague commit messages ("update", "fix") | Future-you can't find anything | type(scope): subject — be specific |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/checkpoints.md` — when to checkpoint pre-commit
- `references/milestone-management.md` — release / tag conventions
- `skills/commit-work/` — adjacent skill for the commit phase itself
