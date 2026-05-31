# Checkpoints

> Decision and verification points where a plan pauses for human input. Three types: `checkpoint:human-verify`, `checkpoint:decision`, `checkpoint:human-action`.

## Why checkpoints exist

A plan that runs to completion without ever asking the human assumes:
- The plan is correct in every detail
- Decisions encountered along the way have obvious right answers
- Edge cases were anticipated

That's rarely true. Checkpoints are the structured place to surface things that weren't true.

## The three types

### checkpoint:human-verify

Claude has done automated work; human confirms before proceeding.

When to use:
- Visual / UI work where automated verification is insufficient
- After a destructive operation, before the next
- When stakes are high and a wrong proceed is expensive

Example:
```
Task: Generate the marketing landing page
checkpoint:human-verify: "Visual check on the rendered page — does it match
                          the brand guidelines? If yes, proceed. If no, list
                          what to change."
```

### checkpoint:decision

Human makes a choice that Claude can't reasonably make alone.

When to use:
- Architecture choice (Redis vs Postgres for caching layer)
- Trade-off (speed vs robustness; quick fix vs proper refactor)
- Preference (UI tone — formal vs casual)
- Scope (include feature X or defer to v1.1?)

Example:
```
checkpoint:decision: "Choose auth provider: (a) build custom JWT,
                     (b) integrate Auth0, (c) use Supabase Auth.
                     Trade-offs documented in research-findings.md."
```

### checkpoint:human-action

Human MUST act in the real world (Claude can't).

When to use:
- 2FA / verification codes
- Account creation that requires email confirmation
- Physical hardware steps
- Inviting team members
- Anything requiring an account Claude doesn't have access to

Example:
```
checkpoint:human-action: "Click the verification link in the email I just
                         triggered. Confirm here when done."
```

USE SPARINGLY. Most "human-action" assumptions are wrong — there's a CLI / API that Claude could use. Verify before adding.

## Anti-pattern: human-action when CLI exists

Common mistakes:

```
✗ checkpoint:human-action: "Deploy to Vercel"
✓ vercel CLI exists; Claude can run `vercel deploy`

✗ checkpoint:human-action: "Create Stripe webhook"
✓ Stripe CLI: `stripe webhooks create --url=...`

✗ checkpoint:human-action: "Set environment variable in Vercel"
✓ `vercel env add VAR_NAME production`

✗ checkpoint:human-action: "Run database migration"
✓ Migration tools have CLIs; Claude runs them
```

Before adding human-action, ask: "Is there a CLI / API for this?" Usually yes.

## Checkpoint placement

In a plan file:

```markdown
## Task: Implement user auth flow

Steps:
1. Generate JWT signing keys
2. Add /api/auth/login endpoint
3. Add /api/auth/refresh endpoint
4. Add middleware for protected routes
5. checkpoint:human-verify — "Try logging in via the new flow on staging.
   Confirm the token persists across requests."
6. Deploy to production
```

The checkpoint goes BEFORE the irreversible operation, not after. "Confirm before deploy" not "deploy then confirm."

## What a checkpoint surfaces

When Claude reaches a checkpoint, it surfaces:

```
🔵 CHECKPOINT REACHED

Type: human-verify | decision | human-action
Context: <what was just completed; what's about to happen>
What I need from you: <specific question or confirmation>
Options (if decision): <list with recommendations>

Reply with: <verb that unblocks me>
```

The reply form should be specific:
- For verify: "ok proceed" / "stop and change X"
- For decision: pick from listed options
- For action: "done" / "couldn't because Y"

## Plan completion without checkpoints

Some plans legitimately have zero checkpoints — they're fully autonomous. This is fine when:
- The plan is reversible (worst case is revert)
- The stakes are low (failing isn't catastrophic)
- Verification can be automated (tests + monitors catch issues)

Don't add checkpoints performatively. Each one stops execution; pay for them where they pay back.

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/user-gates.md` — adjacent reference (where Claude asks the user mid-plan)
- `references/git-integration.md` — how checkpoints interact with commits
- `references/milestone-management.md` — checkpoints at milestone boundaries
