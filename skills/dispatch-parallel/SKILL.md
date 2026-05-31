---
name: dispatch-parallel
description: Launch N sub-agents in parallel, sequential, or competitive mode with meta-judge verification and per-target retry. ALWAYS use when the user says "do in parallel", "parallel subagents", "fan out tasks", "competitive dispatch", "single message multi-Task", or invokes any /shannon:dispatch* command. Each subagent owns an isolated evidence directory; meta-judge generates rubric once; judge ranks outputs per target with iteration loop.
triggers:
  - "do in parallel"
  - "parallel subagents"
  - "fan out tasks"
  - "competitive dispatch"
  - "single message multi-Task"
  - "dispatch in parallel"
  - "launch subagents in parallel"
required_hooks:
  - subagent-governance
---

# dispatch-parallel

Backs all three `/shannon:dispatch*` commands. Mode determined by invocation. Implements the **Supervisor/Orchestrator pattern** with **single-message multi-Task dispatch**, **meta-judge → LLM-as-judge verification**, and **per-target retry with feedback**.

## CRITICAL — Single-message multi-Task enforcement (LOAD-BEARING)

This is the single most important rule in this skill. The Claude Code runtime parallelizes Task tool calls ONLY when they appear in the SAME assistant response. If you call Task, wait for the result, then call Task again — that is SEQUENTIAL, not parallel, regardless of what you tell the user.

### RED FLAGS — Never do these

**NEVER:**
- Wait for one subagent to complete before launching another in parallel mode
- Issue Task calls across multiple assistant turns when they are independent
- Read implementation files yourself "to understand what the subagent will do"
- Write code or modify source files directly — you are the orchestrator only
- Skip meta-judge dispatch "to save a round trip"
- Re-run meta-judge per target or per retry — meta-judge runs ONCE and its YAML is reused
- Read full judge reports — parse only the structured YAML header
- Pass the score threshold to the judge (bias-poisons the verdict)
- Proceed past max retries (3 per target) without user decision

**ALWAYS:**
- Launch ALL parallel agents in a SINGLE assistant response containing N Task tool calls
- Dispatch meta-judge ONCE before parallel implementation dispatch; reuse its YAML across every target and every retry
- Include `CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}` in meta-judge and judge prompts
- Wait for ALL parallel agents to return before dispatching their judges
- Pass the EXACT meta-judge YAML to every judge — no edits, no summary, no truncation
- Parse only `VERDICT`, `SCORE`, `ISSUES`, `IMPROVEMENTS` from judge output
- Isolate failures: one target failing does NOT stop other targets

### Why this matters

The system prompt that drives Claude Code's parallel dispatcher inspects the SET of tool calls within one assistant turn. Tools in the same turn run concurrently; tools across turns are strictly sequential. There is no "parallel queue" — there is only batching by turn. Shannon's parallel mode is meaningless unless this is honored verbatim.

## Mode contract

### Sequential mode (`/shannon:dispatch`)

1. Task list → ordered sequence.
2. Dispatch meta-judge ONCE for the entire run (specification covers acceptance criteria for every task).
3. Per task: spawn one subagent → wait → dispatch judge with the meta-judge YAML → parse verdict → retry (max 3) on FAIL → mark complete → proceed.
4. Between tasks, optionally invoke `subagent-driven-development` to run a fresh code-reviewer subagent before proceeding (see [Related Skills](#related-skills)).

### Parallel mode (`/shannon:dispatch-parallel`)

1. Task list → batches of `--max-parallel` (default: all independent targets in one batch).
2. **Phase 3.5 — Meta-judge dispatch (ONCE)**: launch a single meta-judge sub-agent to produce the evaluation specification YAML. Wait for completion.
3. **Phase 5 — Parallel implementation dispatch**: in a SINGLE assistant response, issue N Task tool calls — one per target. Each prompt contains the Zero-shot CoT prefix, the task body, and the Self-critique suffix (see [Prompt construction](#prompt-construction)).
4. Wait for ALL implementation subagents to return.
5. **Per-target judge dispatch**: for each completed target, dispatch an independent judge subagent with the meta-judge YAML. Per-target judges may be batched in a single response as well.
6. Parse each judge's verdict; per-target retry on FAIL (max 3 per target, reusing the same meta-judge YAML).
7. Emit per-target results table (see [Final summary](#final-summary)).

### Competitive mode (`/shannon:dispatch-competitive`)

1. Same task → N identical spawns in parallel (Phase 1 generators), each owning an isolated output directory.
2. Meta-judge runs in parallel with generators (Phase 1.5) — it does not depend on generator output.
3. After all generators complete: 3 judges score in parallel (Phase 2) using the meta-judge YAML.
4. **Phase 2.5 — Adaptive strategy selection**:
   - **SELECT_AND_POLISH** if VOTE is unanimous → polish the winner, optionally cherry-pick 1-2 elements from runners-up.
   - **REDESIGN** if all average scores `< 3.0` → return to Phase 1 with judge lessons-learned as new constraints.
   - **FULL_SYNTHESIS** otherwise → synthesize the best from all candidates.
5. For full POLISH / REDESIGN / SYNTHESIS process, this skill delegates to `do-competitively`; see [Related Skills](#related-skills).

## Independence validation (REQUIRED before parallel/competitive dispatch)

Before launching parallel implementation agents, verify all targets are truly independent. If ANY check fails, switch to sequential mode and inform the user why parallel was unsafe.

| Check | Question | If NO |
|-------|----------|-------|
| File Independence | Do targets share files for writes? | Cannot parallelize — file conflicts |
| State Independence | Do tasks modify shared in-memory or disk state? | Cannot parallelize — race conditions |
| Order Independence | Does execution order affect correctness? | Cannot parallelize — sequencing required |
| Output Independence | Does any target consume another's output? | Cannot parallelize — data dependency |

Independence Checklist:
- [ ] No target reads output from another target.
- [ ] No target modifies files another target reads.
- [ ] Order of completion doesn't matter.
- [ ] No shared mutable state.
- [ ] No database transactions spanning targets.

## File ownership (LOAD-BEARING for parallel and competitive)

Each subagent owns its evidence/output directory exclusively. Cross-write = invalid run.

Convention:
- Coordinator: writes NOTHING during dispatch (results aggregation happens after all agents return).
- Subagent-N: writes ONLY under `e2e-evidence/<run-id>/<target-N>/` (or the competitive analogue `solution.<a|b|c>.<ext>`).
- Judge-N: writes ONLY `.specs/reports/<target-N>-<date>.md` (per-target judge report).
- Meta-judge: writes ONLY `.shannon/state/rubric-<run-id>.yaml`.

A subagent that writes outside its directory invalidates the entire run.

## Prompt construction

Each subagent prompt MUST include three components in this exact order:

### 1. Zero-shot CoT prefix (REQUIRED — MUST BE FIRST)

```markdown
## Reasoning Approach

Let's think step by step.

Before taking any action, think through the problem systematically:

1. "Let me first understand what is being asked for this specific target..."
   - What is the core objective?
   - What are the explicit requirements?
   - What constraints must I respect?

2. "Let me analyze this specific target..."
   - What is the current state?
   - What patterns or conventions exist?
   - What context is relevant?

3. "Let me plan my approach..."
   - What are the concrete steps?
   - What could go wrong?
   - Is there a simpler approach?

Work through each step explicitly before implementing.
```

### 2. Task body (customised per target)

```markdown
<task>
{Task statement from $ARGUMENTS}
</task>

<target>
{Specific target — file path, component name, output path}
</target>

<file_ownership>
Exclusive write zone: {evidence directory or output path}
Do NOT write outside this zone. Cross-write invalidates the run.
</file_ownership>

<constraints>
- Work ONLY on the specified target.
- Follow existing patterns in the target.
- IRON RULE inject delivered via PreToolUse:Task hook — obey it.
- Acceptance criteria: {list}
</constraints>

<output>
{Expected deliverable location and format}

At the end of your work, provide a "Summary" section containing:
- Files modified (full paths)
- Key changes (3-5 bullet points)
- Any decisions made and rationale
- Potential concerns or follow-up needed
</output>
```

### 3. Self-critique suffix (REQUIRED — MUST BE LAST)

```markdown
## Self-Critique Verification (MANDATORY)

Before completing, verify your work for this target. Do not submit unverified changes.

| # | Question | Why It Matters |
|---|----------|----------------|
| 1 | Did I achieve the stated objective for this target? | Incomplete work = failed task |
| 2 | Are my changes consistent with patterns in this file/codebase? | Inconsistency creates technical debt |
| 3 | Did I introduce any regressions or break existing functionality? | Breaking changes are unacceptable |
| 4 | Are edge cases and error scenarios handled appropriately? | Edge cases cause production issues |
| 5 | Is my output clear, well-formatted, and ready for review? | Unclear output reduces value |

For each question, provide specific evidence from your work. If ANY check reveals a gap: FIX → RE-VERIFY → DOCUMENT what changed.

Do not submit until ALL verification questions have satisfactory answers.
```

## Meta-judge dispatch (Phase 3.5)

Before parallel implementation dispatch, send one meta-judge subagent to generate the evaluation specification YAML. Reuse this YAML for every per-target judge and every retry.

```markdown
## Meta-judge prompt

Generate an evaluation specification YAML for the following task. You will produce rubrics, checklists, and scoring criteria that a judge agent will use to evaluate each target's implementation artifact.

CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}

## User Prompt
{Original task description from user}

## Context
{Relevant codebase context, file paths, constraints}

## Artifact Type
{code | documentation | configuration | etc.}

## Number of Targets
{N}

## Instructions
Return only the final evaluation specification YAML in your response. Do NOT include any pass-threshold value — judges must remain blind to the threshold to avoid bias.
```

Dispatch:

```
Use Task tool:
  - description: "Meta-judge: <brief task summary>"
  - prompt: <meta-judge prompt>
  - model: opus (Shannon default — configurable via .claude/settings.json)
  - subagent_type: "shannon:meta-judge"
```

Wait for meta-judge to complete. Extract the YAML from its response. Store at `.shannon/state/rubric-<run-id>.yaml` for audit traceability.

## Per-target judge dispatch (Phase 5.2)

After each implementation subagent returns, dispatch an independent judge. Multiple judges in the same response = parallel; one per target.

```markdown
## Judge prompt

You are evaluating an implementation artifact for target {target_name} against an evaluation specification produced by the meta judge.

CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}

## User Prompt
{Original task description from user}

## Target
{Specific target}

## Evaluation Specification

```yaml
{exact meta-judge YAML — verbatim, no edits, no summary}
```

## Implementation Output
{Summary section from implementation subagent}
{Paths to files modified}

## Instructions
Follow your full judge process as defined in your agent instructions.

CRITICAL: Reply with the structured evaluation YAML header at the START of your response.
```

Parse only the YAML header:

```
VERDICT: PASS or FAIL
SCORE: X.X/5.0
ISSUES: [list]
IMPROVEMENTS: [list]
```

### Decision logic per target

```
If SCORE >= 4.0:
  → PASS. Mark target complete. Surface IMPROVEMENTS as optional.

If SCORE >= 3.0 AND all ISSUES are low-priority:
  → PASS (soft). Mark target complete. Surface IMPROVEMENTS.

If SCORE < 4.0:
  → FAIL.
  If retries < 3:
    → Dispatch retry implementation subagent with judge ISSUES as feedback.
    → Re-judge with SAME meta-judge YAML (do NOT regenerate rubric).
  If retries >= 3:
    → Mark target FAILED. Continue other targets. Escalate this target to user with persistent issues.
```

### Per-target retry prompt

```markdown
## Retry Required for Target: {target_name}

Your previous implementation did not pass judge verification.

## Original Task
{Original task description}

## Target
{Specific target}

## Judge Feedback (Attempt {N})
VERDICT: FAIL
SCORE: {score}/5.0
ISSUES:
{verbatim issues from judge}

## Your Previous Changes
{files modified in previous attempt}

## Instructions
1. Review each issue the judge identified.
2. Determine root cause for each.
3. Plan the fix.
4. Implement ALL fixes.
5. Verify your fixes address each issue.
6. Provide updated Summary section.

Focus on fixing the specific issues identified. Do not rewrite everything.
```

## Failure isolation

One target failing does NOT affect other targets. Continue processing the rest of the batch. At the end, report:

- Successful targets with judge scores.
- Failed targets with verdict history, persistent issues, and proposed options (provide guidance / skip / manual fix).

This is non-negotiable. Halting the entire batch on one failure defeats the purpose of parallelism.

## Final summary

After all targets complete (with retries as needed), aggregate:

```markdown
## Parallel Execution Summary

### Configuration
- Task: {task description}
- Mode: parallel | competitive | sequential
- Model: opus (configurable via .claude/settings.json)
- Targets: {count}

### Results

| Target | Judge Score | Retries | Status | Summary |
|--------|-------------|---------|--------|---------|
| {target_1} | {X.X}/5.0 | {0-3} | SUCCESS | {brief outcome} |
| {target_2} | {X.X}/5.0 | {0-3} | SUCCESS | {brief outcome} |
| {target_3} | {X.X}/5.0 | {3}   | FAILED  | {failure reason} |

### Overall Assessment
- Completed: {X}/{total}
- Failed: {Y}/{total}
- Total Retries: {sum}

### Files Modified
- {list of all modified files}

### Failed Targets (If Any)
For each failed target after max retries:
- Target: {name}
- Final Score: {X.X}/5.0
- Persistent Issues: {list}
- Options: Retry with guidance / Skip / Manual fix

### Next Steps
{If failures, suggest remediation; cross-reference worktree-merge-validate if parallel agents worked in worktrees}
```

## When to use

- Sequential — multi-step task with strict ordering between steps.
- Parallel — N independent tasks across files / targets with no shared writes.
- Competitive — single output decision where multiple perspectives produce candidates and the best (or synthesis) wins.

## When NOT to use

- Single short task — just do it inline, no dispatch needed.
- Cross-task state required → sequential, never parallel/competitive.
- Targets share write files → sequential or refactor scope to remove overlap.

## Iron rules

- No shared mutable state across parallel/competitive subagents.
- File ownership enforced at spawn-prompt level AND by post-task ownership-glob check.
- IRON RULE inject delivered to every subagent via `subagent-governance` hook (PreToolUse:Task).
- Model defaults to opus per Shannon project rule. Override only with explicit `--model` flag.
- Meta-judge runs ONCE per dispatch run; YAML reused across all targets and all retries.
- Failures isolated. Do NOT halt the batch on one failure.
- Pass-threshold NEVER given to judges.

## Related Skills

- `judge` — single-output evaluation; this skill calls it once per target.
- `judge-with-debate` — engine for multi-round consensus when judges disagree; used when explicitly requested or by `consensus-engine` / `judge`.
- `do-and-judge` — single-task variant of this skill (one target, meta-judge + implement + judge + retry).
- `do-in-steps` — sequential variant with per-step meta-judge.
- `do-competitively` — engine for the competitive mode's POLISH / REDESIGN / SYNTHESIS branches.
- `subagent-driven-development` — interleaves code-review subagents between sequential tasks.
- `multi-agent-patterns` — design rationale (supervisor / swarm / hierarchical, context isolation, failure modes).
- `worktree-merge-validate` — consolidation step after parallel agents work in isolated worktrees.
- `tree-of-thoughts` — for competitive mode when candidates need internal branching/sub-options.
- `consensus-engine`, `judge` — escalation paths when per-target judges disagree.

## Cross-references

- `agents/meta-judge.md` — the rubric-generator agent referenced in Phase 3.5.
- `hooks/subagent-governance.*` — auto-injects IRON RULE on every PreToolUse:Task.
- `core/SUBAGENT_PATTERNS.md` — extended design rationale and worked examples.
