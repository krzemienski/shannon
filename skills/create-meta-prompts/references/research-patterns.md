# Research Patterns

This reference is loaded by `create-meta-prompts` step 1 when the user's selected purpose is **Research**. It defines the structural template for research prompts — prompts that produce a research output another prompt will consume.

## When to use Research patterns

The Research purpose covers: research, understand, learn, gather, analyze, explore, investigate, compare. The output is a research document with structured findings, citations, and confidence flags.

## Required structure

A Research prompt must produce a research.md with this internal structure:

```markdown
# {Topic} Research

## Metadata
- <confidence>high|medium|low</confidence>
- <dependencies>[what downstream needs from this]</dependencies>
- <open_questions>[what remained unknown]</open_questions>
- <assumptions>[what was assumed]</assumptions>

## Scope
What was researched and what was explicitly out of scope.

## Sources consulted
Each source: title, URL, date accessed.

## Findings
Each finding has:
- Statement
- Evidence (citation)
- Confidence (verified vs assumed)
- Impact on downstream plan / implementation

## Conflicts and resolutions
When sources disagreed, what was chosen and why.

## Recommendations
Actionable conclusions, not just summary.
```

## Quality controls

Every research prompt must enforce:

1. **Verification checklist** — for each critical claim, verified against an official source.
2. **Quality report** — at the end, a table that distinguishes verified findings from assumptions.
3. **Source list with URLs** — fully traceable; no "I read somewhere…"
4. **Confidence levels per finding** — not just an overall confidence; each finding tagged.
5. **Streaming write** — the prompt writes findings as it discovers them, not in a final dump (avoids losing context if the run is interrupted).

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Findings without citations | Cannot be verified or trusted | Every claim has a source |
| Single confidence level for whole document | Hides which findings are weak | Per-finding confidence |
| Restating training data without source | Stale or wrong | Fetch current docs / use library-docs-fetch skill |
| Long-form prose instead of structured findings | Hard to consume in downstream prompts | Bullet findings with metadata |
| Open questions silently resolved as "best guess" | Downstream proceeds on wrong assumption | Surface open questions explicitly |

## Template — minimal Research prompt

```markdown
# Password reset — Research prompt

## Objective
Produce research.md covering: token lifetime best practices, library choice (jose vs jsonwebtoken vs node-jose), email provider tradeoffs, rate-limit patterns.

## Sources to consult (priority order)
1. Codebase: existing auth implementation (src/auth/, src/middleware/)
2. OWASP Session Management Cheat Sheet (2024)
3. RFC 7519 (JWT specification)
4. Library docs: jose, jsonwebtoken (current versions only)
5. Email provider docs: SendGrid, Postmark, Resend

## Quality controls
- Every claim cited
- Per-finding confidence (verified vs assumed)
- Compare libraries by: TypeScript support, weekly downloads, recent maintainer activity, known CVEs
- Compare email providers by: deliverability, pricing, ergonomics, sandbox support

## Verification checklist (before submitting)
- [ ] Every library claim has a docs URL OR a codebase observation
- [ ] OWASP claim cites the specific cheat sheet
- [ ] CVE data is current (checked within last 30 days)
- [ ] At least one finding flagged as low-confidence or assumption

## Output
Streaming write to: .prompts/002-pwreset-research/pwreset-research.md
SUMMARY.md at: .prompts/002-pwreset-research/SUMMARY.md

## SUMMARY.md must include
- One-liner: substantive (not "Research completed")
- Top 3 findings with citations
- Recommended path forward
- Open questions and their owners
- Blockers (e.g., "Need API key to verify SendGrid quota")
```

## SUMMARY.md schema for Research prompts

```markdown
# Password reset — Research summary

**One-liner:** JWT with jose (TypeScript-native) + Resend (best deliverability + Sandbox)
recommended for 15-min access tokens with refresh rotation.

**Confidence:** high
**Sources consulted:** 12 (OWASP, RFC 7519, library docs, codebase)
**Open questions:** 2

## Key findings
1. jose has better TS support than jsonwebtoken — verified at https://github.com/panva/jose
2. OWASP recommends 15-min access + refresh rotation — verified at OWASP Session Mgmt Cheat Sheet § 3.2
3. Resend pricing best for our volume tier — verified at https://resend.com/pricing

## Open questions
- Q1: PM stated "single-use links" but no compliance requirement found — confirm desired behavior
- Q2: Existing rate-limit middleware (src/middleware/rate-limit.ts) limits by IP only — extend for by-email?

## Blockers
None.

## Next step
Create plan prompt (.prompts/003-pwreset-plan/) referencing this research.
```

## Streaming write discipline

Research prompts can be long-running. To avoid losing work:

- Write each finding to disk AS SOON AS verified, not at the end
- Use append-mode if possible, with clear section markers
- After verifying a critical claim, save immediately
- Avoid the "do all research, then write everything" pattern — it loses everything on context overflow

The prompt should explicitly instruct: "Write each finding to research.md as soon as verified. Append, don't overwrite."

## Chain detection

Research prompts are typically the FIRST in a chain. They produce a document consumed by a Plan prompt. The Plan prompt consumed by a Do prompt.

When creating a new research prompt, scan `.prompts/` for sibling research files on related topics — reference them rather than duplicating.
