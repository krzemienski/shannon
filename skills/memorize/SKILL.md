---
name: memorize
description: Persist a session-derived pattern to memory, gated by the learner's three-question quality gate (non-Googleable + codebase-specific + hard-won). ALWAYS use when the user says "remember this", "save lesson", "memorize pattern", "save to memory", "add to memory", or invokes /shannon:reflect --mode memorize. Secret-scans, classifies expertise vs workflow, and cross-links via [[wiki-links]].
triggers:
  - "remember this"
  - "save lesson"
  - "memorize pattern"
  - "save to memory"
  - "add to memory"
  - "persist this insight"
---

# memorize

Backs `/shannon:reflect --mode memorize`. Persists session-derived patterns to disk, gated by a strict quality check so the memory store doesn't degrade into noise.

## Behavior contract

1. **Identify what to memorize** — user-pointed pattern, or pattern auto-extracted from session.
2. **Run the three-question quality gate.** Two YES + one NO → memorize. Otherwise refuse and suggest alternatives.
3. **Secret-scan the body** — regex pass for API keys, passwords, tokens. Refuse on hit.
4. **Classify** — type AND subtype.
5. **Write the memory file** with frontmatter.
6. **Update MEMORY.md** index with one-line pointer.
7. **Cross-link** existing related memories via `[[wiki-link]]`.

## The three-question quality gate

Borrowed from `learner` (oh-my-claudecode). Before writing, ask:

1. **Is this codebase-/project-specific?** (Would it apply to most projects? If YES → not worth memorizing, document in code comments instead.)
2. **Would 5 minutes of Google reveal it?** (Public knowledge → not worth memorizing.)
3. **Did it take real effort to discover?** (Trivial observation → not worth memorizing.)

The valid memorize is **two YES + one NO** — typically YES to specificity, NO to Googleable, YES to hard-won.

If the gate fails (e.g., generic principle that doesn't need to persist): refuse with a suggestion:
> "This looks like a general principle, not a codebase-specific lesson. Consider adding it to `docs/code-standards.md` or a code comment instead."

## Secret-scan

Run a regex pass on the memory body before save. Refuse on any match:

| Pattern family | Example | Decision |
|---|---|---|
| AWS access key | `AKIA[0-9A-Z]{16}` | REFUSE |
| OpenAI key | `sk-[A-Za-z0-9]{40,}` | REFUSE |
| GitHub PAT | `ghp_[A-Za-z0-9]{36,}` | REFUSE |
| Slack token | `xox[baprs]-[A-Za-z0-9-]+` | REFUSE |
| JWT-ish | `eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` | REFUSE |
| Password assignment | `(password\|passwd\|pwd)\s*[=:]\s*["'][^"']{4,}["']` | REFUSE |

Refuse hard — don't ask "include anyway?". Surface the matched line and instruct the user to redact before re-running.

## Categorize: type + subtype

### Type (existing, unchanged)
- **user** — about who the user is, role, preferences
- **feedback** — corrections + confirmations the user has given
- **project** — current work-in-progress, decisions, deadlines
- **reference** — pointers to external systems

### Subtype (new in v7, from learner)
- **expertise** — domain knowledge that can evolve as the codebase evolves
- **workflow** — stable procedural rule that should NOT evolve casually

`expertise` memories may be edited freely as understanding deepens. `workflow` memories carry a stronger "no casual edit" expectation — changes require explicit revisit and a `supersedes:` reference to the prior version.

## Frontmatter (v7 schema)

```yaml
---
name: <kebab-case-slug>
description: <one-line summary>
metadata:
  type: <user|feedback|project|reference>
  subtype: <expertise|workflow>
  created: <ISO timestamp>
  supersedes: <prior-memory-slug, optional>
  expires: <ISO date, optional>           # auto-flagged stale after this
  review_after: <ISO date, optional>      # prompt for review after this
---
```

## Body template

Borrowed from `learner`'s skill-body shape:

```markdown
# <Title>

## Insight
<one-paragraph statement of what was learned>

## Why this matters
<the specific failure mode this prevents>

## Recognition pattern
<how to know this memory applies — the smell that triggers recall>

## The approach
<concrete steps to take when the pattern is recognized>

## Example (from session that produced this memory)
<paste of the actual problem + fix from the session that prompted this>

Related: [[other-memory-slug]] [[another-related-slug]]
```

## Save location hierarchy

| Scope | Default location | When |
|---|---|---|
| **Project** (default) | `~/.claude/projects/<project>/memory/<slug>.md` | Codebase-specific, version-controlled with the project |
| **User-global** | `~/.claude/memory/<slug>.md` | Truly portable across all the user's projects (rare) |

Project is default. User-global requires explicit `--global` flag.

## MEMORY.md index

The index is **pointers only**. Never embed content directly. Format:

```markdown
# Memory index

## Feedback (corrections + preferences)
- [Login flow CSRF gotcha](login-flow-csrf-issue.md) — csrf token must be in same-origin cookie
- [Rate-limit defaults](rate-limit-defaults.md) — 60s/IP, not 5/min

## Project (current work)
- [Auth migration status](auth-migration-status.md) — v1→v2 partial, blocked on session store
...
```

## Supersedes chain

When a memory evolves (especially `subtype: expertise`):

```yaml
supersedes: rate-limit-defaults-2026-02
```

The prior memory file stays on disk (audit trail). The new file is the active one. MEMORY.md points only to the active.

## Iron rules

- **Quality gate runs FIRST.** No write without two-YES-one-NO.
- **Secret-scan is mandatory.** Refuse hard on hit.
- **Default scope is project.** Global requires `--global`.
- **Frontmatter required** with type AND subtype.
- **Body explains WHY**, follows the template.
- **MEMORY.md is index-only.** No embedded content.
- **No duplicates** — check MEMORY.md before writing; update existing if applicable.
- **Supersedes preserves audit trail.** Don't overwrite; supersede.

## Cross-references

- `skills/reflect/SKILL.md` — recurrence-promotion source (invokes this)
- `skills/consolidate-memory/SKILL.md` — periodic maintenance counterpart
- `skills/learner/SKILL.md` — three-question gate source
- `skills/session-handoff/SKILL.md` — different use-case (state vs pattern); secret-scan shared

## References

See `references/body-template.md` for the full template with worked examples.


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `consolidate-memory`

# consolidate-memory

Periodic pruning + de-duplication pass over the memory store. Where `memorize` is the **creation** primitive, this skill is the **maintenance** primitive. Without it, MEMORY.md and the handoff dir grow into noise.

## When to use

- Quarterly review (every ~90 days of project activity).
- Before a major version bump where memories should reflect the new code.
- When MEMORY.md has > 50 entries and finding the right one feels slow.
- When `/shannon:retro` runs and the retro skill detects memory bloat.
- After a major refactor — many memories may now be stale.

## When NOT to use

- The store is small (< 10 entries) — nothing to consolidate.
- Mid-active-work — disruptive to merge memories someone is using right now.
- The user just added a memory — let it settle for a week first.

## The four passes

### 1. Duplicate detection

Walk the memory store. Group by **fuzzy title similarity** + **content overlap**. Surface candidate duplicate clusters to the user with one-line summaries:

```
Cluster A:
  - login-flow-csrf-issue (created 2026-02-14, type: feedback)
  - csrf-on-login (created 2026-03-02, type: feedback)
  Title similarity: 0.78
  Recommendation: MERGE into login-flow-csrf-issue (older), supersede the other.
```

The user confirms each cluster before merge. Default action on confirm: keep the older slug, fold the newer into it, set `supersedes: <newer-slug>` on the keeper, and write a redirect stub at the newer path pointing to the keeper.

### 2. Staleness detection

For each memory, check:

- **Project memories** — does the referenced file/path still exist? Run `git ls-files <referenced_path>`. If missing → flag as STALE.
- **Reference memories** — does the external URL still resolve? Skip if no network (offline mode).
- **`metadata.expires:` field** — if set and past, flag as EXPIRED.
- **`metadata.review_after:` field** — if set and past, flag for review.

Stale memories are NOT auto-deleted. They are listed in `MEMORY.md` under a `## Stale (manual review needed)` section.

### 3. Index pruning

Walk `MEMORY.md`:

- Remove pointers to deleted memory files.
- Fix broken `[[wiki-links]]`.
- Re-sort entries by recency or category (per user preference).
- Surface entries with thin descriptions ("hmm" / "TODO") and prompt the user to expand or remove.

### 4. Handoff staleness

Walk `.claude/handoffs/`:

- **< 7 days old** — keep, no action.
- **7-30 days old** — keep, mark with `STALE_AGE` comment.
- **> 30 days old AND not chained-into** — surface for archival to `.claude/handoffs/archive/YYYY-Q*/`.
- **> 30 days old AND chained-into** — keep regardless; chain history is valuable.

## The session-handoff bridge

`consolidate-memory` checks `.claude/handoffs/*.md` for `continues_from:` chains. If a chain has 5+ links, propose creating a **digest memory** — a single memorize-style file summarizing the arc, with the handoff chain linked. This keeps long arcs surfaceable without spelunking handoff files.

## Quality gate enforcement

For every kept memory, re-apply the `learner`-derived quality gate (per `memorize`):

1. Is this codebase-/project-specific? (Y/N)
2. Would 5 minutes of Google reveal it? (Y/N)
3. Did this take real effort to discover? (Y/N)

If 2-YES + 1-NO is no longer true (e.g., what was once codebase-specific is now widely documented), propose downgrading or removing the memory.

## Output

A consolidation report at `reports/memory-consolidation-<date>.md`:

```markdown
# Memory consolidation — 2026-05-27

## Before
- Memories: 87
- Handoffs: 34
- Stale flagged: 0

## After
- Memories: 71 (16 merged into 8 clusters)
- Handoffs: 22 (12 archived to 2026-Q1)
- Stale flagged: 4 (manual review needed)

## Merged clusters
- A: login-flow-csrf-issue ← csrf-on-login (merged)
- B: rate-limiter-config ← rate-limit-tuning, rate-limit-defaults (3-way merge)

## Stale (manual review)
- legacy-auth-shim — references src/auth/v1/ which was removed 2026-04-15
- old-deploy-url — points to deploy.example.com which 404s

## Recommendations
- Memory `login-flow-csrf-issue` is now 8 months old; consider verifying it still applies.
- Two handoffs aged > 60 days were chained-into recently — kept.
```

## Iron rules

- **No auto-delete.** Every deletion is user-confirmed.
- **Mergers preserve provenance.** `supersedes:` field links old slug to new.
- **Redirect stubs replace merged files.** Don't leave dangling references.
- **Stale ≠ wrong.** Mark and surface; let the user decide.
- **Chained handoffs are not archived.** Chain history is irreplaceable context.
- **Run no more than once per quarter** for the same store. Memory takes time to mature.

## Cross-references

- `skills/memorize/SKILL.md` — creation primitive (this is its maintenance counterpart)
- `skills/session-handoff/SKILL.md` — handoff-staleness pass works on its outputs
- `skills/learner/SKILL.md` — quality-gate source
- `skills/observability-report/SKILL.md` — surfaces consolidation reports in /shannon:retro
- `skills/reflect/SKILL.md` — when reflection sees repeated gap, may propose consolidation

## Absorbed from `lesson-learned`

# Lesson Learned

Extract specific, grounded software engineering lessons from actual code changes. Not a lecture -- a mirror. Show the user what their code already demonstrates.

## Before You Begin

**Load the principles reference first.**

1. Read `references/_lesson-learned-se-principles.md` to have the principle catalog available
2. Optionally read `references/_lesson-learned-anti-patterns.md` if you suspect the changes include areas for improvement
3. Determine the scope of analysis (see Phase 1)

**Do not proceed until you've loaded at least `se-principles.md`.**

## Phase 1: Determine Scope

Ask the user or infer from context what to analyze.

| Scope | Git Commands | When to Use |
|-------|-------------|-------------|
| Feature branch | `git log main..HEAD --oneline` + `git diff main...HEAD` | User is on a non-main branch (default) |
| Last N commits | `git log --oneline -N` + `git diff HEAD~N..HEAD` | User specifies a range, or on main (default N=5) |
| Specific commit | `git show <sha>` | User references a specific commit |
| Working changes | `git diff` + `git diff --cached` | User says "what about these changes?" before committing |

**Default behavior:**
- If on a feature branch: analyze branch commits vs main
- If on main: analyze the last 5 commits
- If the user provides a different scope, use that

## Phase 2: Gather Changes

1. Run `git log` with the determined scope to get the commit list and messages
2. Run `git diff` for the full diff of the scope
3. If the diff is large (>500 lines), use `git diff --stat` first, then selectively read the top 3-5 most-changed files
4. **Read commit messages carefully** -- they contain intent that raw diffs miss
5. Only read changed files. Do not read the entire repo.

## Phase 3: Analyze

Identify the **dominant pattern** -- the single most instructive thing about these changes.

Look for:
- **Structural decisions** -- How was the code organized? Why those boundaries?
- **Trade-offs made** -- What was gained vs. sacrificed? (readability vs. performance, DRY vs. clarity, speed vs. correctness)
- **Problems solved** -- What was the before/after? What made the "after" better?
- **Missed opportunities** -- Where could the code improve? (present gently as "next time, consider...")

Map findings to specific principles from `references/_lesson-learned-se-principles.md`. Be specific -- quote actual code, reference actual file names and line changes.

## Phase 4: Present the Lesson

Use this template:

```markdown
## Lesson: [Principle Name]

**What happened in the code:**
[2-3 sentences describing the specific change, referencing files and commits]

**The principle at work:**
[1-2 sentences explaining the SE principle]

**Why it matters:**
[1-2 sentences on the practical consequence -- what would go wrong without this, or what goes right because of it]

**Takeaway for next time:**
[One concrete, actionable sentence the user can apply to future work]
```

If there is a second lesson worth noting (maximum 2 additional):

```markdown
---

### Also worth noting: [Principle Name]

**In the code:** [1 sentence]
**The principle:** [1 sentence]
**Takeaway:** [1 sentence]
```

## What NOT to Do

| Avoid | Why | Instead |
|-------|-----|---------|
| Listing every principle that vaguely applies | Overwhelming and generic | Pick the 1-2 most relevant |
| Analyzing files that were not changed | Scope creep | Stick to the diff |
| Ignoring commit messages | They contain intent that diffs miss | Read them as primary context |
| Abstract advice disconnected from the code | Not actionable | Always reference specific files/lines |
| Negative-only feedback | Demoralizing | Lead with what works, then suggest improvements |
| More than 3 lessons | Dilutes the insight | One well-grounded lesson beats seven vague ones |

## Conversation Style

- **Reflective, not prescriptive.** Use the user's own code as primary evidence.
- **Never say "you should have..."** -- instead use "the approach here shows..." or "next time you face this, consider..."
- **If the code is good, say so.** Not every lesson is about what went wrong. Recognizing good patterns reinforces them.
- **If the changes are trivial** (a single config tweak, a typo fix), say so honestly rather than forcing a lesson. "These changes are straightforward -- no deep lesson here, just good housekeeping."
- **Be specific.** Generic advice is worthless. Every claim must point to a concrete code change.
