# Research Strategies

> When prompt-improver should research instead of (or before) asking the user.

## The improver's third option

Most prompt-improver responses fall into:
1. Tighten the prompt and proceed
2. Ask clarifying questions

There's a third: research first, then tighten / ask with better context.

This file is about when research is the right move.

## When to research first

Research first when:

- The user is asking for something whose CURRENT BEST PRACTICE isn't in your training (e.g., "what's the recommended way to do X in Framework Y 2025+")
- The user named a specific library / tool / API you don't know in detail
- The user's framing implies they already know the domain, and asking basic questions would signal incompetence
- The improver itself doesn't know what good output looks like for this kind of task

When NOT to research first:

- The user's request is in your competent zone
- The user has already shared the relevant context (file attachments, spec)
- Research would just confirm what you already know (waste of latency)
- The cost of being slightly wrong on assumptions is low

## Research before asking — the protocol

```
1. Identify what you don't know
2. Decide: can ASKING get this faster than RESEARCHING?
3. If research is faster / cheaper: do it, then either tighten or ask with better priors
4. If asking is faster: ask
```

The decision usually hinges on:

| Factor | Favors research | Favors asking |
|--------|----------------|---------------|
| Information availability | Public, well-documented | User's private context |
| Specificity of need | General domain knowledge | User's preferences |
| Time cost of research | Quick lookup | Long deep-dive |
| User availability | User offline / async | User present / sync |

## Research sources to consider

### Source 1: Documentation (most common)

For library / framework / API questions, official docs first.

- `skills/perplexity/` for web search
- WebFetch on docs URLs
- `agent-toolkit/context7` MCP for library docs

Read the section relevant to the user's question. Cite what you find. Don't paraphrase if quoting is clearer.

### Source 2: Codebase analysis

For "how do we do X here" questions, the codebase is authoritative.

- `skills/codebase-analysis/` — structured codebase exploration
- `Grep` + `Glob` for specific patterns
- `Read` on key files

Cite specific files / line numbers in the improver response.

### Source 3: External authority

For "what's the consensus on X" questions:
- RFCs, specs, working group output (for standards questions)
- StackOverflow accepted answers (for common pitfalls)
- Recognized expert blogs (for design-decision questions)
- Anti-patterns lists (for "what to avoid" questions)

Don't quote opinion pieces as authority unless the user is asking for opinions.

### Source 4: User's prior work

The user's earlier prompts / artifacts in this conversation often contain the constraint set you need.

```
- Earlier in the conversation, user said "we use Postgres"
- Earlier in the conversation, user attached a spec
- Earlier in the conversation, user mentioned a deadline
```

Re-read before asking. Asking for something the user already said is a tell that you weren't reading.

## When research changes the prompt

Sometimes research reveals that the user's prompt is asking for the wrong thing:

```
User: "Add an index on the email column to make queries faster."

Research reveals:
- Table is 1000 rows (index won't help much)
- Email is already covered by the composite index on (user_id, email)
- The actual slow query is on a DIFFERENT column

Improver response:
"Before adding the index, I checked the schema and query patterns:
- Table has 1000 rows; index lift would be negligible
- Email is already in the (user_id, email) composite
- The slow query I see uses LIKE on the `display_name` column

If you want to make queries faster, the actual leverage points are:
1. Add an index on display_name (real lift)
2. ... or fix the LIKE pattern (different fix)
3. ... or skip — at 1k rows, this isn't a perf problem

Which is the goal?"
```

This response is MORE useful than "OK, adding the index" because it surfaces the user's real need.

## Research as risk reduction

For high-stakes prompts (production systems, hard-to-reverse decisions, irreversible operations), research is risk reduction. Even if the prompt seems clear, verify:

- Does this match the current version of the framework? (sometimes deprecated patterns)
- Does this conflict with the user's existing conventions? (read the codebase)
- Has this been recently changed? (check changelog / git log)
- Are there known landmines? (check issue tracker for the lib/tool)

The 30 seconds of research saves hours of debugging when the obvious-looking prompt would have produced wrong-now code.

## Research caps

Don't research forever. Cap by:

- Time: 30 seconds to 5 minutes per question, not 30 minutes
- Sources: 1-3 sources is plenty; more = analysis paralysis
- Specificity: research the SPECIFIC question, not the whole domain

If research takes >5 min, either:
- Switch to asking (faster)
- Decompose the question and research the most uncertain part only
- Surface the uncertainty to the user instead of resolving it

## Combining research + question

The strongest improver response often combines both:

```
"I researched the docs for {{framework}} and found two recommended patterns
for {{task}}: Approach A (simpler) and Approach B (more flexible).

Approach A is right when {{conditions}}; B is right when {{other-conditions}}.

Which fits your case? Or, if you tell me {{specific-detail}}, I can pick."
```

This is faster than asking blind, AND more informed than assuming.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Asking what you could research in 30s | Wastes user attention | Research first; ask refined question |
| Researching what user already told you | Wastes time + signals you weren't listening | Re-read conversation first |
| Researching forever without producing output | Analysis paralysis | Cap at 5 min; surface uncertainty if needed |
| Citing one blog post as authority | Single-source bias | Cross-reference 2-3 sources |
| Skipping research on high-stakes prompts | Risk of confidently-wrong output | Research is risk reduction; spend the 30s |

## Cross-references

- `skills/prompt-improver/` — parent skill
- `references/examples.md`, `question-patterns.md` — sibling references
- `skills/library-docs-fetch/` — deeper research workflow
- `skills/perplexity/` — web search skill
- `skills/codebase-analysis/` — codebase-as-source-of-truth research
