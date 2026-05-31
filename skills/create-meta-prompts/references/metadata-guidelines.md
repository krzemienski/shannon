# Metadata Guidelines

This reference is loaded by `create-meta-prompts` step 1 for Research and Plan prompts. It defines the schema and quality bar for the `<confidence>`, `<dependencies>`, `<open_questions>`, and `<assumptions>` metadata blocks that downstream Claude prompts consume.

## Why structured metadata

Claude-to-Claude pipelines work because the consumer can mechanically parse what to trust, what to act on, and what to escalate. Free-form prose doesn't survive parsing reliably. Structured metadata does.

## `<confidence>`

A single tag, one of: `high`, `medium`, `low`.

```xml
<confidence>high</confidence>
<confidence_rationale>
  All claims grounded in official docs or codebase. No assumptions beyond
  standard OWASP guidance. Pattern matches existing project conventions.
</confidence_rationale>
```

Calibration:

| Level | When | Downstream interpretation |
|---|---|---|
| high | All claims sourced; no unresolved unknowns; matches existing patterns | Proceed without further verification |
| medium | Some assumptions, but reasonable; minor unknowns flagged | Acceptable; consumer may probe a section |
| low | Significant unknowns or conflicting evidence | Consumer should NOT auto-proceed; route back for refinement |

Anti-pattern: always-medium. If everything is medium, the field is useless. Calibrate honestly.

## `<dependencies>`

A list of what the consumer needs in order to act on this output.

```xml
<dependencies>
  <upstream>
    <item>OWASP cheat sheet access (web)</item>
    <item>Codebase at HEAD or later</item>
  </upstream>
  <downstream>
    <item>SendGrid API key for production</item>
    <item>Database migration capability</item>
  </downstream>
</dependencies>
```

`upstream` is what was required to produce this output. `downstream` is what the consumer will need.

If a critical downstream dependency is missing or uncertain, also surface in `<open_questions>`.

## `<open_questions>`

Each question is structured:

```xml
<open_questions>
  <question id="Q1" owner="product" priority="blocking">
    <text>Should reset links be single-use or N-use within window?</text>
    <why_open>PM has not specified; compliance requirements unclear.</why_open>
    <resolution_trigger>PM confirms acceptable behavior in #product channel.</resolution_trigger>
  </question>
  <question id="Q2" owner="security" priority="non-blocking">
    <text>Rate limit by IP or by email?</text>
    <why_open>Existing middleware (src/middleware/rate-limit.ts) supports IP only; per-email requires extension.</why_open>
    <resolution_trigger>Security team approves IP-only or scopes extension work.</resolution_trigger>
  </question>
</open_questions>
```

Priority values:

| Priority | Meaning |
|---|---|
| blocking | Downstream cannot proceed without resolution |
| non-blocking | Downstream can proceed with a reasonable default; flag in plan |
| informational | Nice to know; doesn't change the path |

If `<open_questions>` is empty, write `<open_questions/>` explicitly — don't omit. Omission ambiguous (no questions vs. forgot to record).

## `<assumptions>`

Each assumption is structured:

```xml
<assumptions>
  <assumption id="A1" risk="low">
    <text>SendGrid sandbox emails are deliverability-representative.</text>
    <falsification>Production sends bounce at higher rate than sandbox.</falsification>
  </assumption>
  <assumption id="A2" risk="high">
    <text>Token rotation can happen synchronously in the response.</text>
    <falsification>Rotation needs to be backgrounded; affects user perception of latency.</falsification>
  </assumption>
</assumptions>
```

Risk values:

| Risk | Meaning |
|---|---|
| low | Assumption is widely held; falsification unlikely |
| medium | Assumption is reasonable but unverified |
| high | Assumption could materially affect the plan if wrong |

For high-risk assumptions, include a `<falsification>` element — what observation would prove the assumption wrong. This lets downstream check the assumption against reality.

## Combined block at top of artifact

For Research and Plan outputs, place all four metadata blocks at the top of the file inside a wrapper:

```xml
<metadata>
  <confidence>high</confidence>
  <confidence_rationale>...</confidence_rationale>

  <dependencies>...</dependencies>

  <open_questions>...</open_questions>

  <assumptions>...</assumptions>
</metadata>

# {Topic}

## Findings
...
```

Downstream parsers expect the `<metadata>` block first. Consistent placement is more important than location-flexibility.

## Per-finding metadata (Research only)

Beyond the document-level metadata, each finding in a Research output should carry its own micro-metadata:

```xml
<finding id="F1">
  <statement>jose has better TypeScript support than jsonwebtoken.</statement>
  <evidence>https://github.com/panva/jose (README, types section)</evidence>
  <confidence>high</confidence>
  <impact>Choose jose for new code.</impact>
</finding>
```

Per-finding confidence is critical because a Research document is often a mix of "verified facts" and "assumed-from-defaults". The consumer needs to know which findings to trust without re-verification.

## Validation of metadata before exit

Before declaring a Research / Plan output complete, the executor should self-check:

```
- [ ] <metadata> block present at top
- [ ] <confidence> is high/medium/low (not blank, not "TBD")
- [ ] <confidence_rationale> is one sentence (not "various reasons")
- [ ] <open_questions> present, even if empty (use <open_questions/>)
- [ ] Each <question> has id + owner + priority
- [ ] Each <assumption> has id + risk; high-risk ones have <falsification>
- [ ] Each <finding> (Research) has its own confidence + evidence
```

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Free-form "Confidence: pretty sure" | Not parseable; not calibrated | Use the three-level scale |
| Open questions written as TBDs in body prose | Easy to miss; not actionable | Lift into `<open_questions>` block |
| Assumptions hidden as "as we know…" | Reads confident; is actually uncertain | Surface as `<assumption>` with risk level |
| Document-level confidence with no per-finding nuance | Hides which parts are solid vs. weak | Always include per-finding confidence in Research |
| Missing metadata on Refine outputs | Refine outputs are also consumed downstream | Refine prompts must include the same metadata |
