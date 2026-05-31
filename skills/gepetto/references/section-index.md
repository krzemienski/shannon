# Section Index

> Gepetto's pattern for breaking a large artifact into addressable sections. Each section gets its own goal, audience, and review treatment. The index is the artifact's table-of-contents-as-structure.

## Why section the artifact

A 50-page document reviewed as one unit produces unfocused feedback. The same document broken into 12 sections, each reviewed against its own criteria, produces actionable feedback.

The section index is the deliberate division of the artifact for:
- Per-section review (different reviewers per section if appropriate)
- Per-section research (different sources per section)
- Parallel work (independent sections can be drafted in parallel)
- Incremental delivery (ship sections as they're ready)

## When to section

Section the artifact when:

- The artifact will exceed ~2000 words / ~10 pages
- The artifact serves multiple audiences (each section targets one)
- The artifact has structurally distinct parts (intro / body / appendices)
- Different parts of the artifact will need different review depths

Don't section trivially. A 500-word memo doesn't need a section index. Sectioning has overhead; pay it when the artifact is large enough to benefit.

## Section index structure

```yaml
artifact: {topic}
target_word_count: {N}
target_audience: {primary reader}

sections:
  - id: S-01
    title: "Executive Summary"
    word_target: 150-300
    audience: executives + skim-readers
    purpose: "Communicate decision + recommendation in 30 seconds"
    review_treatment: "Sharp; cut every word that doesn't add"
    
  - id: S-02
    title: "Context + Problem Statement"
    word_target: 400-600
    audience: cross-functional collaborators
    purpose: "Bring readers up to speed on why this work exists"
    review_treatment: "Clarity-focused; assume reader has no prior context"
    
  - id: S-03
    title: "Proposed Approach"
    word_target: 800-1200
    audience: technical reviewers
    purpose: "Lay out the recommended technical approach"
    review_treatment: "Rigor-focused; cite specs / docs; address objections"
    
  - id: S-04
    title: "Alternatives Considered"
    word_target: 400-600
    audience: technical reviewers
    purpose: "Show the trade-off space; defend the recommendation"
    review_treatment: "Balanced; don't strawman alternatives"
    
  ...
```

The index drives the work plan: each section is a deliverable.

## Section ownership

For multi-author artifacts:

```
S-01 (Executive Summary) — owner: senior author (writes last, after others done)
S-02 (Context) — owner: author with most context
S-03 (Approach) — owner: technical lead
S-04 (Alternatives) — owner: technical lead (with input from team)
S-05 (Risks) — owner: senior author (objective view)
...
```

For solo authors writing with gepetto's help: ownership is gepetto's review pass + your final edit, per section.

## Section status tracking

Track per-section progress:

```yaml
sections:
  S-01: status=draft        owner=you      reviewer=none-yet
  S-02: status=reviewed     owner=you      reviewer=external-LLM-1
  S-03: status=approved     owner=you      reviewer=external-LLM-1+2
  S-04: status=needs-rewrite owner=you     reviewer=external-LLM-1
  S-05: status=not-started  owner=you      reviewer=tbd
```

The artifact ships when ALL sections are `approved`.

## Section dependencies

Some sections need others as input:

```
S-01 (Executive Summary) depends on S-03 (Approach) and S-05 (Risks)
S-04 (Alternatives) depends on S-03 (Approach) for the comparison
```

Plan section work in dependency order. S-01 is usually written LAST even though it appears first.

## Section-level review treatment

Different sections need different review depth:

| Section type | Review depth |
|--------------|--------------|
| Executive summary | Sharp + brief |
| Context | Clarity-focused |
| Approach | Rigor / specs / citations |
| Alternatives | Balanced (don't strawman) |
| Risks | Adversarial (think failure modes) |
| Appendices | Completeness |

The section index records the intended review treatment so reviewers calibrate appropriately.

## Cross-references

- `skills/gepetto/` — parent skill
- `references/section-splitting.md` — how to decide where to split
- `references/external-review.md` — how reviewers use the section index
- `references/interview-protocol.md` — what informs section design
- `skills/plan-author/` — adjacent skill for hierarchical planning
