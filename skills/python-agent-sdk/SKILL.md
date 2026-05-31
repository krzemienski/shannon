---
name: python-agent-sdk
description: Build production-ready AI agents with the Claude Agent SDK for Python. ALWAYS use when the user says "agent SDK", "ClaudeSDKClient", "Python SDK harness", "programmatic agent", "headless Claude", "embed Claude in pipeline", "wire SDK hooks", or when designing the autopilot harness, functional-validation harness, or any long-running orchestration. Covers query() and ClaudeSDKClient patterns, setting_sources, tool restrictions, pre/post hooks, session_id management, MCP servers, and Shannon-specific harness recipes.
triggers:
  - "agent SDK"
  - "ClaudeSDKClient"
  - "Python SDK harness"
  - "programmatic agent"
  - "headless Claude"
  - "embed Claude in pipeline"
  - "wire SDK hooks"
  - "claude_agent_sdk"
---

# python-agent-sdk

> **NOTE**: Shannon does NOT ship an MCP server. The code snippets below showing `mcp__local-evidence-writer__*` are EXAMPLE PATTERNS for users who want to build their own MCP server. Do not assume any `mcp__shannon*` tool exists.


The canonical reference for building Shannon-compatible agents on top of the `claude_agent_sdk` Python package. This skill is the foundation for I-09 (SDK functional-validation harness), the v7 autopilot lifecycle, and every headless/CI orchestration that calls into Shannon's plugin contract.

## When to use

- Embedding Shannon into a Python pipeline, CI/CD job, scheduled task, or notebook
- Building the autopilot harness, validation harness, or any long-running loop driver
- Wiring pre/post hooks on every tool call (the principled instrumentation point for `hooks.jsonl`)
- Persisting and resuming sessions via `session_id`
- Composing Shannon skills (`/shannon:*`) with custom tools and MCP servers

## When NOT to use

- One-shot interactive prompts inside Claude Code (use the chat interface)
- Trivial scripts where shelling out to `claude -p "..."` is enough
- TypeScript/Node clients (use `@anthropic-ai/claude-agent-sdk` and refer to its README)

## The two execution shapes

The SDK exposes two entry points. Pick by lifetime, not by feature.

| Shape | Lifetime | Use for |
|---|---|---|
| `query()` | Single request → response stream | Headless one-shot: render a plan, audit a file, run `/shannon:status` |
| `ClaudeSDKClient` | Persistent session, many turns | Multi-turn loops, autopilot, validation harness, anything that needs `session_id` |

## Required configuration

`ClaudeAgentOptions` is the single config object both shapes accept. Two fields are non-negotiable for Shannon:

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # REQUIRED for plugin discovery — without this, /shannon:* commands
    # and Shannon skills will not be visible to the SDK.
    setting_sources=["user", "project"],

    # Shannon defaults to opus for every agent (per v7 tier-routing
    # decision: KEEP_OPUS_DEFAULT). Tier is configurable, Shannon default
    # is opus.
    model="claude-opus-4-5",

    permission_mode="bypassPermissions",   # headless; flip to "default" interactively
    allowed_tools=["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash"],
)
```

`setting_sources=["user", "project"]` is the most common silent failure: without it the SDK boots with no settings.json hierarchy and the Shannon plugin appears uninstalled.

## query() — one-shot

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

async def render_status():
    options = ClaudeAgentOptions(
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        allowed_tools=["Skill"],
    )

    async for message in query(
        prompt="/shannon:status",
        options=options,
    ):
        print(message)

anyio.run(render_status)
```

Behaviour:
- Single request lifecycle; the stream closes when the assistant finishes its final turn.
- Reuses the user's `~/.claude/settings.json` and the project's `.claude/settings.json` (because of `setting_sources`).
- Commands are namespaced: `/shannon:spec`, `/shannon:prime`, `/shannon:autopilot`.

## ClaudeSDKClient — persistent session

```python
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def autopilot_session():
    options = ClaudeAgentOptions(
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        allowed_tools=["Skill", "Read", "Write", "Edit", "Bash"],
        model="claude-opus-4-5",
    )

    async with ClaudeSDKClient(options=options) as client:
        # Phase 1: spec
        await client.query("/shannon:spec \"Build a CLI that converts CSV to Parquet\"")
        async for msg in client.receive_response():
            handle(msg)

        # Phase 2: plan — same session, same session_id, full context retained
        await client.query("/shannon:plan")
        async for msg in client.receive_response():
            handle(msg)

        # Capture the session_id for resume
        session_id = client.session_id  # set after first turn completes

anyio.run(autopilot_session)
```

`ClaudeSDKClient` is what Shannon's autopilot, loop-runner, and functional-validation harness all build on top of.

## Hooks — the principled instrumentation point

Every tool call in the SDK runs through a hook chain. Shannon's `hooks.jsonl` log is produced by attaching pre/post hooks. This is also how the `transcript-evidence Iron Rule` is enforced in code: the post-hook surfaces command output back into the transcript before any verdict is allowed.

```python
import json
import time
from pathlib import Path
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
)

LOG = Path.home() / ".claude/logs/shannon/hooks.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)


async def pre_tool(input_data, tool_use_id, context: HookContext):
    """Runs BEFORE every tool call. Return None to allow."""
    LOG.open("a").write(json.dumps({
        "ts": time.time(),
        "phase": "pre",
        "tool": input_data["tool_name"],
        "session_id": context.session_id,
    }) + "\n")
    # Validation hook example: block Edit on archive/
    if input_data["tool_name"] == "Edit":
        path = input_data["tool_input"].get("file_path", "")
        if path.startswith("archive/"):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "archive/ is read-only in v7",
                }
            }
    return None


async def post_tool(input_data, tool_use_id, context: HookContext):
    """Runs AFTER every tool call. Append outcome to hooks.jsonl."""
    LOG.open("a").write(json.dumps({
        "ts": time.time(),
        "phase": "post",
        "tool": input_data["tool_name"],
        "session_id": context.session_id,
        "exit_code": input_data.get("tool_response", {}).get("exit_code"),
    }) + "\n")
    return None


options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    hooks={
        "PreToolUse":  [HookMatcher(matcher="*", hooks=[pre_tool])],
        "PostToolUse": [HookMatcher(matcher="*", hooks=[post_tool])],
    },
)
```

The hook signature is stable across `query()` and `ClaudeSDKClient`. Shannon's autopilot harness uses this exact pattern with two additional matchers (one for `Skill(functional-validation)` post-fire and one for `Skill(completion-gate)` post-fire) to enforce the Iron Rule.

## Session resumption

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("kick off the work")
    async for _ in client.receive_response():
        pass
    sid = client.session_id

# Later, in a different process:
options.resume = sid
async with ClaudeSDKClient(options=options) as client:
    await client.query("continue")
    async for msg in client.receive_response():
        handle(msg)
```

Shannon persists the autopilot session id to `.shannon/state/autopilot-session.txt`. Re-invocation of `/shannon:autopilot --resume <run-id>` reads it back and feeds it to `options.resume`.

## Custom tools

Define a tool with `@tool` and expose it through `create_sdk_mcp_server`:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool(
    "shannon_evidence_writer",
    "Append a verbatim command-output block to e2e-evidence/<run-id>/transcript.jsonl",
    {"run_id": str, "stream": str, "content": str},
)
async def shannon_evidence_writer(args):
    path = Path("e2e-evidence") / f"loop-{args['run_id']}" / "transcript.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a").write(json.dumps({
        "ts": time.time(),
        "stream": args["stream"],
        "content": args["content"],
    }) + "\n")
    return {"content": [{"type": "text", "text": f"wrote {path}"}]}


server = create_sdk_mcp_server(
    name="local-evidence-writer",
    version="0.1.0"  # placeholder; substitute your own version,
    tools=[shannon_evidence_writer],
)

options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    mcp_servers={"local-evidence-writer": server},
    allowed_tools=["mcp__local-evidence-writer__write"],
)
```

The allowed-tool name follows `mcp__<server>__<tool>` convention. Forgetting to add the tool name to `allowed_tools` is the second most common silent failure (after `setting_sources`).

## Shannon autopilot harness — composition recipe

The v7 autopilot lifecycle is six SDK turns against one `ClaudeSDKClient`:

```python
PHASES = ["spec", "plan", "execute", "qa", "validate", "cleanup"]

async with ClaudeSDKClient(options=options) as client:
    sid_path = Path(".shannon/state/autopilot-session.txt")

    # Resume if a prior run exists
    if sid_path.exists() and "--resume" in sys.argv:
        options.resume = sid_path.read_text().strip()

    for phase in PHASES:
        # Pre-flight: skip phase if its evidence dir already has a passing report
        if phase_already_complete(run_id, phase):
            log("phase.skip", phase=phase)
            continue

        # Each phase is a single SDK turn that drives a /shannon:* command
        await client.query(f"/shannon:{phase} --run-id {run_id}")
        async for msg in client.receive_response():
            on_message(msg)

        sid_path.write_text(client.session_id)

        # Stall detection: if the phase's verdict fingerprint matches the
        # last three attempts, exit early with STALLED_SAME_BLOCKER.
        if stalled(run_id, phase):
            break
```

This is what the v7 `autopilot-runner` and the I-09 functional-validation harness both reference. Keep the harness in `core/autopilot_harness.py` and call into it from `commands/sh_autopilot.md` via a small Python entry point.

## Preconditions gate

Borrowed from `goal-loop-orchestrator`. Run before any long-lived `ClaudeSDKClient`:

```python
def preconditions_ok() -> tuple[bool, str]:
    settings = Path.home() / ".claude/settings.json"
    if settings.exists():
        data = json.loads(settings.read_text())
        if data.get("disableAllHooks"):
            return False, "hooks are globally disabled — autopilot needs hooks"
    lock = Path.home() / ".claude/locks/shannon-autopilot.lock"
    if lock.exists():
        return False, f"another autopilot run is active: {lock.read_text().strip()}"
    return True, "ok"
```

## Iron rules

- **`setting_sources=["user", "project"]` is required.** Without it the plugin appears uninstalled.
- **Commands are namespaced.** Always `/shannon:foo`, never `foo`.
- **Hooks are the instrumentation point.** Do not parse the transcript after the fact — emit structured events from pre/post hooks.
- **No mocks in the harness.** The harness drives real `/shannon:*` commands against real plugin code. If you need an offline test path, build a fixture in `tests/fixtures/`, not a mock client.
- **Persist `session_id` immediately after the first response.** Lost session_id means lost resume.
- **The transcript-evidence Iron Rule applies to the harness.** A `PASS` verdict from the validation skill is only honoured if the proving command's exit code and final-line summary appear in the message stream.

## Cross-references

- `skills/autopilot-runner/SKILL.md` — multi-phase autopilot that consumes this harness
- `skills/loop-runner/SKILL.md` — bounded iteration loop with stall detection
- `skills/functional-validation/SKILL.md` — the validation skill whose proving commands surface through the harness
- `skills/goal-loop-orchestrator/SKILL.md` — the canonical "transcript-evidence" loop discipline
- `skills/mcp-builder/SKILL.md` — building Python/Node MCP servers
- `skills/observability-report/SKILL.md` — consuming the `hooks.jsonl` events this harness writes
