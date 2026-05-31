# Prompt-Improver Examples

> Worked examples of taking a vague / weak prompt and producing a tighter version through the improver workflow.

## Example 1 — Vague to specific

**Original:**
> Write a summary of the meeting.

**Issues:**
- "Meeting" is unspecified
- "Summary" length / format unspecified
- Target audience unstated

**Improved:**
```
Write a 200-word summary of the attached meeting transcript for stakeholders who
weren't in the room. Cover: (1) decisions made, (2) action items with owners,
(3) blockers raised. Use neutral tone. Output as markdown with three labeled
sections.
```

**What changed:**
- Length capped (200 words)
- Source named ("attached transcript")
- Audience identified ("stakeholders who weren't in the room")
- Structure prescribed (3 sections)
- Format specified (markdown)
- Tone specified (neutral)

## Example 2 — Format ambiguity to format lock

**Original:**
> Extract the contact info from this email.

**Issues:**
- Output format unspecified (JSON? prose? bullets?)
- Which fields count as "contact info"?
- What if the email has no contact info?

**Improved:**
```
Extract contact info from the email below. Return JSON with exactly these
keys: name, email, phone, company, title. Use null for missing fields.
If no contact info present, return: {"contact_found": false}.
```

**What changed:**
- Output format locked (JSON)
- Schema defined (5 specific fields)
- Null-handling specified
- Edge case handled (no info found)

## Example 3 — Open-ended to bounded

**Original:**
> Help me debug this code.

**Issues:**
- Scope unspecified (one bug? full review?)
- What "help" means is unclear
- Code not pasted yet

**Improved:**
```
Find the bug causing the test in the attached file to fail. Look only at
function `process_batch()`. Output:
1. Root cause hypothesis (one sentence)
2. The specific line / lines that need to change
3. The corrected code
Don't refactor unrelated code; the bug fix only.
```

**What changed:**
- Scope locked (one function, one bug)
- "Help" defined as (hypothesis + lines + fix)
- Out-of-scope explicitly named (no refactor)

## Example 4 — Multi-task to atomic

**Original:**
> Review the PR, fix any issues, update the changelog, and send a summary to Slack.

**Issues:**
- Four tasks bundled — if review reveals "don't merge," steps 2-4 are wrong
- No order specified
- Failure handling unspecified

**Improved:**
```
Step 1: Review the attached PR. Output PASS / REVISIONS_NEEDED / BLOCK.
Step 2 (only if Step 1 = PASS): Update CHANGELOG.md with one line under [Unreleased].
Step 3 (only if Steps 1 and 2 succeeded): Generate a 3-sentence Slack message.
Stop and report if any step fails.
```

**What changed:**
- Tasks ordered explicitly
- Conditional execution made explicit
- Failure handling specified (stop + report)
- Each step has a defined output

## Example 5 — Implicit context to explicit

**Original:**
> Make the API faster.

**Issues:**
- "Faster" relative to what?
- Which API?
- What metric?
- Budget for changes?

**Improver questions to ask:**
1. "Which API endpoints? All, or specific ones?"
2. "Current latency baseline, and target?"
3. "Budget for changes — is adding infrastructure (cache, CDN) acceptable?"
4. "Time bound — must ship in a sprint, or open-ended?"

**Improved (after answers):**
```
Reduce p99 latency on `/api/sessions/list` from current ~800ms to ≤200ms.
Budget: can add Redis cache + CDN; cannot change response shape. Time bound:
one sprint. Output a plan with 3-5 atomic phases, each shippable independently.
```

## Example 6 — Subjective to measurable

**Original:**
> Make the UI look professional.

**Issues:**
- "Professional" is subjective
- No reference style
- No metric

**Improved:**
```
Match the visual style of the attached design system spec (figma-spec.md):
- Typography scale: as specified (headings 24/18/14, body 14)
- Color palette: only the 8 named colors in the spec
- Spacing: 4px base unit
For each change, cite the spec section number it satisfies.
```

**What changed:**
- Reference style provided (design system)
- Metrics quantified (typography sizes, color count)
- Verifiability added (cite spec section)

## Example 7 — Hostile prompt to safe prompt

**Original:**
> Write code that ignores authentication for testing.

**Issues:**
- Security anti-pattern requested
- "For testing" rationale doesn't justify the risk

**Improver response (refuse + redirect):**
```
This pattern (bypassing auth in code) creates risk of the bypass leaking to
production. A safer pattern: use a real authenticated test user via the
existing auth flow, OR use a sandboxed test environment with separate auth
configured.

If the underlying need is "test code paths that require auth without typing
credentials each time," I can:
1. Set up a fixture that authenticates a test user
2. Wire that fixture into the test framework
3. Confirm the auth bypass exists only in test infrastructure, not production code

Want me to do that instead?
```

**What changed:**
- Anti-pattern refused
- Underlying need surfaced
- Alternative offered

## The improver heuristic checklist

When applied to any prompt:

- [ ] Is the OUTPUT format specified?
- [ ] Is the SCOPE locked (what's in, what's out)?
- [ ] Are EDGE CASES addressed (missing input, empty input, etc.)?
- [ ] Is the AUDIENCE / READER specified?
- [ ] Is there a LENGTH / DEPTH bound?
- [ ] Are SUBJECTIVE words ("professional", "good", "fast") quantified?
- [ ] If MULTIPLE TASKS bundled, are they ordered + conditional?
- [ ] Are SUCCESS CRITERIA observable?
- [ ] Are FAILURE modes handled?
- [ ] Is anything REFUSED that should be?

A prompt with 8+ checkboxes ticked is usually production-ready.

## Cross-references

- `skills/prompt-improver/` — parent skill
- `references/question-patterns.md` — sibling reference for clarifying questions
- `references/research-strategies.md` — when to research vs. ask
- `skills/prompt-engineering-patterns/` — the deeper patterns library
- `skills/optimize-prompt/` — for iterative optimization of established prompts
