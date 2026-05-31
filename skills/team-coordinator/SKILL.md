---
name: team-coordinator
description: Multi-teammate orchestration lead. ALWAYS use when the user says "spawn team", "coordinate teammates", "multi-agent team", "team charter", "team plan", "team execute", "team verify", or invokes /shannon:team. Staged pipeline (team-plan → team-prd → team-exec → team-verify → team-fix). Maintains shared TaskList, handoff documents, watchdog policy, BLOCKING shutdown protocol, idempotent recovery. Spawns specialized agents per stage via team-builder / team-qa / team-validator.
triggers:
  - "spawn team"
  - "coordinate teammates"
  - "multi-agent team"
  - "team charter"
  - "team plan"
  - "team execute"
  - "team verify"
  - "team fix"
required_hooks:
  - subagent-governance
  - stop-semantics
---

# team-coordinator

Entry orchestrator for Shannon's staged team runtime. Backs `/shannon:team`. Manages the lifecycle from charter parsing through verification, with stage-specific agent routing, handoff documents, watchdog policy, BLOCKING shutdown protocol, and idempotent recovery.

## Staged pipeline

The canonical team runtime executes five stages in sequence, with a bounded verify/fix loop:

```
team-plan → team-prd → team-exec → team-verify ⇄ team-fix
                                       ↓ (passes)
                                    complete
```

### Stage routing table

The lead picks agents per stage — the user does not. Stage selection determines which Shannon agents are spawned and what their role is.

| Stage | Required Agents | Optional Agents | Selection Criteria |
|-------|-----------------|-----------------|--------------------|
| **team-plan** | `team-builder` (opus) | `architect` (opus), `analyst` (opus) | Use `analyst` for unclear requirements. Use `architect` for systems with complex boundaries. |
| **team-prd** | `analyst` (opus) | `critic` (opus) | Use `critic` to challenge scope. |
| **team-exec** | `team-builder` (opus) | `executor` (opus), `debugger` (opus), `designer` (opus), `writer` (opus), `test-engineer` (opus) | Match agent to subtask type. |
| **team-verify** | `team-qa` (opus), `team-validator` (opus) | `security-reviewer` (opus), `code-reviewer` (opus) | Always run `team-qa`. Add `security-reviewer` for auth/crypto changes. Add `code-reviewer` for >20 files or architectural changes. |
| **team-fix** | `team-builder` (opus) | `debugger` (opus) | Use `debugger` for type/build errors and regression isolation. |

Shannon defaults all agent tiers to **opus** per project rule. Cost-mode tier downgrade is NOT applied (per user decision `tier_routing: keep_opus_default`). Users may override individually via `.claude/settings.json`.

Risk-level review escalation:
- Security-sensitive change OR > 20 file changes → must include `security-reviewer` + `code-reviewer` in `team-verify`.

## Stage entry / exit criteria

### team-plan
- **Entry**: team invocation parsed, orchestration starts.
- **Agents**: `explore` scans codebase, `team-builder` creates task graph, optionally `analyst`/`architect`.
- **Exit**: decomposition complete; runnable task graph prepared; handoff written to `plans/handoffs/team-plan.md`.

### team-prd
- **Entry**: scope ambiguous OR acceptance criteria missing.
- **Agents**: `analyst` extracts requirements, optionally `critic`.
- **Exit**: acceptance criteria and boundaries explicit; handoff written to `plans/handoffs/team-prd.md`.

### team-exec
- **Entry**: TeamCreate + TaskCreate + pre-assignment + worker spawn complete.
- **Agents**: workers spawned as appropriate specialist type per subtask (see routing table).
- **Exit**: execution tasks reach terminal state for current pass; handoff written to `plans/handoffs/team-exec.md`.

### team-verify
- **Entry**: execution pass finishes.
- **Agents**: `team-qa` + `team-validator` + task-appropriate reviewers.
- **Exit (pass)**: verification gates pass with no required follow-up.
- **Exit (fail)**: fix tasks generated; transition to `team-fix`.

### team-fix
- **Entry**: verification found defects/regressions/incomplete criteria.
- **Agents**: `team-builder` (executor role) + optionally `debugger`.
- **Exit**: fixes complete; flow returns to `team-exec` then `team-verify`.

## Verify/fix loop and stop conditions

Continue `team-exec → team-verify → team-fix` until:
1. verification passes and no required fix tasks remain, OR
2. work reaches explicit terminal `blocked` / `failed` outcome with evidence.

`team-fix` is bounded by `max_fix_loops` (default: 3). If fix attempts exceed the limit, transition to terminal `failed` — no infinite loop.

## Stage handoff convention

When transitioning between stages, important context — decisions made, alternatives rejected, risks identified — lives only in the lead's conversation history. If the lead's context compacts or agents restart, this knowledge is lost.

**Each completing stage MUST produce a handoff document before transitioning.**

The lead writes handoffs to `plans/handoffs/<stage-name>.md` (Shannon convention — renamed from `.omc/handoffs/`).

### Handoff format

```markdown
## Handoff: <current-stage> → <next-stage>
- **Decided**: [key decisions made in this stage]
- **Rejected**: [alternatives considered and why they were rejected]
- **Risks**: [identified risks for the next stage]
- **Files**: [key files created or modified]
- **Remaining**: [items left for the next stage to handle]
```

### Handoff rules

1. Lead reads previous handoff BEFORE spawning next stage's agents. Handoff content is included in the next stage's agent spawn prompts, ensuring agents start with full context.
2. Handoffs accumulate. `team-verify` can read all prior handoffs (plan → prd → exec) for full decision history.
3. On team cancellation, handoffs survive in `plans/handoffs/` for session resume. They are NOT deleted by team teardown.
4. Handoffs are lightweight (10-20 lines max). They capture decisions and rationale, not full specifications (those live in deliverable files like DESIGN.md, PRD.md).

### Example handoff

```markdown
## Handoff: team-plan → team-exec
- **Decided**: Microservice architecture with 3 services (auth, api, worker). PostgreSQL for persistence. JWT for auth tokens.
- **Rejected**: Monolith (scaling concerns), MongoDB (team expertise is SQL), session cookies (API-first design).
- **Risks**: Worker service needs Redis for job queue — not yet provisioned. Auth service has no rate limiting in initial design.
- **Files**: DESIGN.md, TEST_STRATEGY.md, PRD.md
- **Remaining**: Database migration scripts, CI/CD pipeline config, Redis provisioning.
```

## State persistence

Team state is persisted to `.shannon/state/team-state.json`:

```json
{
  "active": true,
  "team_name": "fix-ts-errors",
  "current_phase": "team-exec",
  "agent_count": 3,
  "agent_types": "executor",
  "task": "fix all TypeScript errors",
  "fix_loop_count": 0,
  "max_fix_loops": 3,
  "stage_history": "team-plan:2026-02-07T12:00:00Z,team-prd:2026-02-07T12:01:00Z,team-exec:2026-02-07T12:02:00Z",
  "linked_loop": false,
  "started_at": "2026-02-07T12:00:00Z"
}
```

**State schema fields**:

| Field | Type | Description |
|-------|------|-------------|
| `active` | boolean | Whether team mode is active |
| `team_name` | string | Slug name for the team |
| `current_phase` | string | Current pipeline stage: `team-plan`, `team-prd`, `team-exec`, `team-verify`, `team-fix` |
| `agent_count` | number | Number of worker agents |
| `agent_types` | string | Comma-separated agent types used in team-exec |
| `task` | string | Original task description |
| `fix_loop_count` | number | Current fix iteration count |
| `max_fix_loops` | number | Maximum fix iterations before failing (default: 3) |
| `stage_history` | string | Comma-separated list of stage transitions with timestamps |
| `linked_loop` | boolean | Whether team is linked to a `loop-runner` persistence loop |
| `started_at` | string | ISO-8601 timestamp |

**Update state on every stage transition.** This enables:
- **Resume** — if the lead crashes, reading `team-state.json` reveals the last stage and team name for recovery.
- **Cancel** — the cancel skill reads `current_phase` to know what cleanup is needed.
- **Loop integration** — `loop-runner` reads team state to know if the pipeline completed or failed.

## Workflow

### Phase 1: Parse input

- Extract `N` (agent count), validate 1-20.
- Extract `agent-type` if specified (override for `team-exec` stage only).
- Extract `task` description.
- Check `.shannon/state/team-state.json` for in-flight team — if present and active, branch to [Idempotent recovery](#idempotent-recovery).

### Phase 2: Pre-flight analysis (optional)

For large ambiguous tasks, run analysis BEFORE team creation:

1. Spawn `Task(subagent_type="shannon:team-builder", ...)` with task description + codebase context.
2. Use the analysis to produce better task decomposition.
3. Create team and tasks with enriched context.

This is especially useful when task scope is unclear.

### Phase 3: team-plan stage

1. Update state: `current_phase = "team-plan"`.
2. Spawn `team-builder` agent (opus) to analyze codebase and decompose task into N subtasks. Each subtask is file-scoped or module-scoped. Identify dependencies.
3. Optionally spawn `architect` for complex systems or `analyst` for unclear requirements.
4. Write handoff to `plans/handoffs/team-plan.md`.

### Phase 4: team-prd stage (conditional)

If scope is ambiguous or acceptance criteria are missing:

1. Update state: `current_phase = "team-prd"`.
2. Spawn `analyst` to extract requirements and write PRD.
3. Optionally spawn `critic` to challenge scope.
4. Write handoff to `plans/handoffs/team-prd.md`.

Skip this stage when scope is already crisp.

### Phase 5: Create team and tasks

1. Update state: `current_phase = "team-exec"`.
2. TeamCreate with slug derived from task (e.g., `fix-ts-errors`).
3. TaskCreate per subtask with `subject`, `description`, `activeForm`. Use `blocks` / `blockedBy` arrays for dependencies.
4. Pre-assign owners via TaskUpdate `owner` field to avoid race conditions.
5. Read handoff from `team-plan` (and `team-prd` if applicable) — include in every teammate's spawn prompt.

### Phase 6: Spawn teammates

Spawn N teammates using `Task` tool with `team_name` and `name` parameters. Each teammate gets the team worker preamble (see [Agent preamble](#agent-preamble)) plus their specific assignment.

**IMPORTANT**: Spawn all teammates in a SINGLE assistant response (parallel). Do NOT serialize spawn calls.

### Phase 7: Monitor (team-exec)

Two channels:

1. **Inbound messages** — teammates send `SendMessage` to `team-lead` when they complete tasks or need help.
2. **TaskList polling** — periodically call TaskList to check overall progress.

**Coordination actions**:

- **Unblock teammate** — send `message` with guidance or missing context.
- **Reassign work** — if a teammate finishes early, use TaskUpdate to assign pending tasks; notify via SendMessage.
- **Handle failures** — if a teammate reports failure, reassign or spawn replacement.

### Phase 7.5: Watchdog policy

Monitor for stuck or failed teammates:

- **Max in-progress age**: if a task stays `in_progress` for more than 5 minutes without messages, send a status check.
- **Suspected dead worker**: no messages + stuck task for 10+ minutes → reassign task to another worker.
- **Reassign threshold**: if a worker fails 2+ tasks, stop assigning new tasks to it.
- **Heartbeat tracking**: track `lastHeartbeatAt` per worker; `consecutiveErrors >= 3` triggers quarantine.

### Phase 8: Stage transition to team-verify

1. Update state: `current_phase = "team-verify"`.
2. Write handoff to `plans/handoffs/team-exec.md`.
3. Spawn `team-qa` agent and `team-validator` agent (both opus). Optionally add `security-reviewer` / `code-reviewer` per risk-escalation rules.

### Phase 9: team-verify stage

1. `team-qa` runs the QA gate (tests, build, lint, typecheck — see `qa-loop` skill for details).
2. `team-validator` runs multi-perspective validation (correctness, security, performance, acceptance-criteria coverage).
3. If verify passes → write handoff to `plans/handoffs/team-verify.md` → transition to [Phase 11 — Completion](#phase-11-completion).
4. If verify fails → generate fix tasks → transition to team-fix.

### Phase 10: team-fix stage (loop)

1. Update state: `current_phase = "team-fix"`, increment `fix_loop_count`.
2. Spawn `team-builder` (executor role) and optionally `debugger` to apply fixes.
3. After fix tasks complete → return to team-exec for re-execution of any affected tasks → team-verify again.
4. Bounded by `max_fix_loops` (default 3). If exceeded → terminal `failed` state. Emit verdict + handoff + escalate to user.

### Phase 11: Completion

When all real tasks (non-internal) are completed AND team-verify passes:

1. Verify all subtasks marked `completed` via TaskList.
2. Execute [BLOCKING shutdown protocol](#blocking-shutdown-protocol).
3. TeamDelete.
4. Clear state: `state_clear(mode="team")`.
5. Preserve handoffs in `plans/handoffs/` for archeological reference.
6. Report summary to user.

## BLOCKING shutdown protocol

**CRITICAL**: Steps must execute in exact order. Never call TeamDelete before shutdown is confirmed.

### Step 1: Verify completion

Call TaskList — verify all real tasks (non-internal) are completed or failed.

### Step 2: Request shutdown from each teammate

Lead sends `shutdown_request` to each teammate with a unique `request_id`:

```json
{
  "type": "shutdown_request",
  "recipient": "worker-1",
  "request_id": "shutdown-<timestamp>@worker-1",
  "content": "All work complete, shutting down team"
}
```

### Step 3: Wait for responses (BLOCKING)

- Wait up to 30s per teammate for `shutdown_response`.
- Track which teammates confirmed vs timed out.
- If a teammate doesn't respond within 30s: log warning, mark unresponsive.

Teammate receives and responds:

```json
{
  "type": "shutdown_response",
  "request_id": "shutdown-<timestamp>@worker-1",
  "approve": true
}
```

After approval:
- Teammate process terminates.
- Teammate auto-removed from team config.
- Internal task for that teammate completes.

### Step 4: TeamDelete

Only after ALL teammates confirmed OR timed out:

```json
{ "team_name": "fix-ts-errors" }
```

### Step 5: Orphan scan

Check for agent processes that survived TeamDelete. Terminate any processes matching the team name whose config no longer exists (SIGTERM → 5s wait → SIGKILL).

**Shutdown sequence is BLOCKING**: do NOT proceed to TeamDelete until all teammates have either confirmed (`shutdown_response` with `approve: true`) OR timed out (30s with no response).

The `request_id` is provided in the shutdown request message that the teammate receives. The teammate must extract it and pass it back. Do NOT fabricate request IDs.

## Idempotent recovery

If the lead crashes mid-run, the team-coordinator skill detects existing state and resumes:

1. Check `.shannon/state/team-state.json` — if `active: true` AND `current_phase` is non-terminal:
2. Read team config to discover active members.
3. Resume monitor mode instead of creating a duplicate team.
4. Read handoffs from `plans/handoffs/` to recover stage transition context.
5. Call TaskList to determine current progress.
6. Continue from the last incomplete stage.

This prevents duplicate teams and allows graceful recovery from lead failures.

## Agent preamble

When spawning teammates, include this preamble in the prompt to establish the work protocol:

```
You are a TEAM WORKER in team "{team_name}". Your name is "{worker_name}".
You report to the team lead ("team-lead").
You are not the leader and must not perform leader orchestration actions.

== WORK PROTOCOL ==

1. CLAIM: Call TaskList to see your assigned tasks (owner = "{worker_name}").
   Pick the first task with status "pending" that is assigned to you.
   Call TaskUpdate to set status "in_progress":
   {"taskId": "ID", "status": "in_progress", "owner": "{worker_name}"}

2. WORK: Execute the task using your tools (Read, Write, Edit, Bash).
   Do NOT spawn sub-agents. Do NOT delegate. Work directly.

3. COMPLETE: When done, mark the task completed:
   {"taskId": "ID", "status": "completed"}

4. REPORT: Notify the lead via SendMessage:
   {"type": "message", "recipient": "team-lead", "content": "Completed task #ID: <summary>", "summary": "Task #ID complete"}

5. NEXT: Check TaskList for more assigned tasks. If you have more pending tasks, go to step 1.
   If no more tasks are assigned to you, notify the lead:
   {"type": "message", "recipient": "team-lead", "content": "All assigned tasks complete. Standing by.", "summary": "All tasks done, standing by"}

6. SHUTDOWN: When you receive a shutdown_request, respond with:
   {"type": "shutdown_response", "request_id": "<from the request>", "approve": true}

== BLOCKED TASKS ==
If a task has blockedBy dependencies, skip it until those tasks are completed.
Check TaskList periodically to see if blockers have been resolved.

== FILE OWNERSHIP ==
Every task description includes "File ownership: <glob>". You MUST respect ownership.
Cross-write outside your ownership invalidates the run; lead will halt and re-task.

== ERRORS ==
If you cannot complete a task, report the failure to the lead:
{"type": "message", "recipient": "team-lead", "content": "FAILED task #ID: <reason>", "summary": "Task #ID failed"}
Do NOT mark the task as completed. Leave it in_progress so the lead can reassign.

== RULES ==
- NEVER spawn sub-agents or use the Task tool
- ALWAYS use absolute file paths
- ALWAYS report progress via SendMessage to "team-lead"
- Use SendMessage with type "message" only -- never "broadcast"
- IRON RULE inject delivered via PreToolUse:Task hook — obey it
```

## File ownership rule (LOAD-BEARING)

Every task description must include `File ownership: <glob>`. Teammates refusing to honor ownership are halted by lead and re-tasked. No exceptions.

This is enforced by:
- The spawn prompt explicitly states ownership.
- A post-edit grep against ownership glob detects violations.
- `subagent-governance` hook delivers the IRON RULE on PreToolUse:Task.

## Communication patterns

### Teammate to lead (task completion report)

```json
{
  "type": "message",
  "recipient": "team-lead",
  "content": "Completed task #1: Fixed 3 type errors in src/auth/login.ts and 2 in src/auth/session.ts.",
  "summary": "Task #1 complete"
}
```

### Lead to teammate (reassignment or guidance)

```json
{
  "type": "message",
  "recipient": "worker-2",
  "content": "Task #3 is now unblocked. Also pick up task #5 originally assigned to worker-1.",
  "summary": "New task assignment"
}
```

### Broadcast (use sparingly — sends N separate messages)

```json
{
  "type": "broadcast",
  "content": "STOP: shared types in src/types/index.ts have changed. Pull latest before continuing.",
  "summary": "Shared types changed"
}
```

## Error handling

### Teammate fails a task

1. Teammate sends SendMessage to lead reporting failure.
2. Lead decides: retry (reassign same task to same or different worker) or skip.
3. To reassign: TaskUpdate to set new owner; SendMessage to the new owner.

### Teammate gets stuck (no messages)

1. Lead detects via TaskList — task stuck in `in_progress` for too long.
2. Lead sends SendMessage to teammate asking for status.
3. If no response within 5min, consider the teammate dead.
4. Reassign the task via TaskUpdate.

### Dependency blocked

1. If a blocking task fails, the lead must decide:
   - Retry the blocker.
   - Remove the dependency (TaskUpdate with modified `blockedBy`).
   - Skip the blocked task entirely.
2. Communicate decisions to affected teammates via SendMessage.

### Teammate crashes

1. Internal task for that teammate shows unexpected status.
2. Teammate disappears from team config.
3. Lead reassigns orphaned tasks to remaining workers.
4. If needed, spawn replacement teammate.

## Outbox auto-ingestion and team status snapshots

The lead proactively ingests outbox messages from workers, enabling event-driven monitoring without relying solely on SendMessage delivery.

### Team status snapshot

`getTeamStatus(teamName)` provides a unified snapshot combining:
- Worker registration (which workers are registered).
- Heartbeat freshness (whether each worker is alive).
- Task progress (per-worker and team-wide pending / in_progress / completed counts).
- Current task per worker.
- Recent outbox messages since last snapshot.

### Event-based actions from outbox messages

| Message Type | Action |
|--------------|--------|
| `task_complete` | Mark task completed, unblock dependents, notify dependent workers |
| `task_failed` | Increment failure sidecar, decide retry vs reassign vs skip |
| `idle` | Worker has no assigned tasks — assign pending work or begin shutdown |
| `error` | Log error, check `consecutiveErrors` for quarantine threshold |
| `shutdown_ack` | Worker acknowledged shutdown — safe to remove from team |
| `heartbeat` | Update liveness tracking |

## Cancellation

Cancellation via `/shannon:cancel`:

1. Read team state — get `team_name` and `linked_loop`.
2. Send `shutdown_request` to all active teammates.
3. Wait for `shutdown_response` (15s timeout per member).
4. TeamDelete.
5. Clear state: `state_clear(mode="team")`.
6. If `linked_loop` is true, also clear loop-runner state.

If teammates are unresponsive, TeamDelete may fail. Wait briefly and retry, or inform the user to manually clean up team resources. Handoff files in `plans/handoffs/` are PRESERVED for potential resume.

## Linked-mode composition (Team + loop-runner)

When invoked via `/shannon:team --loop` or composition with `loop-runner`, team-coordinator wraps itself in a persistence loop:

1. Loop outer iteration 1 starts.
2. Team pipeline runs: `team-plan → team-prd → team-exec → team-verify`.
3. If `team-verify` passes → loop-runner verifies → both modes complete.
4. If `team-verify` fails → team enters `team-fix` → loops back to `team-exec → team-verify`.
5. If fix loop exceeds `max_fix_loops` → loop-runner increments iteration → retries full pipeline.
6. If loop exceeds `max_iterations` → terminal `failed` state.

State linkage:
- Team state: `linked_loop = true`.
- Loop state: `linked_team = true`, `team_name = "<slug>"`.

## When to use

- 3+ independent workstreams that can parallelize.
- Tasks with clear file-ownership boundaries (no overlap).
- Need shared TaskList visibility across teammates.
- Pipelines needing staged plan → execute → verify rhythm.

## When NOT to use

- Single workstream → use `/shannon:cook` or `dispatch-parallel` sequential mode.
- Workstreams share files heavily → sequential is safer.
- Exploratory / unknown decomposition → use `/shannon:plan` first.
- Quick one-shot tasks → no need for stage gates.

## Iron rules

- IRON RULE auto-inject via PreToolUse:Task hook.
- subagent-governance hook integration on every teammate spawn.
- File-ownership-glob requirement per task description.
- Stop-task-semantics hook blocking premature Stop.
- No partial verdicts. Wait for ALL teammates before final synthesis.
- Verdict writer reads ALL evidence, not just inventories.
- Contradictions escalate to lead; lead resolves with citation, never invents.
- Shutdown protocol is BLOCKING — never short-circuit.
- Handoffs are mandatory at every stage transition.
- State persistence on every stage transition for recovery.

## Related Skills

- `agents/team-builder.md` — orchestrates parallel execution within team-exec.
- `agents/team-qa.md` — QA cycle owner for team-verify.
- `agents/team-validator.md` — multi-perspective validation for team-verify.
- `team-plan` — entry stage skill (decomposition).
- `team-prd` — requirements extraction stage.
- `team-exec` — execution stage.
- `team-verify` — verification stage.
- `team-fix` — fix stage.
- `dispatch-parallel` — used by team-builder for parallel implementation dispatch.
- `qa-loop` — used by team-qa for QA cycling.
- `judge` — used by team-validator for quorum gating.
- `consensus-engine` — alternative validation pattern.
- `loop-runner` — composes with team-coordinator for persistence loops.
- `worktree-merge-validate` — consolidation step after parallel workers operate in worktrees.
- `parallel-cli-teams` — alternative team mode using tmux CLI workers (Codex / Gemini).

## Cross-references

- `agents/team-builder.md`, `agents/team-qa.md`, `agents/team-validator.md` — the four new agent files Shannon ships in v7.
- `hooks/subagent-governance.*` — IRON RULE inject on PreToolUse:Task.
- `hooks/stop-semantics.*` — blocks Stop on incomplete tasks.
- `.shannon/state/team-state.json` — persistence file.
- `plans/handoffs/` — stage handoff documents (Shannon convention).
- `core/SUBAGENT_PATTERNS.md` — design rationale.
