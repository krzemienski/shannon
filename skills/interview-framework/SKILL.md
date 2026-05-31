---
name: interview-framework
description: Pre-plan intake interview with intent-based depth scaling and 3-phase Understand/Propose/Confirm algorithm. ALWAYS use when the user says "interview me", "ask me questions", "intake", "clarify the request", "brainstorm with questions", or before /shannon:plan on a GREENFIELD request. Scales question count by intent (TRIVIAL 1-2, REFACTOR 3-5, MID_SIZED 3-7, GREENFIELD 5-10). 2-4 options max per question. Detects "done/proceed/skip" completion signals. Persists to .progress.md.
triggers:
  - "interview me"
  - "ask me questions"
  - "intake"
  - "clarify the request"
  - "brainstorm with questions"
---

# interview-framework

Adaptive brainstorming dialogue algorithm. Runs BEFORE `skills/plan-author/SKILL.md` for GREENFIELD intent. Each downstream phase (research, requirements, design, tasks) supplies its own exploration territory.

## Option Limit Rule

Each question must have 2-4 options (max 4). Keep the most relevant options, combine similar ones.

## Intent-Based Depth Scaling

Read `.progress.md` for intent classification. Scale dialogue depth accordingly:

| Intent | Questions |
|--------|-----------|
| TRIVIAL | 1-2 |
| REFACTOR | 3-5 |
| MID_SIZED | 3-7 |
| GREENFIELD | 5-10 |

## Completion Signal Detection

After each response, check for early completion signals: "done", "proceed", "skip", "enough", "that's all", "continue", "next".

If `askedCount >= minRequired` and signal detected, skip remaining questions and move to Propose Approaches.

## 3-Phase Overview

### Phase 1: UNDERSTAND (Adaptive Dialogue)

Read all available context (.progress.md, prior artifacts, goal text). Identify what is unknown vs already decided. Generate questions from context and exploration territory -- not from a fixed pool. Each question builds on prior answers. Never ask something .progress.md already answers.

See `references/algorithm.md` for full pseudocode.

### Phase 2: PROPOSE APPROACHES

Synthesize dialogue into 2-3 distinct approaches. Each includes: name, description, trade-offs. Lead with recommendation. Present via AskUserQuestion. Maximum 3 approaches (more causes decision fatigue). Trade-offs must be honest -- no straw-man alternatives.

See `references/algorithm.md` for full pseudocode.

### Phase 3: CONFIRM & STORE

Brief recap to user of key decisions and chosen approach. If user corrects something, update before storing. Store in .progress.md under Context Accumulator pattern.

See `references/algorithm.md` for full pseudocode.

## Adaptive Depth (Other Responses)

When user selects "Other": ask a context-specific follow-up (never generic "elaborate"). Reference what the user typed. Continue until clarity or 5 rounds. Do not increment askedCount for follow-ups.

See `references/examples.md` for example follow-up patterns.

## Context Accumulator Pattern

After each interview, update `.progress.md`: read existing content, append new section under "## Interview Responses" with descriptive keys reflecting what was discussed. Include the chosen approach.

See `references/examples.md` for storage format.

## References

- **`references/algorithm.md`** -- Full 3-phase pseudocode (UNDERSTAND, PROPOSE APPROACHES, CONFIRM & STORE)
- **`references/examples.md`** -- Example interview questions, "Other" response handling, context storage format

## Cross-references (Shannon v7)

- `skills/plan-author/SKILL.md` — primary consumer; invokes this skill as pre-step for GREENFIELD intent.
- `skills/prd-clarity/SKILL.md` — 100-point clarity rubric (pair this question loop with that scoring).
- `skills/prompt-improver/SKILL.md` — sibling for the case where the *vague-prompt* path is the issue rather than the *requirements* path.
- `skills/brainstorm/SKILL.md` — ideation-style sibling (when divergence matters more than depth).
- `skills/spec-workflow/SKILL.md` — orchestrator that calls this skill across the research → requirements → design → tasks pipeline.
