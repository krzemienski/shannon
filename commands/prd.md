---
name: prd
description: "Structured PRD authoring with interview. Output feeds /shannon:plan."
argument-hint: "<feature-description>"
---

# /shannon:prd

PRD authoring with structured interview. Output: a PRD.md that can feed `/shannon:plan`.

## Inputs

- Positional: feature description (refined through interview)

## Behavior

1. Invoke `Skill: plan-author` in PRD mode + `Skill: interview-framework`.
2. Interview via `AskUserQuestion`:
   - WHY does this matter? (problem statement, business value)
   - WHAT is in scope vs out of scope?
   - WHO is the user? (personas, jobs-to-be-done)
   - WHEN is success? (success metrics, observable behaviors)
   - WHERE does this fit? (system context, dependencies)
   - HOW will we ship? (rollout strategy, risk mitigation)
3. Synthesize PRD.md to `plans/<date>-<slug>/PRD.md`.
4. Explicit user approval gate at end.

## PRD structure

```markdown
# PRD: <feature name>

## Problem statement
## Goals + non-goals
## User personas + jobs-to-be-done
## Success metrics (measurable)
## Functional requirements
## Non-functional requirements (perf, security, accessibility)
## System context + dependencies
## Risks + mitigation
## Rollout strategy
## Open questions
```

## Skills + agents

- `Skill: plan-author` (PRD subskill)
- `Skill: interview-framework`
- `Skill: spec-workflow`
- `Skill: prompt-engineering-patterns` (interview prompts use the canonical pattern catalog)
- `Task: planner`

## When to use

- Pre-`/shannon:plan` when feature is large or stakeholder alignment needed.
- When success metrics aren't yet defined.

## When NOT to use

- Small refactor, bug fix, or routine feature — go straight to `/shannon:plan`.

## Examples

```
/shannon:prd "Real-time collab cursor with permission model"
/shannon:prd "Inbox unification across Gmail/Outlook"
```
