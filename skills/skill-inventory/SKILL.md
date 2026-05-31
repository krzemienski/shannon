---
name: skill-inventory
description: "Enumerate every skill available in the user Claude Code environment by READING THE FILESYSTEM. Skills live as files at known paths — there is no MCP tool that returns a skill list. Three sources: standalone skills at ~/.claude/skills/<name>/SKILL.md and <project>/.claude/skills/<name>/SKILL.md; plugin skills at <plugin-root>/skills/<name>/SKILL.md where plugin-root contains .claude-plugin/plugin.json; bundled skills shipped with Claude Code itself. Cross-reference ~/.claude/settings.json enabledPlugins to know which plugins are active. Use during planning, before any /shannon:plan or /shannon:cook runs, when the user says find skills for this or which skills apply here or inventory skills or what skills exist."
triggers:
  - "find skills for this"
  - "what skills do I have"
  - "which skills apply here"
  - "inventory my skills"
  - "discover skills for"
  - "skill inventory"
  - "what skills exist"
required_hooks: []
---

# skill-inventory

The capability-side of brownfield analysis. While `codebase-analysis` reads the code, `skill-inventory` reads the user's `~/.claude/` and plugin caches to enumerate what tools are on the bench.

## The MCP correction

**There is no `mcp__skills__list_skills` tool.** Skill discovery is **filesystem-based**. Earlier versions of this SKILL.md falsely cited an MCP tool that does not exist. The corrected discovery procedure is below.

## Where skills actually live

Per the official Claude Code skills documentation (https://docs.claude.com/en/docs/claude-code/skills) and plugins documentation (https://docs.claude.com/en/docs/claude-code/plugins), skills live in THREE source classes:

### Source A — Standalone skills (project + user level)

| Path | Scope | Skill name in `/help` |
|---|---|---|
| `<project>/.claude/skills/<name>/SKILL.md` | This project only | `/<name>` (no prefix) |
| `~/.claude/skills/<name>/SKILL.md` | All projects, per-user | `/<name>` (no prefix) |
| `<project>/.claude/commands/<name>.md` | This project only | `/<name>` (commands are skills) |
| `~/.claude/commands/<name>.md` | All projects, per-user | `/<name>` (commands are skills) |

Per the docs: "A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way."

### Source B — Plugin skills (namespaced)

| Path pattern | Source |
|---|---|
| `<plugin-root>/skills/<name>/SKILL.md` where `<plugin-root>` contains `.claude-plugin/plugin.json` | Any installed plugin |
| `<plugin-root>/commands/<name>.md` (same root) | Plugin commands |

The plugin-root for INSTALLED plugins lives in one of these OS-specific caches:

- **macOS hostloop cache**: `/var/folders/x9/.../claude-hostloop-plugins/<hash>/`
- **macOS Application Support cache**: `~/Library/Application Support/Claude/local-agent-mode-sessions/<session>/<session>/rpm/plugin_<id>/`
- **Cowork plugin cache**: `~/Library/Application Support/Claude/local-agent-mode-sessions/<session>/<session>/cowork_plugins/cache/<marketplace>/<plugin>/<version>/`
- **Marketplace-uploaded plugins**: `cowork_plugins/marketplaces/<marketplace>/<plugin>/`

Plugin skill name in `/help` is namespaced: `/<plugin-name>:<skill-name>` per the plugin manifest at `<plugin-root>/.claude-plugin/plugin.json` field `name`.

### Source C — Bundled skills

Claude Code ships with a small set of built-in skills (`/help`, `/compact`, `/debug`, `/code-review` per the docs). These are not enumerated by this skill — they are always present.

## How to know which plugin skills are ACTIVE

Read `~/.claude/settings.json` for two fields:

1. **`enabledPlugins`** — map of `<plugin-name>@<marketplace>` → `true|false`. Only `true` entries are active in this session.
2. **`extraKnownMarketplaces`** — declares marketplace paths, lets you resolve `<plugin>@<marketplace>` to a filesystem location.

A plugin can be INSTALLED (files present in a cache dir) but not ENABLED. The settings.json is the source of truth for enable state.

## Discovery procedure (mechanical, no fabrication)

```bash
# 1. Standalone user-level skills
find ~/.claude/skills -name "SKILL.md" -maxdepth 3 -type f
find ~/.claude/commands -name "*.md" -maxdepth 2 -type f

# 2. Standalone project-level skills (run from the project root)
find ./.claude/skills -name "SKILL.md" -maxdepth 3 -type f 2>/dev/null
find ./.claude/commands -name "*.md" -maxdepth 2 -type f 2>/dev/null

# 3. Plugin skills — walk every plugin cache + filter by enabledPlugins
# a. Resolve enabled plugins from settings:
jq -r ".enabledPlugins // {} | to_entries[] | select(.value == true) | .key" ~/.claude/settings.json

# b. For each enabled plugin (format: <name>@<marketplace>), find its plugin-root:
#    - Check ${CLAUDE_PLUGIN_ROOT} env if set
#    - Check the hostloop cache: ls /var/folders/*/T/claude-hostloop-plugins/*/
#    - Check Application Support sessions: ls ~/Library/Application\ Support/Claude/local-agent-mode-sessions/*/*/rpm/
#    - Check cowork_plugins/cache and cowork_plugins/marketplaces

# c. For each plugin-root found, enumerate:
find "<plugin-root>/skills" -name "SKILL.md" -maxdepth 3 -type f
find "<plugin-root>/commands" -name "*.md" -maxdepth 2 -type f
```

Read every SKILL.md frontmatter found. Extract `name`, `description`, `triggers`. These are the inputs for relevance matching.

## Relevance matching (mechanical, cited)

Two-pass match against the task description:

**Pass 1 — exact trigger overlap.** For every skill, walk its `triggers:` list. If the task description contains any trigger phrase (case-insensitive substring), mark "directly relevant" with the matched phrase cited.

**Pass 2 — description keyword overlap.** For skills not matched in Pass 1, tokenize the skill `description` and the task description, intersect content keywords (drop stopwords). If overlap ≥ 2 keywords, mark "tangentially relevant" with the overlapping terms cited.

Skills with neither match go in "installed but unmatched".

## Output format

```markdown
# Skill inventory — <run-id>

## Task
<verbatim task description>

## Sources scanned
- standalone-user: ~/.claude/skills/ → N skills found
- standalone-project: ./.claude/skills/ → N skills found
- plugin-skills: N plugins enabled, M skill files found across plugin caches
- bundled: not enumerated (always present: /help, /compact, /debug, /code-review)

## Directly relevant (N skills)

| Skill | Source | Path | Triggered by phrase |
|---|---|---|---|
| `<name>` or `<plugin>:<name>` | standalone-user / standalone-project / plugin:<plugin-name> | <full filesystem path> | "<matched trigger>" |

## Tangentially relevant (N skills)

[same shape, "Triggered by" replaced with "Keyword overlap"]

## Installed but unmatched (N skills)

[plain list — informational. The user has these but they do not match this task.]

## Recommendations

- For <subtask 1>: invoke `Skill: <name>` from `<source>` (path: `<path>`)
- For <subtask 2>: invoke `Skill: <plugin>:<name>` (namespaced; see plugin manifest at `<path>/.claude-plugin/plugin.json`)
```

## Iron Rule

- **Discovery is filesystem-based.** Every claim about an installed skill cites a real `<path>/SKILL.md` that exists on disk.
- **Enable state is settings-based.** Every plugin skill claim cross-references `~/.claude/settings.json` `enabledPlugins`.
- **No hallucinated MCP tools.** The Iron Rule version of this skill does NOT cite any `mcp__skills__*` tool — those do not exist.
- **No fabricated recommendations.** Suggesting a skill that was not found in any of the scan paths is REFUSED. If a search across all paths turns up nothing for the task, the report says so and stops.
- **If `~/.claude/` is not readable** (permissions, exotic install path), write `REFUSAL.md` citing the unreadable path. Do not guess.

## Uninstalled candidates (optional, with web-fetch)

If the task description plus the discovery results suggest the user might want a skill they don't have, this skill can optionally probe the public Claude community marketplace at `https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json` via WebFetch. Any match must cite the marketplace entry's URL. This pass is OFF by default; pass `--include-uninstalled` to enable.

## Related skills

- `codebase-analysis` — the code-side companion (what the code does)
- `library-docs-fetch` — the docs-side companion (third-party library documentation)
- `observability-report` — recent session context
- `plan-author` — the consumer (uses the inventory to ground plan tasks)
