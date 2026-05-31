# Section Splitting

> The decision of where to draw boundaries in a long artifact. Sister reference to section-index.md: that file is the structure; this file is the discipline for choosing the structure.

## The atomicity rule

Each section should be:
1. Independently meaningful (a reader can understand it without reading the rest)
2. Independently reviewable (a reviewer can give meaningful feedback on it alone)
3. Independently editable (changes to it don't ripple across the whole artifact)

If a "section" depends heavily on another section for meaning, the split is wrong — merge them.

## Splitting patterns

### Pattern: Audience-driven split

Sections serving different audiences should be separate.

```
S-Exec: Executive summary (for executives)
S-Tech: Technical detail (for engineers)
S-Ops:  Operational impact (for ops team)
```

Each audience reads their section in isolation; the section is calibrated to them.

### Pattern: Time-driven split

When the artifact covers multiple time horizons:

```
S-Now:   What changes immediately
S-Soon:  Next 1-2 months
S-Later: 6-12 months out
```

Each section has different concreteness — Now is specific, Later is directional.

### Pattern: Decision-vs-execution split

```
S-Decision: What we're deciding + why
S-How:      How we'll execute
S-Risks:    What could go wrong
```

Lets stakeholders engage at the right altitude — execs read S-Decision; engineers read S-How.

### Pattern: Top-down hierarchical split

For very large artifacts, split into top-level sections, each with sub-sections:

```
S-01 Overview
  S-01.1 Background
  S-01.2 Goals
S-02 Approach
  S-02.1 Architecture
  S-02.2 Data flow
  S-02.3 Failure modes
...
```

Each top-level section is itself reviewable in isolation; sub-sections inherit context.

### Pattern: Sequential narrative split

When the artifact tells a story (incident report, RCA):

```
S-01 Timeline
S-02 Impact
S-03 Root cause
S-04 Resolution
S-05 Action items
```

The order is meaningful; reading out-of-order loses the story.

## Anti-patterns in splitting

### Anti-pattern: Splitting by topic when the topic threads through

If a topic appears in 5 sections, you have 5 mini-discussions of the same thing. Consolidate into one section that owns the topic; reference it from others.

### Anti-pattern: Splitting for length alone

A 10-page section isn't automatically bad. A 3-page section with no internal cohesion isn't automatically good. Split for MEANING, not for length.

### Anti-pattern: Splitting then needing forward references

If S-02 references S-04, the order is wrong — either S-02 should be after S-04, or the dependency should be eliminated.

### Anti-pattern: Section size imbalance

If S-01 is 100 words and S-02 is 4000 words, the split is doing more work than it should. Consider whether S-02 should be split further or S-01 should be merged elsewhere.

### Anti-pattern: Section-as-buffer

Adding a "Discussion" section to hold leftover material that didn't fit elsewhere is a sign the split is wrong. The "leftover" content usually belongs to one of the existing sections.

## When NOT to split

Some artifacts are stronger as one continuous piece:

- Short artifacts (<2000 words)
- Single-audience artifacts (no audience-driven split needed)
- Narrative-style artifacts where flow matters more than modularity
- Quick decision memos

Don't impose structure where it doesn't help. Section indices are a tool, not a requirement.

## How splits change during drafting

Initial split → draft → realize the split is wrong → re-split → draft → done.

The first split is a hypothesis. Drafting tests it. If during drafting:
- A section keeps growing → consider splitting it
- Two sections keep referencing each other → consider merging them
- A section's content feels disconnected → reconsider its place in the index

Re-splitting mid-draft is normal. It's cheaper than shipping a poorly-split artifact.

## Cross-references

- `skills/gepetto/` — parent skill
- `references/section-index.md` — the structure being designed
- `references/interview-protocol.md` — informs what to split by
- `references/external-review.md` — review treatment per section
- `skills/plan-author/` — related discipline for plan-decomposition
