---
name: codebase-analysis
description: Parallelized repo-wide context survey via the sciomc scientists pattern (3-7 parallel agents with [FINDING:][EVIDENCE:][CONFIDENCE:] tags), with cross-validation, proving-commands extraction, and incremental caching. ALWAYS use when the user says "analyze codebase", "repo context", "module map", "hot path identification", "survey the repo", or starts /shannon:scope. Produces structured machine-extractable findings under e2e-evidence/<run-id>/codebase-analysis/.
triggers:
  - "analyze codebase"
  - "repo context"
  - "module map"
  - "hot path identification"
  - "dependency manifest survey"
  - "survey the repo"
  - "proving-commands extraction"
---

# codebase-analysis

Stream 1 of `/shannon:scope` (and standalone-invocable). Read-only repo survey grounding the planning phase. The v1 design **parallelizes via the sciomc scientists pattern** and emits structured `[FINDING:][EVIDENCE:][CONFIDENCE:]` tags so downstream skills can grep for them.

## Behavior contract

### Fan-out: 5 parallel scientist sub-agents

Each runs at the configurable model tier (Shannon default is opus) and produces structured findings into a shared `e2e-evidence/<run-id>/codebase-analysis/` directory.

| Sub-agent | Scope | Output |
|---|---|---|
| **inventory** | All files, sizes, mtimes | `file-inventory.txt`, `INVENTORY-FINDINGS.md` |
| **deps** | Package manifests + outdated check | `deps-summary.md`, `DEPS-FINDINGS.md` |
| **entry-points** | CLI bins, route handlers, main funcs | `hot-paths.md`, `ENTRYPOINTS-FINDINGS.md` |
| **proving-cmds** | Test/build/lint/typecheck from manifests + Makefile + CI | `proving-commands.json`, `PROVING-FINDINGS.md` |
| **module-map** | Directory tree with per-dir purpose | `module-map.md`, `MODULES-FINDINGS.md` |

All five are spawned in a **single message** (parallel dispatch — see `dispatch-parallel`). The orchestrator does NOT wait for one before starting the next.

### Structured finding tags

Every fact emitted by a sub-agent uses this shape:

```
[CB-FINDING:F1] The project uses pytest as its test runner.
[EVIDENCE:F1] file: pyproject.toml lines: 23-26
  ```
  [tool.pytest.ini_options]
  minversion = "7.0"
  testpaths = ["tests"]
  ```
[CONFIDENCE:F1] HIGH
```

Downstream skills (`plan-author`, `loop-runner`, `autopilot-runner`) grep `^\[CB-FINDING:` to consume the survey output programmatically.

### Cross-validation step

After the 5 sub-agents finish, a single verification sub-agent runs:

1. **Do the entry points actually run?** For each, attempt `--help` or `--version` with a 5s timeout. Annotate `hot-paths.md` with `verified-runnable: yes/no`.
2. **Do the test/build/lint commands actually exist?** Run each with `--help` or dry-run flag; record exit code.
3. **Are the declared deps actually imported?** Grep imports for each top-level dep in `package.json` / `pyproject.toml`. Flag declared-but-unused.
4. **Contradiction sweep** — do any FINDINGS contradict each other across sub-agents? E.g., inventory says `tests/` dir exists, proving-cmds says `pytest tests/` — consistent; vs. proving-cmds says `jest src/` but inventory shows no `node_modules` — contradiction.

The verification report is `e2e-evidence/<run-id>/codebase-analysis/CROSS-VALIDATION.md`.

## Required outputs

The orchestrator merges sub-agent outputs into the canonical artifact set:

1. **`file-inventory.txt`** — all files in scope with size + last-modified.
2. **`module-map.md`** — directory tree with brief purpose per top-level dir. Each purpose tagged with `[CONFIDENCE:HIGH|MED|LOW]`.
3. **`deps-summary.md`** — parsed `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` / `Gemfile` with outdated-majors flagged.
4. **`hot-paths.md`** — entry points with `verified-runnable` annotation from cross-validation.
5. **`proving-commands.json`** — single most valuable downstream artifact:
   ```json
   {
     "test_cmd":      "pytest -q",
     "build_cmd":     "python -m build",
     "lint_cmd":      "ruff check src/",
     "typecheck_cmd": "mypy --strict src/",
     "run_cmd":       "python -m myproject",
     "extracted_from": ["pyproject.toml", "Makefile", ".github/workflows/ci.yml"]
   }
   ```
6. **`CROSS-VALIDATION.md`** — verification sub-agent's report.
7. **`README.md` + `INDEX.md`** — per `evidence-indexing` convention.

## Incremental caching

Per `session-handoff` staleness pattern:

1. Record `git rev-parse HEAD` and `git status --porcelain | wc -l` to `e2e-evidence/<run-id>/codebase-analysis/cache-fingerprint.txt` on first run.
2. On re-run, compare:
   - HEAD unchanged + no dirty files → skip entirely (print "using cache from <date>").
   - HEAD changed → diff `git diff --name-only <cached-head>..HEAD`, only re-analyze touched files for inventory/module-map; deps/proving-cmds always re-run.
   - Dirty tree → always re-run.

Cache validity expires after 7 days regardless.

## Methodology constraints

- **Glob, not find.** Glob is the Shannon-canonical search tool.
- **Read top-level configs first.** `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Gemfile`, `Makefile`.
- **Read CLAUDE.md** and `docs/codebase-summary.md` if present.
- **Grep for entry-point patterns**: `#!/usr/bin/env`, `if __name__`, `func main`, `export default function`, `module.exports`.
- **Read-only.** No source modifications.
- **No invention.** Every CB-FINDING traces to a grepped or read file (EVIDENCE block).

## When to use

- Stream 1 of `/shannon:scope` (and standalone-invocable).
- Before any non-trivial refactor (`/shannon:plan` may invoke this as prerequisite).
- Onboarding a new repo to Shannon governance.
- Before kicking off a `/shannon:autopilot` run (the proving-commands.json output feeds the autopilot's phase 4 QA).

## When NOT to use

- Single-file edit.
- Documentation-only change.
- Cached analysis < 7 days old and HEAD unchanged — use cache.

## Iron rules

- **Read-only.** No source modifications.
- **Parallel fan-out.** 5 sub-agents in one message, not sequential.
- **Structured findings.** Every fact is `[CB-FINDING:][EVIDENCE:][CONFIDENCE:]` shape.
- **Cross-validation runs.** Always. Even on cached runs (the cache may be stale in subtle ways).
- **No invention.** EVIDENCE block required for every FINDING.
- **Citations specific** — file paths + line ranges, not handwave.
- **Proving-commands.json is canonical.** Downstream skills depend on its shape.

## Cross-references

- `skills/dispatch-parallel/SKILL.md` — parallel fan-out primitive
- `sciomc` (oh-my-claudecode plugin) — scientists pattern this descends from
- `skills/evidence-indexing/SKILL.md` — INDEX.md convention
- `skills/plan-author/SKILL.md` + `skills/loop-runner/SKILL.md` + `skills/autopilot-runner/SKILL.md` — downstream consumers
- `skills/observability-report/SKILL.md` — surfaces cross-validation findings in /shannon:retro


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `codebase-analysis`

# codebase-analysis

Wraps `sequential-thinking` MCP (or equivalent). Used for multi-step reasoning where revisions matter. Theoretical grounding (Chain-of-Thought, self-consistency, tree-of-thoughts) lives in `skills/prompt-engineering-patterns/SKILL.md`.

## Behavior contract

1. Break problem into discrete thought steps (start with estimate of N steps).
2. For each step: state the thought, identify any new ambiguity, note dependencies.
3. **Revision support**: if a later step exposes that an earlier step was wrong, mark it as revised; re-derive downstream.
4. **Branch support**: if multiple viable directions exist, branch; track each branch ID; merge winning branch back to main.
5. **Hypothesis verification**: end-state hypothesis must be verified by tracing the chain of reasoning back to evidence.

## Self-consistency option (NEW)

For high-stakes decompositions where a single chain might be biased, run **N=3 chains** in parallel and take majority hypothesis. From prompt-engineering-patterns: self-consistency improves robustness by sampling diverse reasoning paths.

Trigger: when caller passes `--self-consistency` or when the problem involves contradictory evidence.

Workflow:
1. Spawn 3 codebase-analysis subagents with the same problem statement; isolated thought logs.
2. Each returns its `## Hypothesis` and `## Verification trace`.
3. If 2/3 agree on the hypothesis → emit majority hypothesis with the union of verification traces as evidence.
4. If 3 distinct hypotheses → present all three to the caller for human disambiguation; do NOT silently pick one.

Self-consistency is **optional** and skipped by default to save tokens.

## When to use

- Plan author hits a non-obvious decomposition.
- Validator finds contradictory evidence.
- Refusal-discipline needs to enumerate cascading blockers.
- Disagreement protocol in consensus-engine.

## When NOT to use

- Simple, linear task with obvious decomposition.
- Time-critical iteration (sequential analysis adds latency; self-consistency triples it).

## Output format

```markdown
## Thought 1
<step 1 reasoning>

## Thought 2
<step 2 reasoning>

## Thought 3 (revises Thought 1)
<revised reasoning + why prior thought was wrong>

## Hypothesis
<final claim>

## Verification trace
- Thought 1 → ... → Thought N → Hypothesis (each link cites evidence)
```

## Worked few-shot example

**Problem:** Login endpoint returns 200 with valid creds, but the JWT it issues is rejected by `/me` on the next call.

```markdown
## Thought 1
The login endpoint returns a JWT, which I confirmed via curl. The /me endpoint
rejects the same JWT. Hypothesis: the secret differs between issuer and verifier.

## Thought 2
Check both code paths for the env var name.
- Issuer: src/auth/login.ts reads process.env.JWT_SECRET
- Verifier: src/auth/middleware.ts reads process.env.JWT_SIGNING_KEY
Different env var names. Hypothesis updated: the deploy config sets only one.

## Thought 3 (revises Thought 1)
Thought 1 said "secret differs". More precise: the secret VARIABLE NAME differs;
the running process has only one of the two env vars set. This explains the
"verifier sees empty string" failure mode observed in logs.

## Hypothesis
The issuer signs with JWT_SECRET; the verifier reads JWT_SIGNING_KEY. In
production, only JWT_SECRET is set, so the verifier uses an empty string,
which never matches a real-issued signature.

## Verification trace
- Thought 1 cited curl output (login 200, /me 401).
- Thought 2 cited code reads of src/auth/login.ts:42 and src/auth/middleware.ts:18.
- Thought 3 cited deploy env dump showing JWT_SECRET set, JWT_SIGNING_KEY missing.
- Hypothesis follows: rename one of the two to match.
```

## Iron rules

- **No invented chain links** — every step cites prior step or external evidence (file:line, command output, log path).
- **Revisions explicit** (which earlier step is being revised, why).
- **Final hypothesis only emitted after verification trace passes.**
- If self-consistency runs and 3 chains disagree, **do not silently pick one** — surface all three.

## Cross-references

- `skills/prompt-engineering-patterns/SKILL.md` — CoT, self-consistency, tree-of-thoughts theoretical grounding.
- `skills/tree-of-thoughts/SKILL.md` — explicit tree expansion for branching with pruning + ranked-choice voting.
- `skills/root-cause-tracing/SKILL.md` — domain-specific application of codebase-analysis for debugging.
- `skills/consensus-engine/SKILL.md` — uses codebase-analysis under the hood for disagreement protocol.

## Absorbed from `library-docs-fetch`

# library-docs-fetch

Phase 0 of `/shannon:validate` for new platforms. Maps external standards to Shannon-internal validation criteria. **Shannon-unique skill** — no reference equivalent in anthropic-skills, northstar, or ralph.

## Behavior contract

1. Identify what's being validated (platform, surface, feature type).
2. Map to applicable standards (see standards-map below).
3. For each applicable standard: check **standards-library cache** first; fetch live only if missing or > 90 days old.
4. Save fresh fetches to `research/<topic>/standards/<standard>-<version>-<timestamp>.md`.
5. Map each standard's criteria to a Shannon skill: which skill covers which criterion?
6. **Coverage-gap detection**: enumerate criteria from the standard that do NOT map to any Shannon skill → flag for new-skill creation or external tool.
7. **Diff-vs-prior-version**: if the prior cached version differs from the new fetch, write `research/<topic>/standards/DIFF-<standard>-<prev>-vs-<new>.md`.
8. Output: `research/<topic>/SUMMARY.md` — table of (standard, criterion, mapped skill, evidence type required, coverage gap if any).

## Standards map (by platform / surface)

| Platform / surface | Standards |
|---|---|
| **Web UI** | WCAG 2.2 AA, Core Web Vitals (LCP/INP/CLS), HTML living standard |
| **iOS UI** | Apple HIG, iOS accessibility audit checklist |
| **macOS UI** | Apple HIG (macOS section) |
| **watchOS UI** | Apple HIG (watchOS section) |
| **visionOS UI** | Apple HIG (visionOS section), spatial computing guidelines |
| **Android UI** | Material Design 3, Android Accessibility Suite criteria |
| **Windows UI** | Fluent Design System guidelines |
| **API** | OpenAPI 3.x compliance, OWASP API Security Top 10 (current), REST conventions |
| **CLI** | POSIX argument conventions, exit-code semantics, GNU Coding Standards |
| **Security** | OWASP Top 10, OWASP ASVS, CWE Top 25, NIST SP 800-53 |
| **Privacy / data** | GDPR, CCPA, LGPD |
| **Compliance** | SOC2, HIPAA, PCI-DSS, FedRAMP, ISO 27001 |
| **Accessibility extended** | EN 301 549, Section 508 |

## Standards-to-skill mapping (illustrative)

| Standard | Criterion | Mapped Shannon skill | Evidence type |
|---|---|---|---|
| WCAG 2.2 AA | 1.4.3 Contrast (Min) | `skills/visual-inspection/SKILL.md` | screenshot + measured contrast ratio |
| WCAG 2.2 AA | 2.1.1 Keyboard | `skills/functional-validation/SKILL.md` | Playwright keyboard-only run |
| Apple HIG | Touch targets ≥ 44pt | `skills/visual-inspection/SKILL.md` (iOS) | simulator screenshot + measurement |
| OWASP API Top 10 | API1: Broken Object Level Authz | `api-validation` | curl test with foreign-user token returns 403 |
| OWASP Top 10 | A03 Injection | `skills/no-fakes-discipline/SKILL.md` + code review | static analysis report |
| POSIX | exit code 0 on success | `skills/functional-validation/SKILL.md` | command output + exit code capture |
| GDPR | Article 17 Right to Erasure | (gap — no skill maps this) | flag for new skill or human handoff |
| HIPAA | §164.312 Access Control | `api-validation` | auth + audit log evidence |

## Standards-library cache convention

Cache live in `~/.shannon/standards-library/<standard>/<version>-<YYYY-MM-DD>.md` with an index `INDEX.json`:

```json
{
  "wcag/2.2": [
    {
      "version": "2.2",
      "fetched": "2026-05-27T10:00:00Z",
      "path": "wcag/2.2-2026-05-27.md",
      "sha256": "abc123…"
    }
  ],
  "owasp-api/2023": [...]
}
```

Cache hit if `now - fetched < 90 days`. Otherwise refetch and append (do NOT overwrite).

## Coverage-gap detection algorithm

For each criterion in the fetched standard:

1. Search Shannon's `skills/` directory for any skill whose `description` or `triggers` mention the criterion or a close synonym.
2. If a match is found → record (criterion, skill, evidence type).
3. If no match → record (criterion, GAP, "needs new skill or human handoff").

The SUMMARY.md ends with a `## Coverage Gaps` section listing every GAP row. These are candidates for new Shannon skills in the next release.

## Diff-vs-prior-version

When a standard updates (WCAG 2.1 → 2.2, OWASP Top 10 2021 → 2023):

1. Detect via cache: prior version present → fetch new → compare.
2. Write `DIFF-<standard>-<prev>-vs-<new>.md` summarizing added/removed/renamed criteria.
3. Surface the diff in SUMMARY.md so plan-author knows which criteria are newly required.

## Output: SUMMARY.md template

```markdown
# Validation Research: <topic>

**Generated**: <ISO-8601>
**Platform**: <web | ios | macos | … | full-stack>
**Standards fetched**: <list with versions + dates>

## Standards-to-Skill Coverage

| Standard | Criterion | Mapped Skill | Evidence Type |
|---|---|---|---|
| ... | ... | ... | ... |

## Coverage Gaps

| Standard | Criterion | Gap |
|---|---|---|
| GDPR | Article 17 | No Shannon skill maps to right-to-erasure verification |
| ... | ... | ... |

## Diffs vs prior versions

- WCAG 2.1 → 2.2: 9 new criteria. See `standards/DIFF-wcag-2.1-vs-2.2.md`.
- ...

## Recommended Next Steps

- Add evidence for: <criteria>
- Create new skills for: <gaps>
- Human-handoff: <criteria that can't be automated>
```

## When to use

- New project / new platform onboarding.
- Validating against a new compliance regime (SOC2, HIPAA, PCI-DSS, GDPR, FedRAMP).
- Pre-`/shannon:validate` for high-stakes features.
- After a standards version bump (WCAG, OWASP).

## When NOT to use

- Already-mapped standards in a recurring project (within 90-day cache window).
- Internal-only tool with no compliance dimension.

## Iron rules

- **Always fetch live** if the cache is missing or > 90 days old — no training-data recall of standards.
- **Cite specific section / criterion number**, not "WCAG says".
- **Include retrieval timestamp** in every cached file's frontmatter.
- **Coverage gaps are first-class outputs**, not buried.
- **Cache append-only** — never overwrite prior versions; diff against them instead.

## Cross-references

- `skills/library-docs-fetch/SKILL.md` — fetches external docs (this skill uses it).
- `skills/visual-inspection/SKILL.md` — UI standards (WCAG, HIG) primary reviewer.
- `skills/functional-validation/SKILL.md` — behavioral standards primary reviewer.
- `skills/no-fakes-discipline/SKILL.md` — security standards (no mock-based gates).
- `skills/plan-author/SKILL.md` — consumer of the standards-to-skill mapping.

## Absorbed from `library-docs-fetch`

# library-docs-fetch

Documentation research mode (invoked from `/shannon:scope` or `/shannon:research`). Grounds every external dependency claim in fetched documentation, not training-data recall.

Sibling skill: `codebase-research` covers the **internal** counterpart (grep the repo for existing patterns before writing new code). Documentation-research is the **external** arm; codebase-research is the **internal** arm. Both feed `skills/plan-author/SKILL.md`'s RESEARCH.md and FINDINGS.md.

## Behavior contract

Produces `e2e-evidence/<run-id>/library-docs-fetch/` containing:

1. `sources/` — raw markdown of each fetched documentation page, with `<source>-<ISO-8601-timestamp>.md` naming.
2. `SUMMARY.md` — 3-5 verified facts per source, each linking to the local `sources/` filename.
3. `README.md` + `INDEX.md`.

## Conversation-history-first check

Before any external fetch, check whether the answer is already in this session's conversation:

```bash
# Pseudocode — the model performs this as a self-check
# 1. Did the user paste docs or quote a section?
# 2. Did a prior tool call (WebFetch, context7) already cover this?
# 3. Is the answer already in a recently-read CLAUDE.md or README?
```

If yes → cite the in-conversation source instead of refetching. Saves tokens and avoids duplicate evidence files.

## Research priority order

When research is genuinely needed, follow this order:

1. **Internal codebase** — invoke `codebase-research` first. Existing patterns are higher-confidence than external opinions.
2. **Existing local docs** — `docs/`, `CLAUDE.md`, prior `e2e-evidence/<run-id>/library-docs-fetch/`.
3. **Origin/spec docs** — the doc the plan derives from (BRIEF.md, ROADMAP.md, source design doc).
4. **Official upstream docs** — context7 MCP or canonical docs URL (WebFetch).
5. **External best practices** — only when 1-4 are silent.

## Research-plan-via-TodoWrite step

Before fetching, write a TodoWrite list of what will be researched. Keeps the research bounded and auditable:

```
[ ] Stripe SDK: confirm webhook signature verification API
[ ] Postgres: confirm jsonb index syntax for v15+
[ ] React 19: confirm hooks API for transitions
```

After each fetch, check off the corresponding item. Excess fetching beyond the list is a smell.

## Methodology

For each external dependency identified by `codebase-analysis`:

1. Prefer `context7` MCP for library docs (current, version-aware).
2. Fall back to `WebFetch` against the canonical docs URL.
3. Save the raw markdown to `sources/<lib>-<timestamp>.md`.
4. In `SUMMARY.md`, write 3-5 facts with `[source: sources/<file>]` inline citations.

## Parallel subagent pattern

For research spanning ≥4 distinct external dependencies, dispatch in parallel via `Task`:

```
[ Task: research Stripe webhook signatures → sources/stripe-*.md   ]
[ Task: research Postgres jsonb indexing  → sources/postgres-*.md  ]
[ Task: research React 19 transitions     → sources/react-*.md     ]
[ Task: research Tailwind v4 changes      → sources/tailwind-*.md  ]
```

All Task calls in a single message (per dispatch-parallel discipline). Each subagent writes its own sources/ files; main agent writes the consolidated SUMMARY.md.

## When to use

- Documentation research mode (invoked from `/shannon:scope` or `/shannon:research`).
- Before any SDK / API integration.
- When training data may be stale (recently released libraries, breaking changes in current major).

## When NOT to use

- Pure internal-codebase work with no external deps → use `codebase-research` instead.
- Already-fetched docs < 7 days old (cite the existing source file instead).

## Iron rules

- **Refuse memory-only references.** Every external-fact claim must cite a `sources/` file.
- **ISO-8601 timestamps mandatory.** Stale docs are surfaced, not silently used.
- **No invented URLs.** WebFetch only against URLs the user provided or context7 returned.
- **7-day staleness rule.** Beyond 7 days, refetch — no implicit reuse.
- **Research-priority order honored.** External fetch is the last resort, not the first.

## Cross-references

- `codebase-research` — internal-codebase sibling (grep, glob, git log).
- `skills/library-docs-fetch/SKILL.md` — Phase 0 standards-to-skill mapping (uses this skill).
- `skills/plan-author/SKILL.md` — consumer of RESEARCH.md and FINDINGS.md.
- `prompt-improver` — Phase 1 research step is structurally analogous.
- `skills/gepetto/SKILL.md` — pipeline that orchestrates research → spec → plan with cross-model review.
