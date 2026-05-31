# Confidence Scoring Rubric

This reference is loaded by Phase 2 of `deepen-prompt-plan`. It expands the per-section gap-scoring checklist into a complete set of triggers, weights, and worked examples.

## How scoring works

For each section of the input document, count the number of trigger conditions that fire. Add a risk bonus and a critical-section bonus. The total is the gap score.

```
gap_score = trigger_count + risk_bonus + critical_section_bonus
```

Selection rules:
- gap_score ≥ 2 → candidate for deepening
- gap_score = 1 in a high-risk domain AND the section is materially important → also a candidate
- Select top 2–5 sections by score
- Light-pass mode: cap at 1–2 sections

## Trigger checklists

A trigger fires when the corresponding problem is present in the section.

### Triggers for "Overview" / "Objective" sections

1. Goal stated as activity not outcome ("build X" instead of "users can do Y")
2. No measurable success criterion
3. Audience or context absent
4. Reads as marketing copy ("seamless", "robust", "best-in-class")
5. Mentions deliverables without saying why they matter

### Triggers for "Context" / "Background" sections

1. No links to origin docs, related work, or codebase paths
2. Assumes facts the reader cannot verify
3. Cites no constraints (technical, business, regulatory, performance)
4. Outdated references (links to deprecated APIs, removed services)
5. Skips the "what already exists" inventory

### Triggers for "Requirements" / "Success Criteria" sections

1. Criterion uses subjective language ("works well", "feels fast", "looks clean")
2. No measurable threshold (p95, error rate, throughput, count)
3. Requirements list mixes must-have with nice-to-have without labels
4. No mention of negative requirements (what is explicitly out of scope)
5. Acceptance criteria phrased as feature list, not testable conditions

### Triggers for "Scope Boundaries" sections

1. Missing entirely
2. Only positive scope ("we will…") with no negative scope ("we will NOT…")
3. Scope drifts mid-document (later sections add unannounced scope)
4. No mention of cross-cutting concerns (security, observability, accessibility, i18n)
5. No upgrade / migration / deprecation plan if the change affects existing surface

### Triggers for "Research" / "Sources" sections

1. No citations at all
2. Citations are stale (3+ years old where current standards exist)
3. Cites blog posts where official docs exist
4. No conflict resolution when sources disagree
5. Research conclusions are restated as assumptions without flagging them

### Triggers for "Key Decisions" sections

1. Decisions stated without tradeoff analysis
2. Obvious alternatives not addressed
3. No "why not X" entries for plausible alternates
4. Decisions made by deferral ("we'll decide later")
5. No rationale tied to a constraint or principle from the document

### Triggers for "Open Questions" sections

1. Section missing — implies all questions are resolved (rarely true)
2. Questions phrased rhetorically rather than as actual unknowns
3. No owner assigned per question
4. No deadline or trigger condition for resolution
5. Resolved questions left in the list (should move to Decisions)

### Triggers for "Technical Design" / "Architecture" sections

1. No diagram (where one would clarify dataflow, state, or sequence)
2. Diagram lacks labels or directionality
3. No description of data shapes (response schemas, table columns)
4. No mention of failure modes or partial-failure handling
5. Existing system not described; only the new system

### Triggers for "Tasks" / "Implementation Units" sections

1. Tasks not actionable (no verb, no file path)
2. Tasks too coarse ("Build authentication") — implies sub-tasks but doesn't enumerate
3. No dependency ordering
4. No verification step per task
5. No rollback or revert path

### Triggers for "System-Wide Impact" sections

1. Section missing
2. Only direct callers considered; transitive ones ignored
3. No mention of caches, CDN, search indexes
4. No mention of monitoring, alerting, dashboards that consume the changed surface
5. No mention of documentation that references the changed surface

### Triggers for "Risks" sections

1. Risks listed without mitigation
2. Mitigations are aspirational ("we will monitor closely")
3. Security risks absent where they obviously apply
4. Performance regression risk absent for changes that touch hot paths
5. Cost or rate-limit risks absent for external-API changes

### Triggers for "Validation" / "Verification" sections

1. No validation gates present
2. PASS criteria vague ("works", "looks good")
3. No evidence-capture step
4. No re-validation loop on FAIL
5. Validation involves writing tests or mocks (Iron Rule violation)

### Triggers for "Operational Notes" sections

1. Section missing for changes that have ops implications
2. No deployment plan
3. No feature-flag plan for risky changes
4. No rollback steps
5. No monitoring additions described

### Triggers for "Role / Identity" sections (prompts)

1. Role stated but not specialized ("you are a helpful assistant")
2. Role conflicts with the task (asked to be both critic and author)
3. No mention of audience or output consumer
4. No mention of allowed tools or constraints
5. Voice / tone / formality unspecified where it matters

### Triggers for "Workflows / Phases" sections (prompts)

1. No phase ordering
2. Phases described without transitions between them
3. Skipping conditions absent (when can a phase be skipped?)
4. No failure handling per phase
5. Phases overlap in responsibility (two phases claim the same output)

### Triggers for "Decision Trees / Routing" sections (prompts)

1. Branches non-exhaustive (don't cover all observed inputs)
2. Branches overlap (multiple match the same input)
3. No default / fallback branch
4. Branches lack rationale (why this path for this signal)
5. Routes call skills or tools that don't exist

### Triggers for "Output Specifications" sections (prompts)

1. Format unspecified
2. Format specified but inconsistent across examples
3. No length budget or structural constraint
4. No schema for machine-consumed outputs
5. Examples missing for non-obvious formats

### Triggers for "Edge Cases" sections (prompts)

1. Section missing for any non-trivial prompt
2. Cases listed without expected behavior
3. Cases test the role's boundaries (jailbreaks) but not domain edges
4. No handling for "the input I cannot process"
5. Examples insufficient to disambiguate cases

## Risk bonus (+1)

Add +1 to any section that touches a high-risk topic AND is materially important to that risk:

- Authentication, authorization, session management
- Payments, billing, subscriptions, refunds
- Data migrations, backfills, schema changes
- External APIs (paid, rate-limited, or with side-effects)
- Privacy, PII, compliance (GDPR, HIPAA, SOC 2)
- Cross-platform / multi-surface behavior
- Autonomous-execution prompts (no human-in-loop)
- Production deployments, rollouts, feature flags

## Critical-section bonus (+1)

Add +1 to these section types in moderate-to-complex documents:

- Key Decisions
- Tasks / Implementation
- System-Wide Impact
- Risks
- Validation
- Workflows (for prompts)
- Edge Cases (for prompts)

## Worked example

Input: a 600-word PLAN.md for adding password reset to a Node.js + React app.

| Section | Triggers fired | Risk bonus | Critical bonus | Total | Deepen? |
|---|---|---|---|---|---|
| Overview | 0 | 0 | 0 | 0 | no |
| Context | 1 (no codebase paths) | 0 | 0 | 1 | no |
| Key Decisions | 2 (no tradeoff analysis; alternatives absent) | +1 (auth) | +1 (critical) | 4 | YES |
| Tasks | 2 (no verification per task; coarse) | +1 (auth) | +1 (critical) | 4 | YES |
| System Impact | 1 (no monitoring mention) | 0 | +1 (critical) | 2 | YES |
| Risks | 2 (no mitigation; missing rate-limit) | +1 (auth) | +1 (critical) | 4 | YES |
| Validation | 2 (no gates; vague PASS criteria) | +1 (auth) | +1 (critical) | 4 | YES |

Five sections cross threshold. The deepening pass selects all five if size budget allows, or top-3 (Key Decisions, Risks, Validation) for a lighter pass.

## Calibration notes

- A section that scored 0 is NOT proven good — it may simply not have a trigger checklist entry that catches its problem. Use judgment when the document feels weak in a section that scored 0.
- A high score does NOT guarantee value. If the section is genuinely outside the document's purpose (e.g., a research plan won't have meaningful "Validation"), drop it from the candidate list and document why.
- For light-pass deepening, prefer sections with the HIGHEST score, not the most triggers — risk bonus signals "actually risky" better than trigger count signals "structurally thin."

## Anti-patterns in scoring

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Counting every trigger as equal | Some triggers are catastrophic, others cosmetic | The risk bonus + critical bonus implicitly weight by importance |
| Scoring sections that don't apply | E.g., "Operational Notes" on a pure research doc | Drop inapplicable sections from the table |
| Hiding the score from the user | User can't course-correct what they can't see | Always present the score table before deepening |
| Auto-deepening top-N without showing why | User loses trust when the choice is opaque | Show the table, ask "adjust?" before proceeding |
