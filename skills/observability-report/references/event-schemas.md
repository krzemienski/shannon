# Shannon Event Schemas

> The shapes of events that appear in Claude Code session JSONLs and Shannon-produced logs. Reference for `/shannon:trace` and observability reports.

## Where events live

Claude Code writes session events to:

```
~/.claude/projects/<project-slug>/<session-id>.jsonl
```

Each line is one event. Some sessions are >100MB; always stream-parse, never load whole.

Shannon-produced logs live at:

```
.v7/runs/*/bench.jsonl
.evidence/I-*/transcript.json
.omc/state/sessions/<session-id>/*.json
```

## Top-level event shape

Every event has at minimum:

```json
{
  "type": "<event-type>",
  "timestamp": "<ISO8601 or ms-since-epoch>",
  ...type-specific fields
}
```

The discriminator is `type`. Filter by type when scanning.

## Event types (the ones Shannon trace cares about)

### tool_use

A tool being invoked by the assistant.

```json
{
  "type": "tool_use",
  "id": "<tool-call-id>",
  "name": "Read | Write | Edit | Bash | Glob | Grep | Task | Skill | ...",
  "input": { ... tool-specific arguments ... },
  "timestamp": "..."
}
```

Filter:
- `Task` calls = sub-agent dispatches (count = parallelism factor)
- `Skill` calls = skill invocations (cascade of behavioral activation)
- `Bash` calls = real-system actions (each one is potential evidence)
- `Write` / `Edit` calls = file mutations

### tool_result

The output of a tool_use.

```json
{
  "type": "tool_result",
  "tool_use_id": "<id of the matching tool_use>",
  "content": "<output text or structured data>",
  "is_error": true | false,
  "timestamp": "..."
}
```

Pair each `tool_result` with its `tool_use` by `tool_use_id`. Compute duration from timestamps.

### assistant_message

The model's textual response.

```json
{
  "type": "assistant_message",
  "content": [
    { "type": "text", "text": "..." },
    { "type": "tool_use", ... },
    ...
  ],
  "timestamp": "..."
}
```

The assistant message can contain MULTIPLE tool_use blocks — that's the single-message-multi-Task parallel pattern. When counting parallelism, look for tool_use count within ONE assistant_message.

### user_message

User input.

```json
{
  "type": "user_message",
  "content": "...",
  "timestamp": "..."
}
```

### hook_fire

A Claude Code hook firing (PreToolUse, PostToolUse, Stop, etc.).

```json
{
  "type": "hook_fire",
  "hook_name": "PreToolUse:Write",
  "hook_event": "...",
  "decision": "allow | block | warn",
  "decision_reason": "...",
  "timestamp": "..."
}
```

Shannon's hooks (`block-fab-files`, `evidence-gate`, etc.) emit these. A `decision=block` is a hook refusing the tool call — that's a finding.

### subagent_dispatch / subagent_result

Sub-agent (Task tool) lifecycle.

```json
{
  "type": "subagent_dispatch",
  "subagent_type": "general-purpose | meta-judge | team-builder | ...",
  "description": "...",
  "prompt": "...",
  "agent_id": "<unique id>",
  "timestamp": "..."
}

{
  "type": "subagent_result",
  "agent_id": "<matches dispatch>",
  "result": "...",
  "total_tokens": 12345,
  "tool_uses": 42,
  "duration_ms": 60000,
  "timestamp": "..."
}
```

Pair by `agent_id`. Compute per-subagent metrics from the result.

### skill_invocation

A skill being invoked via the Skill tool.

```json
{
  "type": "skill_invocation",
  "skill_name": "functional-validation | judge | ...",
  "args": "...",
  "result": "loaded | failed",
  "timestamp": "..."
}
```

Skill invocations indicate which behavioral patterns activated. A skill that loads but never runs is a smell (maybe over-broad description triggering).

### shannon_banner

Shannon-emitted bracket-prefix lines (e.g., `[SHANNON:LOOP iteration=3]`, `[RALPH + ULTRAWORK]`).

```json
{
  "type": "shannon_banner",
  "banner": "SHANNON:LOOP",
  "fields": { "iteration": 3, "metric": 0.87 },
  "timestamp": "..."
}
```

Some banners are emitted as bare assistant_message text — parse them by matching the bracket prefix.

## Computed metrics (derived from events)

The observability report computes:

| Metric | How |
|--------|-----|
| Total tool calls | count(tool_use) |
| Tool call distribution | group by name, count |
| Sub-agent dispatches | count(type=tool_use AND name=Task) |
| Parallelism factor | max(tool_use count within single assistant_message where name=Task) |
| Skill invocations | count(skill_invocation) |
| Hook fires | count(hook_fire) |
| Hook blocks | count(hook_fire WHERE decision=block) |
| Wall clock | last_timestamp - first_timestamp |
| Per-subagent avg tokens | mean(subagent_result.total_tokens) |
| Failure rate | count(tool_result WHERE is_error=true) / count(tool_result) |

## Trace modes (`/shannon:trace`)

### Mode: timeline

Chronological list of events filtered to the interesting types.

```
00:00.000  user_message       "Build me a feature..."
00:00.234  assistant_message  (text)
00:01.500  tool_use           Skill("functional-validation")
00:01.600  skill_invocation   skill_name=functional-validation
00:02.000  tool_use           Bash("npm test")
00:18.500  tool_result        is_error=false, content=...
00:18.700  hook_fire          PostToolUse:Bash, decision=allow
...
```

### Mode: focus-on-subagents

Show only sub-agent dispatch + result pairs.

```
[dispatch]   agent-id=a1b2  subagent_type=general-purpose
[result]     agent-id=a1b2  tokens=45_000  tool_uses=23  duration=180s
```

### Mode: focus-on-hooks

Show hooks fired + their decisions.

```
PreToolUse:Write       decision=block   reason="block-fab-files: test_*.py refused"
PreToolUse:Write       decision=allow
PreToolUse:Task        decision=allow
Stop                   decision=allow
```

Hook blocks are findings.

## Doctor mode (`/shannon:doctor`)

Aggregate health check across a session:

- Are all hooks firing as expected (per `hooks/hooks.json`)?
- Is the parallelism factor ≥1.5 when multiple Tasks were dispatched?
- Are evidence files written to expected paths?
- Are any banners in error/warning state?

The doctor output is a checklist with PASS/WARN/FAIL per check.

## Status mode (`/shannon:status`)

Live view of currently-active state files:

- Active autopilot phase (from `.omc/state/autopilot-state.json`)
- Active loop iteration (from `loop-runner` state)
- Pending tasks (from task tracking)
- Recent hook fires (last N)

## Session-log audit

The audit mode correlates events with git history. For each git commit during the session, identify which assistant_message produced it (by file paths in commit vs file paths in Write/Edit tool_use).

Output: per-commit attribution showing which assistant decisions led to the commit.

## Replay mode

Re-render past events as if they were happening now. Useful for:
- Debugging an old session's behavior
- Showing a colleague what happened
- Validating that a fix would have caught a prior failure

## Anti-patterns when reading event logs

| Anti-pattern | Why | Do instead |
|---|---|---|
| Loading the whole JSONL into memory | Sessions can be >100MB | Stream-parse line by line |
| Trusting assistant_message text without tool_result | Model can claim things it didn't actually verify | Always check tool_result for the underlying tool call |
| Counting tool_use without filtering by name | "47 tool calls" is uninformative | Group by name; report meaningfully |
| Ignoring hook_fire events | Hook decisions are first-class signals | Always include hook decisions in the trace |
| No timeline view | Hard to see cause-effect | Always offer chronological view |

## Cross-references

- `skills/observability-report/` — parent skill
- `skills/python-agent-sdk/` — the SDK that produces transcript.json
- `skills/trace/` — adjacent tracing skill (oh-my-claudecode pattern)
- `commands/trace.md`, `commands/doctor.md`, `commands/retro.md` — slash-command entry points
