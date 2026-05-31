---
name: observability-report
description: Shannon-specific log reader for session, hook, and run-state diagnostics. ALWAYS use when the user says "session trace", "shannon doctor", "session log audit", "hooks fired log", "observability report", "trace the session", "run doctor", or invokes /shannon:trace, /shannon:doctor, /shannon:status, /shannon:retro. Modes — trace, doctor, status (live), session-log-audit (with optional git correlation), replay.
triggers:
  - "session trace"
  - "shannon doctor"
  - "session log audit"
  - "hooks fired log"
  - "observability report"
  - "trace the session"
  - "run doctor"
  - "shannon status"
---

# observability-report

The single skill for reading Shannon-produced logs, Claude Code session JSONLs, and active run-state files. Cross-references with `python-agent-sdk` (the producer of `hooks.jsonl`), the loop/autopilot state files, session-handoff outputs, and goal-orchestration state.

## Modes

### trace — post-hoc timeline (`/shannon:trace`)

1. Read `~/.claude/projects/<project>/<session-id>.jsonl`.
2. Stream-parse (some sessions are >100MB).
3. Filter to Shannon-relevant events using the schema in `references/event-schemas.md`:
   - hook fires (PreToolUse, PostToolUse, etc.)
   - skill triggers (`Skill(<name>)` invocations)
   - tool calls (Read/Write/Edit/Bash/Glob/Grep/Skill)
   - agent spawns (Task / Subagent)
   - banner emissions (`[SHANNON:LOOP ...]`, `[RALPH + ULTRAWORK ...]`)
4. Render chronological timeline with line citations.

`--replay <session-id>` walks events one at a time (or `--step N`) — critical for debugging stuck loops.

### doctor — installation + recent-activity health (`/shannon:doctor`)

1. Read `.claude-plugin/plugin.json` + `marketplace.json`.
2. Read `hooks/hooks.json`; verify scripts present at declared paths.
3. Read `~/.claude/settings.json`; check Shannon plugin enabled.
4. Read `~/.claude/logs/shannon/hooks.jsonl` (last 100 lines).
5. Per-check verdict with quantitative thresholds:

| Check | PASS | WARN | FAIL |
|---|---|---|---|
| plugin.json valid JSON | always | n/a | parse error |
| hooks.json declares hooks | ≥ 1 | 0 | missing file |
| hooks scripts exist | all present | some missing | none present |
| Shannon enabled in settings.json | yes | n/a | disabled |
| disableAllHooks | not set | n/a | true |
| recent hook fires | < 60 min | 60 min - 24 hr | none in 24 hr |
| hook-error rate | < 1% of fires | 1-5% | > 5% |
| autopilot lock orphaned | absent or fresh | held > 30 min | held > 6 hr |

Thresholds tunable via `~/.claude/settings.json:shannon.observability_thresholds`.

### status — live run state (`/shannon:status`)

Reads ALL active state files and prints a single dashboard:

```
[shannon:status] as of 2026-05-27T14:30:00Z

active runs:
  - autopilot: run=auto-2026-05-27-1330 phase=qa attempt=2/6 elapsed=14m12s
    last verdict: REFUSED — "test_login_flow failed at line 47"
    fingerprint history: REFUSED:test_login_flow x2 / fresh
  - /goal:     condition="<one-line>" turns=27/60 elapsed=10m32s tokens=~143k
    last evaluator reason: "<reason>"
    stall fingerprint count: 2/3
  - loop:      none active

last 5 min:
  hook fires: 312
  errors:     0
  active skill: functional-validation
```

Reads from:
- `.shannon/state/autopilot-session.txt`, `.shannon/state/autopilot-run.txt`
- `e2e-evidence/<run-id>/phase-log.md`
- `~/.claude/state/goal/<run-id>/state.json`
- `~/.claude/logs/shannon/hooks.jsonl` (last 5 min tail)

### session-log-audit — aggregate (`/shannon:retro`, `/shannon:audit --scope session`)

1. Walk `~/.claude/projects/<project>/` for sessions in declared date range.
2. Stream-parse each; extract user prompts, assistant turns, tool calls, commits, skill invocations.
3. **Optional `--correlate-git`** — for each session in range, also pull `git log --since=<session-start> --until=<session-end>` from the project's primary repo. Joins "what Claude was doing" with "what was committed."
4. Emit aggregate metrics + sample citations.

Scope syntax:
- `--since <ISO>` — open-ended from a date
- `--last N` — last N sessions
- `--session <id>` — single session
- `--branch <name>` — sessions that touched a specific branch (requires `--correlate-git`)

## Log paths Shannon writes to

```
~/.claude/logs/shannon/
  hooks.jsonl                  # one line per hook fire
                               # schema: {ts, script, matchedTool, decision, exitCode, ms, sessionId}
                               # rotated at 50MB → hooks.jsonl.1, keep last 5
  hook-errors.jsonl            # one line per crash / slow-fire (> 5s)
  open-tasks.txt               # TaskCreate/TaskUpdate listener output

~/.claude/state/goal/<run-id>/
  state.json                   # active /goal run state (see goal-orchestration)
  stall-log.jsonl              # fingerprint history

.shannon/state/
  autopilot-session.txt        # SDK session_id for active autopilot
  autopilot-run.txt            # active autopilot run-id

e2e-evidence/<run-id>/
  phase-log.md                 # autopilot phase history
  stall-log.jsonl              # autopilot fingerprint history
  transcript.jsonl             # Iron-Rule proving outputs
```

## Event schemas

See `references/event-schemas.md` for the schemas of:
- hook-fire entries
- skill-trigger entries
- tool-call entries (Read/Write/Edit/Bash/Glob/Grep/Skill)
- agent-spawn entries
- banner lines (regex)

The schemas double as the regex patterns the stream-parser uses.

## Optional exporters

For users running Shannon in CI/cloud with a real observability backend:

- `--export prometheus` — convert `hooks.jsonl` last-N lines to Prometheus exposition format on stdout.
- `--export otlp` — emit OTLP traces (requires `OTLP_ENDPOINT` env var).

Off by default; opt-in for production environments.

## Iron rules

- **Never invent log entries.** Missing log → report missing, don't fabricate.
- **Stream-parse large files.** Some sessions are >100MB; never `read_to_string` the whole thing.
- **Cite session-id + line number** when surfacing claims.
- **Live mode reads state files, not logs.** Logs are post-hoc; status is now.
- **Threshold defaults are explicit** (see doctor table).
- **`--correlate-git` is opt-in.** Don't shell out to git unless requested.

## Cross-references

- `skills/python-agent-sdk/SKILL.md` — produces `hooks.jsonl` via pre/post hooks
- `skills/loop-runner/SKILL.md` — produces `e2e-evidence/loop-<run-id>/stall-log.jsonl`
- `skills/autopilot-runner/SKILL.md` — produces `.shannon/state/autopilot-*.txt`
- `skills/goal-loop-orchestrator/SKILL.md` — produces `~/.claude/state/goal/<run-id>/state.json`
- `skills/session-handoff/SKILL.md` — surfaces in /shannon:retro
- `skills/consolidate-memory/SKILL.md` — surfaces consolidation reports
- `skills/lesson-learned/SKILL.md` — git-correlation pattern source

## References

See `references/event-schemas.md`.
