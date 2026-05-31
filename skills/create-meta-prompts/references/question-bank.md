# Question Bank

This reference is loaded by `create-meta-prompts` step 0 (intake gate). It supplies the contextual questions to ask the user during intake, routed by Purpose.

The intake gate gathers 2–4 questions max. Picking the RIGHT 2–4 from this bank is the skill of intake.

## Universal first question (only if Purpose unclear)

**header**: Purpose
**question**: What is the purpose of this prompt?
**options**:
- Do — Execute a task, produce an artifact
- Plan — Create an approach, roadmap, or strategy
- Research — Gather information or understand something
- Refine — Improve an existing research or plan output

Skip this if Purpose was inferable from the user's invocation.

## Universal second question (always)

**header**: Topic
**question**: What topic / feature is this for? (used for file naming, kebab-case)
**options**: Free text via "Other"

Enforce kebab-case in the answer; convert spaces/underscores.

## Do-specific questions

### Artifact type

**header**: Artifact
**question**: What kind of artifact will this produce?
**options**:
- Code change (TypeScript, Swift, Python, Go, etc.)
- Configuration / infrastructure
- Database migration / schema
- Documentation
- Other (free text)

### Scope

**header**: Scope
**question**: How big is the task?
**options**:
- Atomic (single file, single concept)
- Multi-file (3–5 files, single feature)
- Multi-area (cross-cutting; touches frontend + backend + DB)

If Multi-area, suggest splitting into a chain (Research → Plan → multiple Dos) before the user can pick Multi-area for a single prompt.

### Approach preference

**header**: Approach
**question**: Any preferred approach or library?
**options**:
- I'll let you pick based on research
- I have a specific approach (free text)
- I want a comparison before deciding (route to Research instead)

## Plan-specific questions

### Plan purpose

**header**: Plan type
**question**: What kind of plan?
**options**:
- Implementation plan (tasks → code)
- Roadmap (phases → milestones)
- Migration plan (current → target)
- Decision document (compare options, choose one)

### Constraints

**header**: Constraints
**question**: Any hard constraints?
**options**:
- Time-boxed (ship by date)
- Resource-bound (one developer / specific team)
- Tech-constrained (must use X)
- None / open

### Output format

**header**: Format
**question**: Where should the plan land?
**options**:
- .planning/PLAN.md (Shannon convention)
- .prompts/.../plan.md (Claude-to-Claude convention)
- README section
- ADR (architecture decision record)

## Research-specific questions

### Depth

**header**: Depth
**question**: How deep?
**options**:
- Quick scan (1–2 sources, surface answer)
- Standard (3–6 sources, comparison)
- Deep dive (10+ sources, comprehensive, with conflicts resolved)

### Sources

**header**: Sources
**question**: Which sources?
**options**:
- Codebase only
- Codebase + official docs
- Codebase + official docs + community / blogs
- Web search broad

### Output format

**header**: Format
**question**: Output shape?
**options**:
- Findings list (bullets with citations)
- Comparison table (for options vs options decisions)
- Narrative report (for architecture / design questions)
- Decision recommendation (for "which to pick" research)

## Refine-specific questions

### Target

**header**: Target
**question**: Which existing output to refine?
**options**: Scan `.prompts/*/` and list candidates; user picks via "Other"

### Feedback

**header**: What to change
**question**: What's missing or weak in the current version?
**options**: Free text via "Other"

This is the most important intake answer for Refine — without it, the prompt has no direction.

### Preservation

**header**: What to preserve
**question**: Anything in v1 that MUST stay intact?
**options**:
- Confidence rating
- Specific findings (free text to specify)
- Overall structure
- All decisions
- "Free to change anything"

## Question selection algorithm

Given Purpose, ask:

```
if Purpose unclear:
  ask Universal-first
ask Universal-second (Topic)

if Purpose == Do:
  ask Artifact type
  ask Scope
  (optionally) ask Approach if user hasn't said

if Purpose == Plan:
  ask Plan type
  ask Constraints
  (optionally) ask Output format

if Purpose == Research:
  ask Depth
  ask Sources
  (optionally) ask Output format

if Purpose == Refine:
  ask Target
  ask Feedback (REQUIRED)
  (optionally) ask Preservation
```

Stop at 2–4 questions. Over-questioning kills momentum.

## Decision gate (after questions)

After the questions, present the decision gate:

**header**: Ready
**question**: Ready to create the prompt?
**options**:
- Proceed — Create the prompt with current context
- Ask more questions — I have more details to clarify
- Let me add context — I want to provide additional information

Loop until Proceed.

## When to skip the intake gate

If the invocation arrives with sufficient context (e.g., from another skill or a follow-up turn in a clear thread), skip the gate. Use inferred values and proceed to generation. Surface the inference: "Inferred Purpose=Do, Topic=password-reset; proceeding."

Always allow the user to interrupt: "Wait, I want to clarify…"

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Asking the same question with different wording | User loses trust in the gate | Pick one canonical phrasing per question |
| 5+ questions before proceeding | Intake fatigue; user disengages | Cap at 4, ask follow-ups in conversation if needed |
| Asking questions whose answers don't change the output | Waste of intake budget | Every question must change the generated prompt in a non-trivial way |
| Requiring AskUserQuestion for trivial confirms | Use inline question for yes/no | Reserve AskUserQuestion for genuine multi-option choices |
