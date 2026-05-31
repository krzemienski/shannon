# Milestone Management

> How to mark and manage shipped versions. Milestones are the punctuation in continuous iteration — they say "this is v1.0; the next phases are v1.1."

## What a milestone is

A milestone is a named version of the shipped artifact:

- v1.0 — first shipped version (the brief was realized)
- v1.1 — incremental ship after v1.0
- v2.0 — major redesign / breaking change

Milestones are NOT phases. Phases are work units. Milestones are SHIPS.

## When to declare a milestone

Declare a milestone when:
- The work satisfies a meaningful chunk of the brief
- The version is shippable to users (or to the next stakeholder)
- You want a git tag / release-notes anchor

Don't declare a milestone for every phase. Milestones aggregate phases.

Typical pattern:
```
Phases 01-04 → ship as v1.0
Phases 05-08 → ship as v1.1
Phases 09-12 → ship as v1.2
Phases 13-20 → ship as v2.0 (major redesign)
```

## Milestone artifacts

When declaring v1.0:

1. **Update `MILESTONES.md`** with the entry
2. **Update `CHANGELOG.md`** with the user-facing summary
3. **Git tag**: `git tag -a v1.0.0 -m "<release name>"`
4. **Git push**: `git push origin v1.0.0`
5. **Release announcement** (if applicable)

### MILESTONES.md entry template

```markdown
## v1.0.0 — <Release Name> — YYYY-MM-DD

**Phases included**: 01, 02, 03, 04

**Headline**: <one sentence describing what shipped>

**Highlights**:
- Feature A is now live
- Feature B integrated with C
- Performance: <metric improved by N%>

**Known issues**:
- <documented limitations carried forward>

**Reference**:
- Brief: .planning/BRIEF.md (the goals this realizes)
- Phase summaries: .planning/phases/01..04/*-SUMMARY.md
- Git tag: v1.0.0
```

The MILESTONES.md grows over time. Each entry is a historical anchor.

## Continuous extension vs. version archive

When v1.0 ships, two patterns:

### Pattern: Extend (default)

Keep building on the same `.planning/` tree. New phases (05+) are v1.1.

```
.planning/
├── BRIEF.md            (still the same vision)
├── ROADMAP.md          (extended with phases 05+)
├── MILESTONES.md       (entries grow)
└── phases/
    ├── 01..04 / (v1.0)
    ├── 05..08 / (v1.1)
    └── 09..   / (in progress)
```

Use this for continuous iteration on the same product.

### Pattern: Archive (rare)

Move v1.0's planning to an archive and start fresh for v2.0.

```
.planning/
├── archive/
│   └── v1.x/   (BRIEF, ROADMAP, phases — frozen)
├── BRIEF.md    (new vision for v2.0)
├── ROADMAP.md
└── phases/
    └── 01..   (v2.0 work)
```

Use this for major rewrites where v2.0's brief is genuinely different.

## Phase numbering across milestones

Don't reset phase numbers. v1.1's phases continue from v1.0's last phase:

```
v1.0: phases 01-04
v1.1: phases 05-08
v1.2: phases 09-12
v2.0: phases 13-20 (still continuous; just a bigger version bump)
```

Phase IDs are unique forever; milestone IDs are the user-facing version.

## Major / minor / patch decisions

Semantic versioning (semver):
- **Major (v2.0)** — breaking changes; users must migrate
- **Minor (v1.1)** — new features, backwards-compatible
- **Patch (v1.0.1)** — bug fixes only

For non-library projects (apps, services), the rules are looser but the spirit is the same: signal to users what to expect.

When a phase introduces a breaking change, the next milestone is major (bump from 1.x to 2.0).

## Milestone reviews

After each milestone ships, a brief retrospective:

```markdown
# Retro: v1.0

## What went well
- ...

## What surprised us
- ...

## What to change for next milestone
- ...

## Action items for v1.1
- ...
```

Save under `.planning/retros/v1.0-retro.md` (committed to repo).

This feeds the v1.1 brief / roadmap with lessons.

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/checkpoints.md` — checkpoints at milestone boundaries
- `references/git-integration.md` — git tag conventions
- `references/scope-estimation.md` — milestone-level scoping
- `skills/reflect/`, `skills/lesson-learned/` — milestone retros
