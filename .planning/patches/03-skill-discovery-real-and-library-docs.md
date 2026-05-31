# Patch v0.1.3: skill-inventory rewrite (filesystem-real) + library-docs-fetch + 4-stream scope

**Date**: 2026-05-28
**Status**: ✅ Applied; all gates green
**Scope**: Two real defects in v0.1.2 surfaced by user review

## The defects

### Defect 1 — `skill-inventory` cited an MCP tool that does not exist

The v0.1.2 `skill-inventory` SKILL.md claimed it called `mcp__skills__list_skills` to discover installed skills. **That tool does not exist.** The official Claude Code documentation (https://docs.claude.com/en/docs/claude-code/skills and /plugins) describes skill discovery as filesystem-based:

- Standalone skills: `<project>/.claude/skills/<name>/SKILL.md` and `~/.claude/skills/<name>/SKILL.md`
- Plugin skills: `<plugin-root>/skills/<name>/SKILL.md` where `<plugin-root>` contains `.claude-plugin/plugin.json`
- Plugin enable state: `~/.claude/settings.json` field `enabledPlugins`

The hallucination came from naming conventions in this session's environment that LOOKED like skill-list MCP tools but weren't. Verified by filesystem inspection: `~/.claude/skills/` is real and has 53+ standalone skills; plugin caches at `/var/folders/.../claude-hostloop-plugins/`, `~/Library/Application Support/Claude/local-agent-mode-sessions/.../rpm/`, and cowork plugin caches are real.

### Defect 2 — Planning didn't fetch third-party library documentation

The v0.1.2 planning pre-flight had three streams (codebase-analysis + skill-inventory + observability-report). It was missing the most important one for any project with third-party dependencies: **fetching the authoritative docs for those libraries** so planning is grounded in the current API surface, not training-data recall.

The docs.claude.com page itself ships with an `llms.txt` index (header: "Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt"). That convention is widely adopted. Many libraries publish `llms.txt` at their domain root for exactly this reason. Planning should fetch it.

## Fixes applied

### Fix 1 — `skills/skill-inventory/SKILL.md` rewritten (filesystem-real)

The new SKILL.md:

- **Explicit "The MCP correction" section at top**: "There is no `mcp__skills__list_skills` tool. Skill discovery is filesystem-based. Earlier versions of this SKILL.md falsely cited an MCP tool that does not exist."
- **Documents the 3 actual source classes**: standalone (project + user), plugin (with OS-specific cache paths), bundled (always present, not enumerated)
- **Documents the actual cache paths**: hostloop, Application Support sessions, cowork_plugins cache, cowork_plugins marketplaces
- **Documents the discovery procedure with real bash**: `find ~/.claude/skills -name "SKILL.md"`, `jq -r ".enabledPlugins // {} | to_entries[] | select(.value == true) | .key" ~/.claude/settings.json`, walking plugin caches
- **Documents the enable-state cross-reference**: a plugin can be INSTALLED but not ENABLED; `~/.claude/settings.json` is the source of truth
- **Documents the namespacing**: standalone skills get `/<name>`; plugin skills get `/<plugin>:<name>` from the plugin manifest's `name` field
- **Iron Rule**: every claim about an installed skill cites a real `<path>/SKILL.md` on disk; no hallucinated MCP tools; REFUSAL.md if `~/.claude/` is unreadable

### Fix 2 — New skill `skills/library-docs-fetch/SKILL.md`

Reads `deps-summary.md` from `codebase-analysis` Stream 2. For every third-party library, fetches docs via this fallback chain:

1. **`llms.txt` probe** — `https://<library-domain>/llms.txt`, `/docs/llms.txt`, `docs.<domain>/llms.txt`
2. **Library homepage docs** — derived from `npm view <pkg> homepage` / equivalent + docs link discovery
3. **Context7 MCP** (if connected) — `mcp__78201b8b-...__resolve-library-id` + `__query-docs`
4. **GitHub README** — `raw.githubusercontent.com/<owner>/<repo>/HEAD/README.md`
5. **REFUSAL** — `e2e-evidence/<run-id>/library-docs/<library>-REFUSAL.md` if none worked

Iron Rule: no fabricated API claims. Every method/option cited in a plan task must be backed by a fetched docs file. No training-data substitution.

### Fix 3 — `/shannon:scope` now has 4 streams

Stream 1: `codebase-analysis` (unchanged)
Stream 2: `skill-inventory` (filesystem-real, no MCP)
Stream 3: `observability-report` (unchanged)
**Stream 4 (new): `library-docs-fetch`** — reads Stream 1's deps-summary; fetches per-library docs

The synthesis scope-report now has a "Third-party library API surface" section citing the fetched docs per library.

### Fix 4 — `planner` agent embeds `library-docs-fetch`

The planner's embedded_skills list goes from 7 → 8 (plan-author, interview-framework, goal-condition-architect, spec-workflow, create-meta-prompts, codebase-analysis, skill-inventory, **library-docs-fetch**). The build inlines all 8 SKILL.md bodies into the planner's AGENT.md.

### Fix 5 — `plan-author` skill refuses plans without library-docs

The "Codebase-first discipline" section now lists THREE required pre-flight outputs (was 2): codebase-analysis + skill-inventory + library-docs-fetch. Missing any of the three triggers REFUSAL.md.

The plan task citation pattern adds a 4th valid citation type:

- A specific library docs section (e.g., `Task 6.2: Use the React Server Components API as documented in e2e-evidence/<run-id>/library-docs/react.md § "Server Components" (fetched from https://react.dev/reference/rsc/server-components)`)

## Verification

| Check | v0.1.2 | v0.1.3 |
|---|---|---|
| Skills count | 32 | **33** (+library-docs-fetch) |
| Planner embedded skills | 7 | **8** (+library-docs-fetch) |
| `/shannon:scope` streams | 3 | **4** |
| skill-inventory cites real MCP-tool-list | YES (wrong) | **NO** (corrected; explicit "does not exist" callout) |
| skill-inventory cites real filesystem paths | NO | **YES** (~/.claude/skills/, plugin caches, settings.json) |
| Planning fetches library docs | NO | **YES** (Stream 4 mandatory) |
| Plan-author refuses plans without library-docs | NO | **YES** (3-pre-flight requirement) |
| doctor.py mismatches | 0 | 0 |
| build/verify-build.py mismatches | 0 | 0 |
| harness --dry-run | exit 0 | exit 0 |

## What this means operationally

After v0.1.3:

- `/shannon:plan "add a feature using react-query"` on a brownfield repo:
  1. `/shannon:scope` runs automatically (Step 0)
  2. Stream 1 reads code, produces `deps-summary.md` showing react-query@5.x as a dep
  3. Stream 2 walks `~/.claude/skills/` + plugin caches + settings.json to find any react-query-related skills you have installed
  4. Stream 3 reads recent sessions for prior react-query decisions
  5. **Stream 4 fetches https://tanstack.com/query/llms.txt (or falls back to homepage/Context7/GitHub README) and saves to `e2e-evidence/<run-id>/library-docs/react-query.md`**
  6. Planner produces plan citing specific files + specific available skills + specific react-query API methods from the fetched docs
  7. Every plan task references one of: a file path, a skill name with path, a proving-command, or a library docs section

- No "use the react-query useQuery hook" without a citation. The fetched docs are the source of truth.

## Cross-references

- `skills/skill-inventory/SKILL.md` — filesystem-real, no MCP
- `skills/library-docs-fetch/SKILL.md` — new
- `commands/scope.md` — 4 streams
- `agents/planner/manifest.yml` — embeds library-docs-fetch
- `agents/planner/AGENT.md` — inlines all 8 embedded SKILL.md bodies
- `skills/plan-author/SKILL.md` — refuses plans without all 3 pre-flight skills
- `docs/SKILLS_CATALOG.md` — regenerated with 33 skills + the corrected brownfield section
- `.planning/patches/02-mandatory-brownfield-and-skill-fix.md` — superseded by this patch

## Done condition

✓ skill-inventory is filesystem-real (no MCP tool hallucination)
✓ library-docs-fetch skill exists and is embedded in planner
✓ /shannon:scope has 4 streams (added library-docs-fetch)
✓ plan-author refuses plans without library-docs context
✓ All 8 doctor checks PASS, mismatches: 0
✓ Build OK; verify-build mismatches: 0
✓ Harness --dry-run aggregate exit 0
✓ SKILLS_CATALOG.md regenerated with 33 skills
