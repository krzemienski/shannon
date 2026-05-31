# Research Strategies for Deepening

This reference is loaded by Phase 3 of `deepen-prompt-plan`. It expands the source-priority ladder, parallel-execution patterns, conflict-resolution rules, and quality bars for research that closes confidence gaps.

The point of research in a deepening pass is NOT to write a research report. It is to find the smallest piece of evidence that closes a specific gap. Stop the moment the gap is closed.

## Source priority ladder

When multiple sources could close a gap, prefer earlier entries on this ladder:

1. **Codebase analysis** — grep, find, read the code that already exists. This is the strongest evidence because it reflects the actual system, not a generic answer.
2. **Existing in-repo documentation** — README.md, CLAUDE.md, ARCHITECTURE.md, ADRs, comments, and docstrings. These reflect this project's decisions, not a generic template.
3. **Origin documents the plan derives from** — the brief, spec, roadmap, or feature request that birthed this plan. Often answers "why this way" better than any external source.
4. **Official upstream documentation** — framework docs (Next.js docs, Apple Developer docs), library guides (React docs), API references (OpenAI API ref). Use the `library-docs-fetch` skill or context7 MCP to fetch.
5. **Vendor security / compliance docs** — OWASP, NIST, framework hardening guides for security-sensitive sections.
6. **High-quality industry sources** — engineering blogs from primary maintainers, RFCs, IETF drafts.
7. **Web search for general best practices** — last resort. Reliable for "what's the standard pattern" but not for "what does Library X do in version Y."

When a lower-priority source contradicts a higher-priority one, the higher-priority one wins. When two same-priority sources contradict, document the conflict and pick one with rationale.

## Research execution patterns

### Pattern A — Codebase grep first

Most gaps in implementation plans close from codebase evidence alone.

```bash
# Find the existing pattern for whatever the gap is about
grep -rn 'authMiddleware' src/ | head -20
grep -rn 'TokenStore' src/ | head -20
find src -name '*.swift' -newer LAST_FEATURE_BRANCH | head -20
```

If the codebase already has a convention for the area being planned, the plan should follow it. Cite the file and line.

### Pattern B — Documentation fetch

For framework- or library-specific questions, fetch the current upstream doc.

```bash
# Via library-docs-fetch skill
# Returns the official answer + URL for citation
```

NEVER rely on training data for version-specific questions. Always fetch current docs.

### Pattern C — Origin re-read

For "why did we decide X" gaps, re-read the brief or spec. Many decisions are already justified there; the plan just didn't carry the rationale forward.

### Pattern D — Parallel investigation

When the deepening pass selects multiple weak sections, run their research in parallel — different gaps, different sources, no dependency between them. Issue searches/reads in a single message.

```
Bad (serial):
  grep auth -> wait -> read docs -> wait -> check spec -> wait

Good (parallel):
  In one message:
    - grep -rn 'auth' src/
    - library-docs-fetch --library next-auth
    - read .planning/SPEC.md "Authentication" section
  Synthesize the three results together
```

## Quality bar for evidence

Not every result is good evidence. Apply these tests before citing:

- **Specificity** — "OWASP recommends short-lived tokens" is weaker than "OWASP recommends 15-minute access tokens with refresh rotation [link]". Cite the specific recommendation.
- **Currency** — Is the source current for the library version in use? React 18 advice doesn't apply to React 16; Swift 5.9 advice doesn't apply to Swift 5.5. Check version.
- **Authority** — Who wrote this? A maintainer post on the official blog > a random Stack Overflow answer.
- **Repo-grounding** — Does the source's advice match the codebase's existing conventions? If it conflicts, prefer the repo's pattern unless there's a strong reason to deviate.
- **Reproducibility** — Can the reader follow the citation and verify the claim? "I read somewhere that…" fails. "Per Apple HIG Layout doc, line 4 [link]…" passes.

## Conflict resolution

When sources disagree:

1. Promote codebase evidence over any external source (the existing system IS the source of truth for "how this codebase does it").
2. Promote official docs over blog posts and forum answers.
3. Promote primary-maintainer statements over secondary writeups.
4. If still tied, document both positions and recommend the one that better fits the project's constraints (security, performance, simplicity).

Never paper over a conflict by picking one side without acknowledgment. Surface the conflict in the deepened document so the next reader knows what was uncertain.

## Research presentation

After Phase 3, present a compact summary BEFORE rewriting. The user must see what evidence was found and how it will be used.

```xml
<research_summary>
  <finding section="Key Decisions" source="OWASP Session Management Cheat Sheet (2024-01)">
    JWT access tokens should be short-lived (15-30 min) with refresh-token rotation.
    Impact: Adds rationale + source to decision D1; rejects the alternative of long-lived JWTs.
  </finding>
  <finding section="Risks" source="codebase: src/middleware/logger.ts:23">
    Logger middleware already redacts the `authorization` header.
    Impact: Risk R3 (token leakage in logs) mitigation can cite existing safeguard.
  </finding>
  <finding section="Tasks" source="codebase: src/auth/AuthManager.swift:1-80">
    Existing AuthProvider protocol pattern. New flows should conform.
    Impact: Task T2 file list becomes precise; task description references the protocol.
  </finding>
</research_summary>
```

Keep entries to 1-3 lines. The reader should be able to scan and approve quickly.

If no research was needed (gap closeable from the document itself), say so. Skip Phase 3.

## When to stop researching

Stop when:

- The gap has a citation that closes it
- The next source would only restate what the previous one said
- The remaining ambiguity is genuine product / business / strategy uncertainty — not a research gap; mark as Open Question and move on

Do NOT keep researching to inflate the deepening pass. A deepening session that produced 0–2 findings for 5 weak sections is normal; for some gaps, the existing material plus light editing is enough.

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| "Survey of all approaches" before picking one | Plans deepen by closing specific gaps, not by widening the option space | Pick the source most likely to close the gap; cite once |
| Citing a tutorial blog post for security | Tutorial blogs are written for getting started, not for hardening | Cite OWASP / NIST / vendor security doc for security claims |
| Skipping codebase grep because "I know how the project works" | Memory drifts; the project changed last week | Always grep before citing existing patterns |
| Restating training-data assumptions as research | Training data is undated; libraries move fast | Always fetch current docs for version-specific claims |
| Producing a long research report instead of integrating findings | The deepening is the deliverable; the research is the means | Compress findings into 1-3 line impacts and move on |

## Citation discipline

Every claim added to the deepened document during Phase 5 must trace to an evidence source captured in the research summary. Format:

- Codebase: `src/path/to/file.ext:line-range`
- In-repo doc: `path/to/doc.md` (anchor if specific section)
- Origin doc: `BRIEF.md` (section)
- External doc: short title + URL (version pinned where applicable)

A deepened section without traceable citations is just an opinion. Iron Rule applies to research too: real source, not what feels right.
