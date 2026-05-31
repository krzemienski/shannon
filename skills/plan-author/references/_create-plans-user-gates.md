# User Gates

> The structured pauses where Claude asks the user for input. Different from checkpoints — gates are for critical decision points where Claude won't proceed without input.

## Gates vs. checkpoints

- **Checkpoint**: a planned pause point in a phase. Specific question, specific answer.
- **Gate**: a class of pause — "I won't proceed past this kind of decision without explicit user input."

Gates are policy; checkpoints are instance.

## Mandatory gates (Shannon's defaults)

These pause Claude regardless of what the plan says:

### Gate 1: Before writing PLAN.md

After interview + initial sketch, Claude proposes the plan breakdown. User confirms before Claude commits to the structure.

```
Gate: "Plan ready. Here's what I'd produce:
  Phase 1: <one-line>
  Phase 2: <one-line>
  ...
  
  Approve / change / restart?"
```

Catching a mis-aligned plan here costs minutes; catching it after 3 phases of work costs hours.

### Gate 2: After low-confidence research

If research-findings.md has LOW confidence on a critical question:

```
Gate: "I researched <question>. My confidence on the answer is LOW because <reason>.
       Proceeding with my best guess vs. deferring to your judgment?"
```

Low confidence + auto-proceed → confidently-wrong code later.

### Gate 3: On verification failures

If the verify step of a task fails:

```
Gate: "Task verification failed: <what was expected> vs. <what was observed>.
       Likely causes: <list>.
       Options:
       (a) Auto-retry with <adjustment>
       (b) Investigate root cause first
       (c) Skip + log as known issue
       (d) Stop"
```

Don't silently retry. Each failure is signal.

### Gate 4: After phase completion with issues

If a phase completed but with deviations (Rule 5 deviations — see deviation_rules):

```
Gate: "Phase complete with deviations:
       1. Auto-fixed <bug> while doing main work
       2. Added <missing-critical> not in original plan
       Continue to next phase, or pause to review deviations?"
```

The default is continue; the gate exists to let user pause if needed.

### Gate 5: Before starting next phase with previous issues

If previous phase finished but flagged issues for the next:

```
Gate: "Phase N is done. It flagged 2 issues for Phase N+1:
       - <issue 1>
       - <issue 2>
       Proceed to Phase N+1, address those, or stop?"
```

## Optional gates (decided per-plan)

These are added to the plan when relevant:

### Gate: Before destructive operation

```
Gate: "About to: <delete X / rewrite Y / migrate Z>.
       This is hard to reverse. Confirm?"
```

For schema changes, large deletes, branch operations on shared branches.

### Gate: Before external API call (production)

```
Gate: "About to hit <production API>. This will <side effect>.
       Confirm?"
```

For ops involving paid services, account changes, etc.

### Gate: At cost / scope threshold

```
Gate: "Token usage at 60K (budget was 100K).
       Estimated remaining work: 40K.
       This will tighten. Proceed, split, or stop?"
```

## Gate response patterns

The user replies in one of three modes:

### Mode A: Direct answer

User picks an option:
```
Claude: "Approve / change / restart?"
User: "approve"
Claude: proceeds
```

### Mode B: Modification

User adjusts the plan:
```
Claude: "Phase 2: implement login endpoint"
User: "Phase 2: implement login AND password reset"
Claude: updates plan, re-presents gate
```

### Mode C: Defer

User can't decide yet:
```
Claude: gate
User: "let me look at the data first"
Claude: marks gate as deferred, returns control
```

## Gate output structure

Every gate emits:

```
🔵 GATE: <gate-type>

CONTEXT
<what's happening>

QUESTION
<specific question, with options if applicable>

DEFAULT (if no answer)
<what Claude does if user defers indefinitely — often: stop>

YOUR REPLY UNBLOCKS:
- "<option 1>" → Claude proceeds with <X>
- "<option 2>" → Claude proceeds with <Y>
- "stop" → Claude saves state, exits
```

The "your reply unblocks" section makes the unblock vocabulary clear.

## Gates in autonomous execution

For `/run-plan` / autopilot scenarios where Claude executes plans WITHOUT a human present:

- Default gates: defer to plan's checkpoints
- Autonomous-friendly: structure plans so they have FEW gates
- Auto-proceed: enable for verify-failures up to N retries (then escalate)

The trade-off: more gates = safer + slower; fewer gates = faster + riskier.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| No gates at all | Easy to drift undetected | Keep mandatory gates active |
| Gates after every task | Too granular; user fatigue | Only at decision points |
| Gates without specific options | User doesn't know what to say | Always list response options |
| Gates without a "stop" path | User can't pause | Always include stop |
| Auto-proceed past verify failures | Hides bugs | Always gate on verification failure |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/checkpoints.md` — specific checkpoint types
- `references/scope-estimation.md` — gates at scope thresholds
- `references/cli-automation.md` — when gate becomes "use the CLI instead"
- `skills/interview-framework/` — the gate before plan starts
