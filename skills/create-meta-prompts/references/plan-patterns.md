# Plan Patterns

This reference is loaded by `create-meta-prompts` step 1 when the user's selected purpose is **Plan**. It defines the structural template for planning prompts — prompts that produce an executable plan (PLAN.md) that downstream Do prompts will consume.

## When to use Plan patterns

The Plan purpose covers: plan, roadmap, approach, strategy, decide, phases, sequence, design. The output is a plan document, not an implementation.

## Required structure

A Plan prompt must produce a plan.md with this internal structure:

```markdown
# {Topic} Plan

## Confidence
<confidence>high|medium|low</confidence>
Rationale for the confidence level.

## Objective
One sentence: what the plan delivers.

## Context
What we know (from research / specs / codebase).

## Key decisions
For each decision: statement, rationale, alternatives considered, source.

## Open questions
What remains uncertain. Each with owner and resolution trigger.

## Assumptions
What we are assuming to be true. Flag any high-risk assumption.

## Tasks (or Phases)
Numbered breakdown. Each task: type, files, action, verify, done.

## Validation strategy
How each task / phase is validated. Iron Rule.

## Risks
Each risk: severity, likelihood, mitigation.

## Dependencies
External deps, prior prompts, services that must be in place.

## Success criteria
Measurable conditions that mean "the plan worked end-to-end."
```

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Plan without confidence rating | Downstream cannot know whether to trust the plan | Always assign confidence + rationale |
| Decisions stated without alternatives | Reader cannot tell whether the decision was thought through | Cite at least one rejected alternative |
| Open questions hidden as "TBD" in body | Easy to miss; downstream consumer can't act | Lift every TBD into the Open Questions section with owner |
| Tasks coarse enough to span days | Implementer drowns; partial-failure invisible | Atomic tasks: 1 file or 1 concept each, with verification |
| Risks listed without mitigation | "We named the risk" is not the same as "we addressed it" | Every listed risk has at least one concrete mitigation |
| Success criteria phrased as feature list | Cannot tell when the plan is done | Make every criterion testable via real-system observation |

## Atomic task discipline

A task should be small enough that:
- It can be implemented in one focused session
- It has a single failure mode
- It produces exactly one verifiable outcome
- It commits as one logical changeset

If a task seems too small, group sub-tasks under a single parent. If a task crosses three files and two concepts, split it.

## Plan vs design

A plan describes WHAT and IN WHICH ORDER. It does NOT include implementation code. Pseudo-code or architecture sketches are allowed; concrete syntax is forbidden.

If the user needs full design (data models, API schemas, error codes), the Plan prompt should generate a separate `design.md` AND a `plan.md`. The design is reference material; the plan is execution sequence.

## Template — minimal Plan prompt

```markdown
# Password reset feature — Plan prompt

## Objective
Produce a plan.md that breaks the password-reset feature into 3–5 atomic tasks
with per-task validation gates and an overall risk register.

## Context
@.planning/SPEC.md
@.prompts/002-auth-research/auth-research.md
!grep -n 'AuthProvider' src/

## Required output structure
Output to: .prompts/003-pwreset-plan/pwreset-plan.md

The plan must contain:
- <confidence>...</confidence>
- Objective (one sentence)
- Key decisions (at least 3, with alternatives)
- Open questions (at least 2)
- Assumptions (at least 2, flagged for risk)
- 3–5 atomic tasks
- Validation gate per task (real-system, Iron Rule)
- Risk register (at least 3 risks, each with mitigation)
- Success criteria (measurable)

## Constraints
- Iron Rule: no tests, no mocks, no in-memory DBs
- Tasks must each fit in one focused session (no "Build the auth system" mega-tasks)
- Cite OWASP for any security claim
- Cite codebase paths for any "existing pattern" claim

## SUMMARY.md
Path: .prompts/003-pwreset-plan/SUMMARY.md

Must include:
- One-liner: what the plan delivers
- Number of tasks + estimated effort signal
- Open questions count
- Highest risk + mitigation
- Next step: which Do prompt consumes this plan
```

## SUMMARY.md schema for Plan prompts

```markdown
# Password reset — Plan summary

**One-liner:** A 4-task plan for password reset with 3 BLOCKING gates and OWASP-backed token lifetimes.

**Confidence:** high
**Tasks:** 4
**Open questions:** 2 (rate-limit threshold, email provider)
**Highest risk:** Token replay if backend clock skewed (MITIGATION: include iat + exp; reject tokens > 15min)

## Decisions made
- D1: JWT access tokens with 15-min expiry (OWASP)
- D2: Refresh in HttpOnly cookie
- D3: SendGrid for transactional email

## Open questions
- Q1: Should reset links be single-use or N-use within window? (owner: PM)
- Q2: Rate limit by IP or by email? (owner: security)

## Blockers
None.

## Next step
Run `.prompts/004-pwreset-do/004-pwreset-do.md` once Q1 and Q2 are answered.
```

## Plan-to-Do handoff

The Do prompt consuming this plan MUST be able to:
- Read the plan's tasks and translate each into Do-prompt tasks
- Inherit the validation gates verbatim
- Surface any of the plan's open questions as gates ("STOP unless Q1 resolved")

Keep the plan structured enough that this handoff is mechanical, not interpretive.
