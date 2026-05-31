---
name: library-docs-fetch
description: "Fetch documentation for every third-party library identified in the codebase. Reads deps-summary.md from codebase-analysis output; for each library, probes for llms.txt at the library domain (the documented convention), falls back to the library homepage docs URL, or uses Context7 MCP if connected. Caches fetched docs to e2e-evidence run-id library-docs library-name.md so plan tasks can cite them. ALWAYS use during planning whenever the project depends on third-party libraries — the planner must know the API surface, not guess from training data. Use when user says fetch docs or pull library docs or grab third-party documentation or planning a feature that uses a library."
triggers:
  - "fetch docs"
  - "pull library docs"
  - "grab third-party documentation"
  - "fetch documentation"
  - "library documentation"
  - "llms.txt"
  - "third-party docs"
required_hooks: []
---

# library-docs-fetch

The third-party documentation pre-flight. Planning a feature that uses a library Claude has only seen in its training data is how plans end up referencing methods that don't exist or APIs that were renamed three versions ago. This skill fetches the current authoritative docs and pins them into the planning context.

## Why this exists

Every non-trivial project depends on third-party libraries — frameworks, SDKs, CLIs, packages. The planner cannot reliably plan against an external API surface from training-data recall alone:

- The library may have shipped breaking changes after training cutoff
- The library may be small enough that its API surface isn't in training at all
- The version pinned in `package.json` / `pyproject.toml` may be older or newer than what training knows
- The library may be internal / private and never indexed at all

The fix: fetch the actual current documentation BEFORE planning and feed it into the plan context. Then every plan task that touches the library can cite the fetched docs.

## When to activate

Auto-activate during `/shannon:scope` (Stream 4) and `/shannon:plan` (Step 0c) whenever `codebase-analysis` produced a non-empty `deps-summary.md`.

Manual activation also valid when the user explicitly wants library docs in the planning context.

## Input

Reads `e2e-evidence/<run-id>/codebase/deps-summary.md` (produced by `codebase-analysis` Stream 2). Expected format: one entry per third-party library with:

- `name`: package name (e.g., `react`, `axios`, `boto3`)
- `version`: pinned version from manifest
- `homepage`: URL from package metadata (if known)
- `purpose`: one-line summary of why this dep exists in the project

## Discovery procedure (per library)

For each library in `deps-summary.md`, try these sources in order. Stop at the first success.

### 1. `llms.txt` at library domain

Per the convention adopted by docs.claude.com and many other documentation sites (see the `<llms.txt>` header in `https://code.claude.com/docs/en/skills` which says "Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt"), probe:

```
https://<library-domain>/llms.txt
https://<library-domain>/docs/llms.txt
https://docs.<library-domain>/llms.txt
```

If the homepage URL is known, derive the domain. If unknown, try `https://<pkg-name>.dev/llms.txt`, `https://<pkg-name>.io/llms.txt`, `https://<pkg-name>.org/llms.txt` (well-known patterns).

If any `llms.txt` is returned, fetch it. It's expected to be a markdown index of the library's docs. Then fetch each documented section.

### 2. Library homepage docs

If `llms.txt` is not available, fetch the library homepage from `homepage` (in `deps-summary.md` or from `npm view <pkg> homepage` / equivalent). Then locate the docs link on the homepage and fetch.

### 3. Context7 MCP (if connected)

If neither `llms.txt` nor a homepage docs link works, AND Context7 MCP is connected to this Claude Code session, call:

- `mcp__78201b8b-5b27-4742-b432-e290ce1c972f__resolve-library-id` with `<pkg-name>` to get a context7 library id
- `mcp__78201b8b-5b27-4742-b432-e290ce1c972f__query-docs` with that id to get the docs

Cache the result.

### 4. GitHub README fallback

If the package has a known GitHub URL (often present in `package.json`/`Cargo.toml`/`pyproject.toml` as `repository.url`), fetch the README from `https://raw.githubusercontent.com/<owner>/<repo>/HEAD/README.md`.

### 5. REFUSAL

If none of the above worked, write `e2e-evidence/<run-id>/library-docs/<library-name>-REFUSAL.md` citing:

- Each URL attempted
- The HTTP status / error returned
- Recommendation: the user must manually provide docs, OR plan-author must mark this library as "API surface unknown, plan with extra defensiveness"

DO NOT silently substitute training-data recall. The Iron Rule applies: no fabricated documentation.

## Output

For each library:

```
e2e-evidence/<run-id>/library-docs/
├── INDEX.md                          # one-line-per-library inventory + source URL
├── <library-1>.md                    # fetched docs body (or llms.txt + key sections)
├── <library-2>.md
├── <library-3>-REFUSAL.md            # if discovery failed
...
```

`INDEX.md` shape:

```markdown
# Library docs inventory — <run-id>

| Library | Version | Source | Status |
|---|---|---|---|
| react | 18.3.1 | llms.txt at https://react.dev/llms.txt | OK |
| axios | 1.7.4 | homepage docs at https://axios-http.com/docs/ | OK |
| my-internal-lib | 0.2.0 | (none found — REFUSAL.md) | REFUSED |
```

## How plan-author consumes this

When `plan-author` produces a plan task that touches library `react`, it MUST cite either:

- A specific section of `e2e-evidence/<run-id>/library-docs/react.md` (cite the path + heading), OR
- A `REFUSAL.md` if docs weren't available, and pair the task with explicit defensive measures (try/catch, version-pinning, etc.)

No "use the standard React hooks API" without a citation. The fetched docs are the source of truth for this plan.

## Iron Rule

- **No fabricated library API claims.** Every API method/option cited in a plan task must be backed by a fetched docs file.
- **Fetch is real.** Real HTTP via WebFetch or Context7 MCP. Empty/error responses become REFUSAL.md, not silent training-data fallback.
- **Pinned-version awareness.** If the project pins an older version, prefer fetching that version's docs (most docs sites have `/v<version>/` or release-tagged URLs). Cite the exact version fetched.
- **Cache, do not re-fetch on every plan.** Once `e2e-evidence/<run-id>/library-docs/<library>.md` exists for a run, subsequent plan-author invocations reuse the cached file. Fresh fetch only on new run-id.

## Related skills

- `codebase-analysis` — produces the deps list this skill consumes
- `skill-inventory` — the capability-side companion
- `plan-author` — the consumer (cites fetched docs in plan tasks)
- `refusal-discipline` — applies when no docs source works
