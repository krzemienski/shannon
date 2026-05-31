# Research Protocol

> When gepetto researches before planning. Research is the third pillar (alongside interview + external-review) of producing well-grounded artifacts.

## When research is needed

Research informs gepetto's plan when:

- The topic involves a library / framework / API gepetto doesn't deeply know
- The "best practice" has likely changed recently
- The user references domain expertise gepetto needs to load
- There's a published standard / RFC that should guide the work
- Stakeholders expect citations to authoritative sources

Research is overkill when:
- The topic is in gepetto's competent zone
- The user's input + interview output is sufficient
- Cost / time budget doesn't allow it

## Research sources

### Source 1: Official documentation

For library / framework / API questions. Use `WebFetch` or `skills/perplexity/` to retrieve.

- Read the official docs for the SPECIFIC version the user mentioned
- Quote what you find; don't paraphrase
- Cite the URL + section in the eventual plan

### Source 2: Specifications / standards

For protocol / format questions, the spec is authoritative. RFCs, W3C specs, ISO standards.

- Cite the section number
- Quote the relevant clause
- Don't extrapolate beyond what the spec says

### Source 3: Recognized expert sources

For "what's the consensus" questions:
- Industry blogs of known authority (not just anyone with a blog)
- Conference talks from recognized experts
- Books considered canonical in the field

Avoid:
- Single-blog opinion as authority
- Stack Overflow answers without high vote counts
- AI-generated content (echo chamber risk)

### Source 4: Codebase (if relevant)

For "how do we do X here" questions, the codebase is authoritative.

- `skills/codebase-analysis/` for structured exploration
- `Grep` / `Glob` / `Read` for specific patterns
- Cite specific files / line ranges in the eventual plan

### Source 5: Prior work in the conversation / repo

The user's earlier prompts, attached files, project docs.

- Re-read before researching externally — sometimes the answer is already there
- Cite the file + section

## Research depth budget

Set a budget BEFORE starting. Typical budgets:

| Topic complexity | Research budget |
|------------------|-----------------|
| Trivial / well-known | 0-2 minutes |
| Moderate / library-specific | 5-15 minutes |
| Complex / cross-domain | 30-60 minutes |
| Research-thesis-level | Multi-hour, multi-session |

Cap and stop. Research is a means, not an end.

## Research output structure

Write findings to `.gepetto/research-<topic>.md`:

```markdown
# Research — {topic}

## Goal
{What question this research is answering}

## Sources consulted
1. {URL or file path} — {one-line description, last-modified date}
2. ...

## Key findings
- **Finding 1** (HIGH confidence): {claim}. Source: [1] section X.
- **Finding 2** (MEDIUM confidence): {claim}. Source: [2].
- **Finding 3** (LOW confidence): {claim}. Source: [3]. Note: only one source; treat as tentative.

## Implications for the plan
- {How finding 1 changes the plan}
- {How finding 2 changes the plan}

## Open questions
- {Questions research couldn't resolve}

## Recommended next step
- {Use this research to inform plan X, or run further research on Y}
```

The confidence tags + source citations make the research output trustable.

## Research vs. interview

Sometimes the question is "should I research this OR ask the user?"

| Favor research | Favor asking the user |
|----------------|-----------------------|
| Public / well-documented fact | User's private context |
| General domain question | User's specific preferences |
| Standards / specs | Project-specific conventions |
| Fast to look up | User available + responsive |
| Cost of being wrong is high | Cost of asking is high (executive time, async) |

Often the right move is research-then-ask: research the general landscape, then ask the user to pick within the constrained option space.

## Cross-references

- `skills/gepetto/` — parent skill
- `references/external-review.md` — what research feeds into
- `references/interview-protocol.md` — when to research vs. ask
- `references/section-index.md`, `section-splitting.md` — how research informs structure
- `skills/perplexity/`, `skills/library-docs-fetch/` — research workflows
- `skills/codebase-analysis/` — codebase-as-source-of-truth
