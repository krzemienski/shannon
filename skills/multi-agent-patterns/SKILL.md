---
name: multi-agent-patterns
description: Design multi-agent architectures for complex tasks. Use when single-agent context limits are exceeded, when tasks decompose naturally into subtasks, or when specializing agents improves quality. Provides the "why" layer for Shannon's orchestration cluster — catalogs supervisor / swarm / hierarchical patterns, context-isolation mechanisms, consensus protocols, and failure modes.
triggers:
  - "multi-agent design"
  - "agent architecture"
  - "subagent patterns"
  - "supervisor or swarm"
  - "context isolation"
  - "agent failure modes"
required_hooks:
  - subagent-governance
---

# Multi-Agent Architecture Patterns

Multi-agent architectures distribute work across multiple agent invocations, each with its own focused context. When designed well, this distribution enables capabilities beyond single-agent limits. When designed poorly, it introduces coordination overhead that negates benefits. The critical insight is that sub-agents exist primarily to isolate context, not to anthropomorphize role division.

This skill is Shannon's **design rationale** for the orchestration cluster. It does not orchestrate by itself; it provides the vocabulary and decision-making framework used by `dispatch-parallel`, `team-coordinator`, `consensus-engine`, `judge`, `tree-of-thoughts`, and `subagent-driven-development`.

## Core concepts

Multi-agent systems address single-agent context limitations through distribution. Three dominant patterns exist: **supervisor/orchestrator** for centralized control, **peer-to-peer/swarm** for flexible handoffs, and **hierarchical** for layered abstraction. The critical design principle is **context isolation** — sub-agents exist primarily to partition context rather than to simulate organizational roles.

Effective multi-agent systems require explicit coordination protocols, consensus mechanisms that avoid sycophancy, and careful attention to failure modes including bottlenecks, divergence, and error propagation.

## Why multi-agent architectures

### The context bottleneck

Single agents face inherent ceilings in reasoning capability, context management, and tool coordination. As tasks grow more complex, context windows fill with accumulated history, retrieved documents, and tool outputs. Performance degrades according to predictable patterns: the lost-in-middle effect, attention scarcity, and context poisoning.

Multi-agent architectures address these limitations by partitioning work across multiple context windows. Each agent operates in a clean context focused on its subtask. Results aggregate at a coordination layer without any single context bearing the full burden.

### The parallelization argument

Many tasks contain parallelizable subtasks that a single agent must execute sequentially. A research task might require searching multiple independent sources, analyzing different documents, or comparing competing approaches. A single agent processes these sequentially, accumulating context with each step.

Multi-agent architectures assign each subtask to a dedicated agent with a fresh context. All agents work simultaneously, then return results to a coordinator. The total real-world time approaches the duration of the longest subtask rather than the sum of all subtasks.

### The specialization argument

Different tasks benefit from different agent configurations: different system prompts, different tool sets, different context structures. A general-purpose agent must carry all possible configurations in context. Specialized agents carry only what they need.

Multi-agent architectures enable specialization without combinatorial explosion. The coordinator routes to specialized agents; each agent operates with lean context optimized for its domain.

## Architectural patterns

### Pattern 1: Supervisor / Orchestrator

The supervisor pattern places a central agent in control, delegating to specialists and synthesizing results. The supervisor maintains global state and trajectory, decomposes user objectives into subtasks, and routes to appropriate workers.

```
User Request → Supervisor → [Specialist A, Specialist B, Specialist C] → Aggregation → Final Output
```

**When to use**: complex tasks with clear decomposition, tasks requiring coordination across domains, tasks where human oversight is important.

**Advantages**: strict control over workflow, easier to implement human-in-the-loop interventions, ensures adherence to predefined plans.

**Disadvantages**: supervisor context becomes bottleneck, supervisor failures cascade to all workers, **"telephone game" problem** where supervisors paraphrase sub-agent responses incorrectly.

**Shannon implementations**:
- `dispatch-parallel` is supervisor-pattern.
- `team-coordinator` is supervisor-pattern with staged pipelines.
- `judge` is supervisor-pattern with quorum semantics.

### Pattern 2: Peer-to-Peer / Swarm

The peer-to-peer pattern removes central control, allowing agents to communicate directly based on predefined protocols. Any agent can transfer control to any other through explicit handoff mechanisms.

**When to use**: tasks requiring flexible exploration, tasks where rigid planning is counterproductive, tasks with emergent requirements that defy upfront decomposition.

**Advantages**: no single point of failure, scales effectively for breadth-first exploration, enables emergent problem-solving behaviors.

**Disadvantages**: coordination complexity increases with agent count, risk of divergence without central state keeper, requires robust convergence constraints.

**Shannon implementations**:
- `judge-with-debate` is peer-to-peer at the debate-round level (judges read each other's reports directly from the filesystem).
- `consensus-engine` debate Phase 4 is peer-to-peer.

### Pattern 3: Hierarchical

Hierarchical structures organize agents into layers of abstraction: strategic, planning, and execution layers. Strategy layer agents define goals and constraints; planning layer agents break goals into actionable plans; execution layer agents perform atomic tasks.

```
Strategy Layer (Goal Definition) → Planning Layer (Task Decomposition) → Execution Layer (Atomic Tasks)
```

**When to use**: large-scale projects with clear hierarchical structure, enterprise workflows with management layers, tasks requiring both high-level planning and detailed execution.

**Advantages**: mirrors organizational structures, clear separation of concerns, enables different context structures at different levels.

**Disadvantages**: coordination overhead between layers, potential for misalignment between strategy and execution, complex error propagation.

**Shannon implementations**:
- `team-coordinator` staged pipeline (team-plan / team-prd / team-exec / team-verify / team-fix) is hierarchical.
- `tree-of-thoughts` exploration → pruning → expansion → evaluation → synthesis is hierarchical.

## Context isolation as design principle

The primary purpose of multi-agent architectures is context isolation. Each sub-agent operates in a clean context window focused on its subtask without carrying accumulated context from other subtasks.

### Isolation mechanisms

**Instruction passing**: for simple, well-defined subtasks, the coordinator creates focused instructions. The sub-agent receives only the instructions needed for its specific task. In Shannon, this means passing minimal, targeted prompts to subagents via the Task tool.

**File system memory**: for complex tasks requiring shared state, agents read and write to persistent storage. The file system serves as the coordination mechanism, avoiding context bloat from shared state passing. This is the most natural pattern for Shannon — agents communicate through markdown files, JSON state files, or structured documents under `.shannon/state/`, `plans/`, and `e2e-evidence/`.

**Full context delegation**: for complex tasks where the sub-agent needs complete understanding, the coordinator shares its entire context. The sub-agent has its own tools and instructions but receives full context for its decisions. Use sparingly as it defeats the purpose of context isolation.

### Isolation trade-offs

Full context delegation provides maximum capability but defeats the purpose of sub-agents. Instruction passing maintains isolation but limits sub-agent flexibility. File system memory enables shared state without context passing but introduces consistency challenges.

The right choice depends on task complexity, coordination needs, and the nature of the work.

## Consensus and coordination

### The voting problem

Simple majority voting treats hallucinations from weak reasoning as equal to sound reasoning. Without intervention, multi-agent discussions can devolve into consensus on false premises due to inherent bias toward agreement.

### Weighted contributions

Weight agent contributions by confidence or expertise. Agents with higher confidence or domain expertise carry more weight in final decisions.

### Debate protocols

Debate protocols require agents to critique each other's outputs over multiple rounds. Adversarial critique often yields higher accuracy on complex reasoning than collaborative consensus.

**Shannon implementations**: `judge-with-debate` is Shannon's debate engine. `consensus-engine` and `judge` escalate to debate when single-round consensus is non-unanimous.

### Trigger-based intervention

Monitor multi-agent interactions for specific behavioral markers:
- **Stall triggers** — activate when discussions make no progress.
- **Sycophancy triggers** — detect when agents mimic each other's answers without unique reasoning.
- **Divergence triggers** — detect when agents are moving away from the original objective.

## Failure modes and mitigations

### Failure: Supervisor bottleneck

The supervisor accumulates context from all workers, becoming susceptible to saturation and degradation.

**Mitigation**: implement output constraints so workers return only distilled summaries. Use file-based checkpointing to persist state without carrying full history in context.

### Failure: Telephone game

Supervisor paraphrases sub-agent responses incorrectly, losing fidelity.

**Mitigation**: allow sub-agents to pass responses directly when synthesis would lose important details. In Shannon, this means letting subagents write directly to shared files (or return their output verbatim) rather than having the supervisor rewrite everything. Judge reports' structured YAML headers are the explicit mechanism — the supervisor parses only the header, never paraphrases the body.

### Failure: Coordination overhead

Agent communication consumes tokens and introduces latency. Complex coordination can negate parallelization benefits.

**Mitigation**: minimize communication through clear handoff protocols. Use structured file formats for inter-agent communication (`plans/handoffs/<stage>.md`, `.specs/reports/`). Batch results where possible.

### Failure: Divergence

Agents pursuing different goals without central coordination can drift from intended objectives.

**Mitigation**: define clear objective boundaries for each agent. Implement convergence checks that verify progress toward shared goals. Use iteration limits on agent execution (max debate rounds = 3, max fix loops = 3).

### Failure: Error propagation

Errors in one agent's output propagate to downstream agents that consume that output.

**Mitigation**: validate agent outputs before passing to consumers (e.g., judge after every implementation). Implement retry logic with feedback. Design for graceful degradation when components fail (failure isolation in `dispatch-parallel`).

## Applying patterns in Shannon

### Command as supervisor

A `/shannon:*` command:
1. Analyzes the task and creates a plan.
2. Dispatches subagents via Task tool for specialized work.
3. Collects results (via return values or shared files).
4. Synthesizes final output.

### Subagents as specialists

Shannon defines specialized agents:
- Each agent focuses on one area of expertise (judge, critic, oracle, team-builder, team-qa, team-validator, meta-judge).
- Agents receive focused context relevant to their specialty.
- Agents return structured outputs (YAML headers) that coordinators can aggregate.

### Files as shared memory

Shannon uses the file system for inter-agent coordination:
- State files: `.shannon/state/*.json`, `.shannon/state/rubric-<run-id>.yaml`.
- Handoff documents: `plans/handoffs/<stage>.md`.
- Evidence: `e2e-evidence/<run-id>/`.
- Reports: `.specs/reports/`.

### Example: Code review multi-agent

```
Supervisor Command: /shannon:dispatch-parallel "code review"
├── Subagent: security-reviewer (security specialist)
├── Subagent: performance-reviewer (performance specialist)
├── Subagent: style-reviewer (style/conventions specialist)
├── Per-target Judge: scores each review against meta-judge YAML
└── Aggregation: combine findings, deduplicate, prioritize
```

Each subagent receives only the code to review and their specialty focus. The supervisor aggregates all findings into a unified review.

## Guidelines

1. Design for context isolation as the primary benefit of multi-agent systems.
2. Choose architecture pattern based on coordination needs, not organizational metaphor.
3. Use file-based communication as the default for Shannon multi-agent patterns.
4. Implement explicit handoff protocols with clear state passing.
5. Use critique/debate patterns for consensus rather than simple agreement.
6. Monitor for supervisor bottlenecks and implement checkpointing via files.
7. Validate outputs before passing between agents.
8. Set iteration limits to prevent infinite loops (Shannon defaults: 3 debate rounds, 3 fix loops, 3 retries).
9. Test failure scenarios explicitly.
10. Start simple — add multi-agent complexity only when single-agent approaches fail.

## Memory and state management

For tasks spanning multiple sessions or requiring persistent state, use file-based memory:

### Working memory
The context window itself. Provides immediate access but vanishes when sessions end. Keep only active information; summarize completed work.

### Session memory
Files created during a session that track progress:
- Task lists (what's done, what remains).
- Intermediate results.
- Decision logs.

### Long-term memory
Persistent files that survive across sessions:
- `CLAUDE.md` for project-level context.
- `.shannon/state/` for run-state and rubrics.
- Structured knowledge bases in markdown or JSON.

### Memory patterns for multi-agent
- **Handoff files**: agent A writes state, agent B reads and continues.
- **Result aggregation**: multiple agents write to separate files, supervisor reads all.
- **Progress tracking**: shared task list updated by all agents.
- **Knowledge accumulation**: agents append findings to shared knowledge files.

Choose the simplest memory mechanism that meets your needs. File-based memory is transparent, debuggable, and requires no infrastructure.

## Related Skills

- `dispatch-parallel` — supervisor pattern, parallel + competitive + sequential modes.
- `team-coordinator` — hierarchical staged pipeline.
- `consensus-engine` — file-mediated debate with 5-state synthesis.
- `judge` — quorum gate with debate escalation.
- `judge-with-debate` — peer-to-peer debate engine.
- `tree-of-thoughts` — hierarchical exploration / pruning / expansion / evaluation.
- `subagent-driven-development` — sequential supervisor with code-review-between-tasks.
- `do-and-judge` — supervisor with meta-judge + judge per task.
- `do-competitively` — competitive supervisor with adaptive strategy.
- `launch-sub-agent` — single-shot supervisor with CoT + self-critique.
- `agents/meta-judge.md` — rubric generation primitive (shared across all consensus skills).

## Cross-references

- `core/SUBAGENT_PATTERNS.md` — extended worked examples and pattern catalogs.


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `subagent-driven-development`

# Subagent-Driven Development

Create and execute a plan by dispatching a fresh subagent per task or issue, with code and output review after each (or batch of) tasks.

**Core principle**: fresh subagent per task + code-review between (or after) tasks = high quality, fast iteration.

Executing plans through subagents:
- Same session (no context switch for the lead).
- Fresh subagent per task (no context pollution for the worker).
- Code review after each or batch of tasks (catch issues early).
- Faster iteration than human-in-the-loop between every task.

This skill is Shannon's discipline for **sequential execution with quality gates between tasks**. It complements `dispatch-parallel` (sequential mode) by adding the explicit code-review-between-tasks step that catches integration/style/regression issues a per-task judge would miss.

## Supported execution types

### Sequential execution

When tasks are related and need to be executed in order, investigating or modifying them sequentially is the best approach.

Dispatch one agent per task or issue. Let it work sequentially. Review the output and code after each task.

**When to use**:
- Tasks are tightly coupled.
- Tasks should be executed in order.
- Each task's output is needed by the next.

### Parallel execution

When you have multiple unrelated tasks (different files, different subsystems, different bugs), investigating or modifying them sequentially wastes time. Each task is independent and can happen in parallel.

Dispatch one agent per independent problem domain. Let them work concurrently. Overall review can be done after all tasks are completed.

**When to use**:
- Tasks are mostly independent.
- Overall review can be done after all tasks completed.

For parallel execution, this skill defers to `dispatch-parallel`. Use this skill primarily for **sequential mode with code-review-between-tasks** — which is the capability `dispatch-parallel` sequential mode lacks by itself.

## Sequential Execution Process

### Step 1: Load plan

Read plan file. Create TodoWrite with all tasks.

### Step 2: Execute task with subagent

For each task:

**Dispatch fresh implementation subagent**:

```
Task tool:
  description: "Implement Task N: <task name>"
  prompt: |
    You are implementing Task N from {plan-file}.

    Read that task carefully. Your job is to:
    1. Implement exactly what the task specifies.
    2. Write tests (following TDD if task says to).
    3. Verify implementation works.
    4. Commit your work (NOTE: in Shannon, commits queued for apply.sh — do not git commit unless explicitly allowed by environment).
    5. Report back.

    Work from: {directory}
    File ownership: {glob} — write ONLY within this scope.
    IRON RULE inject delivered via PreToolUse:Task hook — obey it.

    Report:
    - What you implemented
    - What you tested
    - Test results
    - Files changed
    - Any issues
```

Subagent reports back with summary of work.

### Step 3: Review subagent's work

**Dispatch code-reviewer subagent**:

```
Task tool:
  description: "Code review of Task N"
  prompt: |
    You are a code reviewer evaluating the implementation of Task N.

    WHAT_WAS_IMPLEMENTED: {from implementation subagent's report}
    PLAN_OR_REQUIREMENTS: Task N from {plan-file}
    BASE_REF: {commit / state before task}
    HEAD_REF: {commit / state after task}
    DESCRIPTION: {task summary}

    Evaluate:
    - Strengths
    - Issues (Critical / Important / Minor)
    - Assessment (Ready / Needs fixes / Reject)

    Cite file:line for every finding.
```

Code reviewer returns:
- **Strengths**.
- **Issues** classified Critical / Important / Minor.
- **Assessment**.

### Step 4: Apply review feedback

**If issues found**:
- Fix Critical issues immediately.
- Fix Important issues before next task.
- Note Minor issues (defer or document).

**Dispatch fix subagent if needed**:

```
Task tool:
  description: "Fix issues from code review of Task N"
  prompt: |
    Fix issues from code review:
    {list issues with file:line citations}

    Make the minimal changes needed to address each issue. Do not refactor unrelated code.
    Report back what you changed.
```

### Step 5: Mark complete, next task

- Mark task as completed in TodoWrite.
- Move to next task.
- Repeat steps 2-5.

### Step 6: Final review

After all tasks complete, dispatch final code-reviewer:
- Reviews entire implementation across all tasks.
- Checks all plan requirements met.
- Validates overall architecture.

### Step 7: Complete development

After final review passes:
- Announce: "I'm using the finishing-a-development-branch protocol to complete this work."
- Run any required validation (e.g., functional-validation, qa-loop).
- Present completion options to the user.

### Example workflow

```
You: I'm using Subagent-Driven Development to execute this plan.

[Load plan, create TodoWrite]

Task 1: Hook installation script

[Dispatch implementation subagent]
Subagent: Implemented install-hook with tests, 5/5 passing

[Dispatch code-reviewer]
Reviewer: Strengths: Good test coverage. Issues: None. Ready.

[Mark Task 1 complete]

Task 2: Recovery modes

[Dispatch implementation subagent]
Subagent: Added verify/repair, 8/8 tests passing

[Dispatch code-reviewer]
Reviewer: Strengths: Solid. Issues (Important): Missing progress reporting

[Dispatch fix subagent]
Fix subagent: Added progress every 100 conversations

[Verify fix, mark Task 2 complete]

...

[After all tasks]
[Dispatch final code-reviewer]
Final reviewer: All requirements met, ready to merge

Done!
```

### Red flags

**Never**:
- Skip code review between tasks.
- Proceed with unfixed Critical issues.
- Dispatch multiple implementation subagents in parallel for sequential tasks (conflicts; use `dispatch-parallel` parallel mode for independent work).
- Implement without reading plan task.
- Have the lead implement directly to "save a round trip" — the whole point is fresh contexts.

**If subagent fails task**:
- Dispatch a fresh fix subagent with specific instructions.
- Don't try to fix manually (context pollution).

## Parallel execution process

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle**: batch execution with checkpoints for architect review.

**Announce at start**: "I'm using the executing-plans protocol to implement this plan."

### Step 1: Load and review plan

1. Read plan file.
2. Review critically — identify any questions or concerns about the plan.
3. If concerns: raise them with the user before starting.
4. If no concerns: create TodoWrite and proceed.

### Step 2: Execute batch

**Default: first 3 tasks** (or `--max-parallel`).

For each task:
1. Mark as `in_progress`.
2. Follow each step exactly (plan has bite-sized steps).
3. Run verifications as specified.
4. Mark as `completed`.

Use `dispatch-parallel` for the actual parallel spawn — this skill defers to that for the SINGLE-MESSAGE multi-Task pattern.

### Step 3: Report

When batch complete:
- Show what was implemented.
- Show verification output.
- Say: "Ready for feedback."

### Step 4: Continue

Based on feedback:
- Apply changes if needed.
- Execute next batch.
- Repeat until complete.

### Step 5: Complete development

After all tasks complete and verified:
- Final code review.
- Announce: "I'm using the finishing-a-development-branch protocol to complete this work."
- Follow that protocol to verify tests, present options, execute choice.

### When to stop and ask for help

**STOP executing immediately when**:
- Hit a blocker mid-batch (missing dependency, test fails, instruction unclear).
- Plan has critical gaps preventing starting.
- You don't understand an instruction.
- Verification fails repeatedly.

**Ask for clarification rather than guessing.**

### When to revisit earlier steps

Return to Review (Step 1) when:
- Partner updates the plan based on your feedback.
- Fundamental approach needs rethinking.

**Don't force through blockers** — stop and ask.

## Parallel investigation process

Special case of parallel execution, when you have multiple unrelated failures that can be investigated without shared state or dependencies.

### 1. Identify independent domains

Group failures by what's broken:
- File A tests: tool approval flow
- File B tests: batch completion behavior
- File C tests: abort functionality

Each domain is independent — fixing tool approval doesn't affect abort tests.

### 2. Create focused agent tasks

Each agent gets:
- **Specific scope**: one test file or subsystem.
- **Clear goal**: make these tests pass.
- **Constraints**: don't change other code.
- **Expected output**: summary of what you found and fixed.

### 3. Dispatch in parallel (SINGLE assistant response)

```
Task("Fix agent-tool-abort.test.ts failures")
Task("Fix batch-completion-behavior.test.ts failures")
Task("Fix tool-approval-race-conditions.test.ts failures")
```

All three run concurrently because they're in the SAME assistant response.

### 4. Review and integrate

When agents return:
- Read each summary.
- Verify fixes don't conflict.
- Run full test suite.
- Integrate all changes.

### Agent prompt structure

Good agent prompts are:
1. **Focused** — one clear problem domain.
2. **Self-contained** — all context needed to understand the problem.
3. **Specific about output** — what should the agent return?

```markdown
Fix the 3 failing tests in src/agents/agent-tool-abort.test.ts:

1. "should abort tool with partial output capture" — expects 'interrupted at' in message
2. "should handle mixed completed and aborted tools" — fast tool aborted instead of completed
3. "should properly track pendingToolCount" — expects 3 results but gets 0

These are timing/race condition issues. Your task:
1. Read the test file and understand what each test verifies.
2. Identify root cause — timing issues or actual bugs?
3. Fix by:
   - Replacing arbitrary timeouts with event-based waiting.
   - Fixing bugs in abort implementation if found.
   - Adjusting test expectations if testing changed behavior.

Do NOT just increase timeouts — find the real issue.

Return: Summary of what you found and what you fixed.
```

### Common mistakes

- **Too broad**: "Fix all the tests" — agent gets lost.
- **Specific**: "Fix agent-tool-abort.test.ts" — focused scope.
- **No context**: "Fix the race condition" — agent doesn't know where.
- **Context**: paste the error messages and test names.
- **No constraints**: agent might refactor everything.
- **Constraints**: "Do NOT change production code" or "Fix tests only".
- **Vague output**: "Fix it" — you don't know what changed.
- **Specific**: "Return summary of root cause and changes".

### When NOT to use parallel mode

- **Related failures** — fixing one might fix others; investigate together first.
- **Need full context** — understanding requires seeing entire system.
- **Exploratory debugging** — you don't know what's broken yet.
- **Shared state** — agents would interfere.

### Verification

After agents return:
1. Review each summary — understand what changed.
2. Check for conflicts — did agents edit same code?
3. Run full suite — verify all fixes work together.
4. Spot check — agents can make systematic errors.

## Iron rules

- Fresh subagent per task. No context reuse across tasks.
- Code review BETWEEN tasks (or batches), not just at the end.
- Lead does not implement directly; lead orchestrates.
- File-ownership glob in every spawn prompt.
- IRON RULE inject delivered via PreToolUse:Task hook.
- Critical issues fixed before next task.
- TodoWrite tracks task state.

## Related Skills

- `dispatch-parallel` — used for parallel mode dispatch (single-message multi-Task pattern).
- `do-and-judge` — single-task variant with meta-judge + judge + retry.
- `do-in-steps` — sequential with per-step meta-judge (lighter than this skill's full code-review).
- `judge` — used as the per-task evaluator (alternative to code-reviewer agent).
- `critique` — adversarial alternative to code-reviewer.
- `multi-agent-patterns` — design rationale for supervisor-with-quality-gates pattern.

## Cross-references

- `agents/code-reviewer.md` — the code-reviewer agent invoked between tasks.
- `agents/critic.md` — adversarial alternative.
- `hooks/subagent-governance.*` — IRON RULE inject.
