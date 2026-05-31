---
name: reflect
description: Self-refinement pass on prior output with dominant-gap discipline (≤ 3 gaps, most blocking first), reflective tone, transcript-proof requirement on proposed fixes, and recurrence-promotion to memorize. ALWAYS use when the user says "reflect on this", "self-refine", "self-improve this", "what could be better", "reflection pass", invokes /shannon:reflect --mode self, or runs the inner reflection step of /shannon:loop.
triggers:
  - "reflect on this"
  - "self-refine"
  - "self-improve this"
  - "what could be better"
  - "reflection pass"
  - "dominant gap"
---

# reflect

Backs `/shannon:reflect --mode self`. Also the inner reflection step of `/shannon:loop` (loop-runner).

## Behavior contract

1. **Read the artifact under reflection** — last assistant turn, completed file, named target, or current iteration's evidence dir.
2. **Categorize the gaps** using the five-category taxonomy (see below).
3. **Apply dominant-gap discipline** — at most 3 gaps surfaced, ordered by most-blocking first. If more exist, batch them and only surface 3.
4. **For each gap, propose a fix with transcript-proof shape** — a concrete action verb AND the command whose output will prove the fix worked.
5. **Output `reflect.md`** with the structure below.
6. **Recurrence-promotion check** — if the same gap fingerprint has appeared 3+ sessions in a row, recommend `/shannon:reflect --mode memorize` to promote into a persistent rule.

## The five-category gap taxonomy

| Category | Smell | Fix shape |
|---|---|---|
| **Unaddressed asks** | User requested X, response addressed Y instead | "Re-read the user's prompt; the missing ask is <quote>. Address it by <action>." |
| **Vague claims** | "should work" / "improved" without citation | "Replace claim '<quote>' with the command + output that proves it." |
| **Missing evidence** | Claimed PASS without cited artifact | "Run `<cmd>` and surface its output verbatim before re-claiming PASS." |
| **Drive-by edits** | Changed lines that don't trace to the user's ask | "Revert <file:lines>; not asked for. If needed, justify in next turn." |
| **Premature completion** | TaskUpdate=completed without gate | "Re-open the task. Gate verdict required before completion." |

## Reflective tone

Borrowed from `lesson-learned` (agent-toolkit). The reflect output is **reflective, not prescriptive**:

- BAD: "You should have run the tests before claiming PASS."
- GOOD: "The approach here surfaces a `PASS` without command output. Next iteration, run `<cmd>` and let its final-line summary speak."

Use the user's own code/output as primary evidence. Frame fixes as observations + actions, not commands.

## Output shape

```markdown
## Artifact reflected
<path or "last assistant turn">

## Gaps (dominant-first, cap 3)

### 1. <category> — <one-line smell>
**Observation**: <quote or paraphrase from artifact>
**Fix**: <action verb> — <specific change>
**Proves**: `<command>` whose output shows <expected signal>

### 2. <category> — <one-line smell>
...

### 3. <category> — <one-line smell>
...

## Recurrence
<one of:>
- "Fresh — no matching gap fingerprint in recent sessions."
- "Recurrence: matches gap fingerprint '<X>' from 3 prior sessions. Recommend `/shannon:reflect --mode memorize` to promote to a persistent rule."

## Converged?
YES | NO

(If NO, the proposed fixes are the next-iteration prompt for /shannon:loop.)
```

## Transcript-proof on every fix

Iron Rule from `goal-loop-orchestrator`: every proposed fix MUST include the **command that proves the fix**, not just the action. This is what makes reflect's output actionable inside a loop.

- BAD: "Fix: re-run pytest."
- GOOD: "Fix: edit `tests/auth/test_login.py:47` to remove the stale assertion. Proves: `pytest tests/auth/test_login.py -q` final line shows '14 passed, 0 failed'."

## Recurrence promotion

If the same gap fingerprint (`<category>:<first 80 chars of smell>`) has appeared in:
- 3+ recent `reflect.md` outputs across sessions, OR
- 3+ iterations of the current `/shannon:loop` run

… then the gap is a pattern, not an incident. Reflect's output recommends promoting it via `Skill(memorize)` with type=feedback so the rule is persisted and the next session avoids it.

## Mode escalation

If reflect-self surfaces fewer than 2 gaps but the artifact still feels incomplete (subjective, but flag it), the output recommends:

```
Suggested next mode: `/shannon:reflect --mode critique` (adversarial reviewer voice)
```

Critique uses a stricter posture and may surface gaps reflect-self glossed over.

## When to use

- End of a `/shannon:loop` iteration.
- After completing a phase, before TaskUpdate=completed.
- User says "reflect on this" / "what could be better".
- Inner step of `autopilot-runner` phases when intermediate verdicts feel thin.

## When NOT to use

- Trivial change with nothing to reflect on.
- Adversarial review — use `/shannon:reflect --mode critique` instead.
- Reflecting on something already converged — pointless overhead.

## Iron rules

- **At most 3 gaps surfaced.** Dominant-first. If more exist, batch.
- **Every fix has a transcript-proof command.** No "try harder."
- **Reflective tone — observations, not commands.**
- **Recurrence check on every run.** Surface promotion candidates.
- **Mode escalation suggestion is automatic** when reflect-self finds < 2 gaps.
- **Converged YES means the inspector cannot find another gap** in the dominant category. Soft gaps may still exist below threshold.

## Cross-references

- `skills/loop-runner/SKILL.md` — invokes this as the inner reflection step
- `skills/memorize/SKILL.md` — recurrence-promotion target
- `skills/critique/SKILL.md` — adversarial counterpart (mode=critique)
- `skills/deep-interview/SKILL.md` — escalate here when reflect-self under-yields
- `skills/goal-loop-orchestrator/SKILL.md` — transcript-proof discipline source
- `skills/lesson-learned/SKILL.md` — reflective-tone source
- `skills/reflexion/SKILL.md` — broader self-reflection doctrine

## References

See `references/gap-taxonomy.md` for worked examples per category.
