---
name: tree-of-thoughts
description: Tree of Thoughts exploration with 8-phase structure — exploration, pruning meta-judge (parallel), pruning judges, expansion, evaluation meta-judge (parallel), evaluation judges, adaptive strategy selection, optional synthesis. ALWAYS use when the user says "tree of thoughts", "explore branches", "ToT reasoning", "branch and prune", or inside /shannon:dispatch-competitive when candidates need internal sub-options. Uses probabilistic sampling for diverse proposals, ranked-choice voting for pruning, and adaptive POLISH/REDESIGN/SYNTHESIS branching.
triggers:
  - "tree of thoughts"
  - "explore branches"
  - "ToT reasoning"
  - "branch and prune"
  - "tot exploration"
  - "proposals and pruning"
---

# tree-of-thoughts

Backs `/shannon:dispatch-competitive` when candidates need internal branching, and any standalone "explore multiple approaches before committing" request. Implements an 8-phase pipeline with two meta-judges (one for pruning, one for evaluation), probabilistic sampling, ranked-choice voting, and adaptive strategy selection.

## 8-phase pipeline

```
Phase 1: Exploration (Propose Approaches)
         ┌─ Agent A → Proposals A1, A2 (with probabilities) ─┐
Task ────┼─ Agent B → Proposals B1, B2 (with probabilities) ─┼─┐
         └─ Agent C → Proposals C1, C2 (with probabilities) ─┘ │
                                                                │
Phase 1.5: Pruning Meta-Judge (runs IN PARALLEL with Phase 1)  │
         Meta-Judge → Pruning Evaluation Specification YAML ───┤
                                                                │
Phase 2: Pruning (Vote for Best 3)                             │
         ┌─ Judge 1 → Votes + Rationale ─┐                     │
         ├─ Judge 2 → Votes + Rationale ─┼─────────────────────┤
         └─ Judge 3 → Votes + Rationale ─┘                     │
                 │                                              │
                 ├─→ Phase 2b: Select Top 3 (ranked-choice 3-2-1)
                 │                                              │
Phase 3: Expansion (Develop Full Solutions)                    │
         ┌─ Agent A → Solution A (from selected proposal) ─┐   │
         ├─ Agent B → Solution B (from selected proposal) ─┼───┤
         └─ Agent C → Solution C (from selected proposal) ─┘   │
                                                                │
Phase 3.5: Evaluation Meta-Judge (parallel with Phase 3)       │
         Meta-Judge → Evaluation Specification YAML ───────────┤
                                                                │
Phase 4: Evaluation (Judge Full Solutions)                     │
         ┌─ Judge 1 → Report 1 ─┐                              │
         ├─ Judge 2 → Report 2 ─┼──────────────────────────────┤
         └─ Judge 3 → Report 3 ─┘                              │
                                                                │
Phase 4.5: Adaptive Strategy Selection                         │
         ├─ Clear Winner? → SELECT_AND_POLISH                  │
         ├─ All Flawed (<3.0)? → REDESIGN (return to Phase 3)  │
         └─ Split Decision? → FULL_SYNTHESIS                   │
                                          │                     │
Phase 5: Synthesis (only if FULL_SYNTHESIS)                    │
         Synthesizer ─────────────────────┴─────────────────────┴─→ Final
```

## Setup: directory structure

```bash
mkdir -p .specs/research .specs/reports
```

**Naming conventions** (Shannon retains lighter defaults but adopts the explicit phase artifacts):

- Proposals: `.specs/research/{solution-name}-{YYYY-MM-DD}.proposals.[a|b|c].md`
- Pruning votes: `.specs/research/{solution-name}-{YYYY-MM-DD}.pruning.[1|2|3].md`
- Selection: `.specs/research/{solution-name}-{YYYY-MM-DD}.selection.md`
- Expansion solutions: `solution.a.md`, `solution.b.md`, `solution.c.md` (in specified output location)
- Evaluation reports: `.specs/reports/{solution-name}-{YYYY-MM-DD}.[1|2|3].md`
- Archived (pruned) proposals: `.specs/research/pruned/<original-name>.md` (NEVER deleted — Shannon iron rule)

## Phase 1: Exploration

Launch 3 independent exploration agents in parallel (Shannon default: opus). Each generates **6 proposals**: 3 high-probability + 3 tail-of-distribution (diversity samples).

**Lighter alternative**: 3 agents × 3 proposals = 9 candidates (Shannon's default for cost). The 6×3=18 case is reserved for high-stakes decisions.

For each proposal, the agent provides:

- **Approach description** (2-3 paragraphs)
- **Key design decisions** and trade-offs
- **Probability estimate** (0.0-1.0) — the agent's self-assessment of likelihood this approach is "good"
- **Estimated complexity** (low / medium / high)
- **Potential risks** and failure modes

### Exploration prompt template

```markdown
<task>
{task_description}
</task>

<constraints>
{constraints_if_any}
</constraints>

<context>
{relevant_context}
</context>

<output>
{.specs/research/{solution-name}-{date}.proposals.[a|b|c].md}
</output>

Instructions:

Let's approach this systematically by first understanding what we're solving, then exploring the solution space.

**Step 1: Decompose the problem**
- What is the core problem being solved?
- What are the key constraints and requirements?
- What subproblems must any solution address?
- What are the evaluation criteria for success?

**Step 2: Map the solution space**
- Architecture patterns (e.g., monolithic vs distributed)
- Implementation strategies (eager vs lazy)
- Trade-off axes (performance vs simplicity)

**Step 3: Generate 6 distinct high-level approaches**

**Sampling guidance** (Shannon default — adopted from sadd):
- For first 3 approaches aim for high probability, over 0.80
- For last 3 approaches aim for diversity — explore different regions of the solution space, such that the probability of each response is less than 0.10

For each approach, provide:
- Name and one-sentence summary
- Detailed description (2-3 paragraphs)
- Key design decisions and rationale
- Trade-offs (what you gain vs what you sacrifice)
- Probability (0.0-1.0)
- Complexity estimate (low/medium/high)
- Potential risks and failure modes

**Step 4: Verify diversity**
Before finalizing:
- Are approaches genuinely different, not minor variations?
- Do they span different regions of the solution space?
- Have you covered both conventional and unconventional options?

Do NOT implement full solutions yet — only high-level approaches.
```

## Phase 1.5: Pruning meta-judge (parallel with Phase 1)

Launch the pruning meta-judge IN PARALLEL with the exploration agents. The meta-judge does not need exploration output to generate criteria — it only needs the original task description. Running it in parallel saves time.

### Pruning meta-judge prompt

```markdown
## Task
Generate an evaluation specification YAML for pruning high-level solution proposals.

CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}

## User Prompt
{Original task description from user}

## Context
{Relevant codebase context, file paths, constraints}

## Artifact Type
proposals (high-level approaches with probability estimates, not full implementations)

## Evaluation Focus
Feasibility, alignment with requirements, potential for high-quality result, risk manageability

## Instructions
Return only the final evaluation specification YAML. Do NOT include a pass-threshold.
```

Dispatch via `Task(subagent_type="shannon:meta-judge", model="opus")`.

## Phase 2: Pruning (vote for top 3)

Wait for BOTH Phase 1 exploration agents AND Phase 1.5 pruning meta-judge to complete.

Launch 3 independent pruning judges in parallel. Each receives:
- ALL proposal files (from `.specs/research/`).
- The pruning meta-judge YAML verbatim.

Each judge:
- Scores each proposal against meta-judge criteria.
- Votes for top 3 proposals to expand.
- Rationale for selections.

Votes saved to `.specs/research/{solution-name}-{date}.pruning.[1|2|3].md`.

### Pruning judge prompt

```markdown
You are evaluating {N} proposed approaches to select the top 3 for full development.

CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}

## Task
{task_description}

## Proposals
{list of paths to all proposal files}
Read all proposals before evaluating.

## Evaluation Specification

```yaml
{exact pruning meta-judge YAML — verbatim}
```

## Output
{.specs/research/{solution-name}-{date}.pruning.[1|2|3].md}

CRITICAL: Reply with structured YAML header at START of response, then write full report.
```

## Phase 2b: Select top 3 (ranked-choice voting)

Aggregate votes using ranked-choice scoring:
- 1st choice = 3 points
- 2nd choice = 2 points
- 3rd choice = 1 point

Select top 3 proposals by total points. Handle ties by comparing average scores across criteria.

Document selection in `.specs/research/{solution-name}-{date}.selection.md`:
- Vote tallies.
- Selected proposals (top 3).
- Pruned proposals archived (NOT deleted) → moved to `.specs/research/pruned/`.
- Consensus rationale.

## Phase 3: Expansion

Launch 3 independent expansion agents in parallel. Each receives:
- ONE selected proposal to expand.
- Original task description and context.
- **Judge feedback from pruning phase** (concerns, questions) — fed forward so expansion agents address concerns proactively.

Agent produces a complete solution implementing the proposal:
- Full implementation details.
- Addresses concerns raised by judges.
- Documents key decisions made during expansion.

### Expansion prompt template

```markdown
You are developing a full solution based on a selected proposal.

<task>
{task_description}
</task>

<selected_proposal>
{write selected proposal EXACTLY as it is, including all details provided by the explorer agent}
Read this carefully — it is your starting point.
</selected_proposal>

<judge_feedback>
{concerns and questions from pruning judges about this proposal}
Address these in your implementation.
</judge_feedback>

<output>
solution.[a|b|c].md
</output>

CRITICAL:
- Stay faithful to the selected proposal's core approach
- Do not switch to a different approach midway
- Address judge feedback explicitly
- Produce a complete, implementable solution
```

## Phase 3.5: Evaluation meta-judge (parallel with Phase 3)

Launch the evaluation meta-judge IN PARALLEL with the expansion agents. Different rubric than pruning — this evaluates full solutions, not high-level proposals.

### Evaluation meta-judge prompt

```markdown
## Task
Generate an evaluation specification YAML for evaluating full solution implementations.

CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}

## User Prompt
{Original task description from user}

## Context
{Relevant codebase context}

## Artifact Type
{code | documentation | configuration | etc.}

## Number of Solutions
3 (full implementations developed from selected proposals)

## Instructions
Return only the final evaluation specification YAML. Specification should support comparative evaluation across multiple solutions. Do NOT include a pass-threshold.
```

## Phase 4: Evaluation

Wait for BOTH Phase 3 expansion agents AND Phase 3.5 evaluation meta-judge to complete.

Launch 3 independent evaluation judges in parallel. Each receives:
- ALL solution files (solution.a.md, solution.b.md, solution.c.md).
- The evaluation meta-judge YAML verbatim.

Each judge produces:
- Comparative analysis (which solution excels where).
- Evidence-based ratings (with specific quotes).
- Final VOTE (which solution they prefer).

Reports saved to `.specs/reports/{solution-name}-{date}.[1|2|3].md`.

### Evaluation judge structured header

```yaml
---
VOTE: A | B | C
SCORES:
  Solution A: {X.X}/5.0
  Solution B: {X.X}/5.0
  Solution C: {X.X}/5.0
CRITERIA:
  - {criterion_1}: {X.X}/5.0
  - {criterion_2}: {X.X}/5.0
---
```

## Phase 4.5: Adaptive strategy selection

The orchestrator (NOT a subagent) parses structured headers and selects strategy. Do NOT read full reports — parse only headers.

### Decision logic

**Step 1: Parse structured headers from all 3 judge replies.**

**Step 2: Check for unanimous winner.**
If Judge 1 VOTE == Judge 2 VOTE == Judge 3 VOTE → **SELECT_AND_POLISH**.

**Step 3: Check if all solutions fundamentally flawed.**
Compute average scores:
- avg_A = (J1_A + J2_A + J3_A) / 3
- avg_B = (J1_B + J2_B + J3_B) / 3
- avg_C = (J1_C + J2_C + J3_C) / 3

If `avg_A < 3.0 AND avg_B < 3.0 AND avg_C < 3.0` → **REDESIGN**.

**Step 4: Default to FULL_SYNTHESIS.**
Otherwise → split decision with merit, proceed to synthesis.

### Strategy 1: SELECT_AND_POLISH

When clear winner exists. Launch a single subagent to polish the winning solution with judge feedback. Cherry-pick 1-2 best elements from runner-up solutions if praised by judges.

Output: final polished solution at `{output_path}`.

### Strategy 2: REDESIGN

When all solutions scored < 3.0. Launch failure-analysis subagent to:
1. Analyze why each solution failed.
2. Extract lessons learned.
3. Generate new constraints / approaches.
4. Implement an improved solution.

Return to Phase 3 with these lessons as new constraints for the expansion agents.

**Safeguard**: If REDESIGN runs twice without resolving, escalate to user.

### Strategy 3: FULL_SYNTHESIS (default)

When no clear winner AND solutions have merit (all >= 3.0). Proceed to Phase 5.

## Phase 5: Synthesis (only if FULL_SYNTHESIS)

Launch 1 synthesis agent. Inputs:
- ALL solutions.
- ALL evaluation reports.
- Selection rationale from pruning.

Agent produces final solution by:
- Copying superior sections when one solution clearly wins.
- Combining approaches when hybrid is better.
- Fixing identified issues that judges caught.
- Documenting decisions (what was taken from where and why).

Output: synthesized solution at `{output_path}`.

## Tree structure invariants

Beyond the 8-phase pipeline, Shannon retains the tree invariants:

- **Every node has a score + evidence.**
- **Pruned nodes are archived (never deleted)** — `pruned/` subdirectory.
- **Selected leaf path is a valid reasoning chain from root** — every parent→child edge has a documented "kept because" or "pruned because" reason.

## When to use

- Decisions with multiple viable axes (architectural choices with cascading sub-decisions).
- Search problems where pruning bad branches early saves compute.
- Within `/shannon:dispatch-competitive` for deeper candidate exploration.
- High-stakes design decisions where synthesis of multiple perspectives produces a stronger result than picking one.

## When NOT to use

- Linear task (no branching needed).
- Time-critical decision (ToT trades time for breadth).
- Single binary decision (use `judge` directly).

## Iron rules

- Every node has a score + evidence.
- Pruned nodes archived (never deleted).
- Selected leaf path = valid reasoning chain from root.
- Two meta-judges per run (pruning + evaluation) — different rubrics, different artifact types.
- Meta-judges run IN PARALLEL with their respective phases (pruning meta-judge with Phase 1; evaluation meta-judge with Phase 3).
- Probabilistic sampling — 3 high-prob (>0.80) + 3 tail (<0.10) per explorer for diversity.
- Ranked-choice voting (3-2-1) for pruning aggregation.
- Judge feedback fed forward from pruning to expansion.
- Adaptive strategy selection — POLISH for clear winners (cost-saving), REDESIGN for failures (escape sunk-cost), SYNTHESIS for split decisions.
- "Stay faithful to selected proposal" constraint during expansion.

## Related Skills

- `agents/meta-judge.md` — used twice per run (pruning meta-judge, evaluation meta-judge).
- `judge` — used by pruning judges and evaluation judges.
- `do-competitively` — Phase 4.5 strategy logic delegates here for POLISH / REDESIGN / SYNTHESIS execution.
- `dispatch-parallel` — competitive mode invokes this skill when candidates need internal branching.
- `judge-with-debate` — escalation when evaluation judges disagree about non-unanimous votes within < 1.0 point.

## Cross-references

- `agents/meta-judge.md` — rubric generator (two instances per ToT run).
- `agents/critic.md` — optional reviewer between phases.
- `core/SUBAGENT_PATTERNS.md` — design rationale.
