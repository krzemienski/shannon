# Phase Transitions

> The contract for moving between phases of the spec-driven dev workflow: research → requirements → design → tasks → implement. Each transition has a gate.

## The five-phase pipeline

```
research → requirements → design → tasks → implement
   ↓             ↓           ↓        ↓         ↓
findings    requirements   design   tasks    code
.md         .md            .md      .md      ...
```

Each phase produces ONE artifact. The artifact is the input to the next phase. A phase doesn't end until its artifact is signed off.

## Transition gates

A transition gate is a check that runs at the boundary between phases. The downstream phase doesn't start until the gate passes.

### research → requirements gate

**Question:** Do we have enough information to write requirements?

**Pass criteria:**
- findings.md exists with sources cited
- ≥3 sources consulted for non-trivial questions
- Open questions explicitly listed (not silently elided)
- Confidence level stated (HIGH / MEDIUM / LOW per finding)

**Fail signs:**
- "I think X" without a source
- Confident assertions about questions the research didn't explicitly cover
- Findings.md is short despite the question being complex

**On fail:** loop back to research. Don't write requirements on shaky findings.

### requirements → design gate

**Question:** Are the requirements complete and unambiguous enough to design against?

**Pass criteria:**
- Every requirement is testable (you can describe what evidence proves it satisfied)
- No "should be intuitive" / "should work well" hand-waves
- In-scope and out-of-scope explicitly listed
- Acceptance criteria per requirement

**Fail signs:**
- "Must be fast" without a number
- "Must be secure" without a threat model
- "Must handle errors gracefully" without specifying which errors
- Requirements contradict each other and the conflict isn't resolved

**On fail:** loop back to requirements. Don't design against ambiguity.

### design → tasks gate

**Question:** Is the design concrete enough that someone can write a task list?

**Pass criteria:**
- Every component named (no "an abstraction layer")
- Every data flow mapped (where does state live, where do mutations happen)
- Every external dependency identified
- Trade-offs explicitly considered
- Risks listed with mitigations

**Fail signs:**
- Design that's "the existing pattern" without restating it
- Component boundaries fuzzy
- Missing data model
- Concurrency / lifecycle questions unanswered

**On fail:** loop back to design. Don't task-plan against vapor.

### tasks → implement gate

**Question:** Is each task atomic, ordered, and verifiable?

**Pass criteria:**
- Every task has a "done = ..." statement (testable, observable)
- Each task is independently shippable (or explicitly marked as requiring a predecessor)
- 2-3 tasks per plan-file (atomicity rule from plan-author)
- Verification step per task

**Fail signs:**
- "Implement the feature" as a single task
- 10+ tasks in a single plan-file
- "Done when it works" — not testable
- Order matters but isn't recorded

**On fail:** loop back to tasks. Don't implement against an under-specified plan.

### implement → done gate

**Question:** Is the work actually done — verified by real-system evidence?

**Pass criteria (Iron Rule):**
- All tasks marked done WITH evidence (transcript / screenshot / curl / file diff)
- All gates from upstream phases satisfied
- No skipped verification steps
- Summary written

**Fail signs:**
- "Tests pass" without surfaced output
- Mock/stub introduced during implementation
- Tasks marked done without evidence
- "Mostly done" claim

**On fail:** loop back to implement. Don't sign off on partial work.

## Skipping phases

Some workflows skip phases legitimately:

| Skip | When legit |
|------|------------|
| Skip research | Question is in-distribution; no unknowns |
| Skip requirements | Bug fix or trivial change; "fix the typo" needs no requirements doc |
| Skip design | Trivial implementation; e.g., adding a field to an existing struct |
| Skip tasks | Implementation is a single atomic step |

The transition gates above APPLY to each kept phase. Skipping doesn't mean skipping the gate — it means the upstream phase isn't needed.

## Looping between phases

Loops are expected. A design pass that surfaces missing requirements loops back to requirements. A tasks pass that finds the design is unworkable loops back to design.

The discipline:
1. Document the loop ("Returning to requirements because design discovered an unmet constraint X")
2. Don't loop silently
3. Cap the number of loops per transition (usually 2-3); if you exceed, escalate to the user

## Parallel work within a phase

A phase can have parallel work. Example: research has 3 sub-questions, each researched independently.

But the GATE is one — findings.md is the single artifact. Sub-research feeds into it; the gate fires on the combined findings.

## Roles per phase

In Shannon's terms (per `agents/`):
- research → researcher agent
- requirements → planner agent
- design → planner agent (or architect)
- tasks → planner agent
- implement → executor + validator agents

The spec-workflow skill orchestrates this; the agents do the per-phase work.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Skipping a gate to save time | Downstream phase builds on shaky base | Run the gate; pass or fail explicitly |
| Looping silently | Future-you doesn't know why a phase ran twice | Document the loop trigger |
| Treating tasks as design | Tasks should be derivable from design, not a substitute | Force the design to exist before tasks |
| Long requirements doc with no test criteria | "Requirements" become marketing copy | Every requirement is testable |
| Implementation gate skipped on tight timeline | Ships untested code | Implementation gate is non-negotiable |

## Cross-references

- `skills/spec-workflow/` — parent skill
- `skills/plan-author/` — task-plan generation
- `skills/interview-framework/` — pre-research intake
- `skills/gate-validation-discipline/` — Iron Rule for the implement gate
- `agents/planner.md`, `agents/researcher.md`, `agents/executor.md`, `agents/validator.md` — phase owners
