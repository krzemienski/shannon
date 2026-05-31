---
name: why
description: "Five-whys + root-cause-tracing + cause-and-effect diagram. Output root-cause analysis report."
argument-hint: "<symptom-or-bug-description>"
---

# /shannon:why

Root-cause analysis. Five-whys cascade plus cause-and-effect mapping.

## Inputs

- Positional: symptom or bug description

## Behavior

1. Invoke `Skill: root-cause-tracing`.
2. Apply five-whys:
   - Q1: Why does the symptom occur? → A1
   - Q2: Why does A1 happen? → A2
   - ...continue until reaching a root cause that is actionable.
3. Build cause-and-effect diagram (Ishikawa / fishbone; categories: code, data, config, environment, dependency, human).
4. Identify the smallest fix that addresses the root cause.
5. Output: `reports/root-cause-<slug>.md` with whys chain + diagram + proposed fix.

## Skills + agents

- `Skill: root-cause-tracing`
- `Skill: codebase-analysis` (for surface-area surveys)
- `Skill: reflect` (synthesis)

## Success criteria

- Five-whys chain reaches an actionable root cause.
- Diagram identifies primary category.
- Proposed fix is specific (file path + change description).

## Iron rules

- No "the system is buggy" — go deeper.
- No "more testing" — fix the cause, do not pad coverage.
- If you can't determine root cause in 10 min of reading: ADD INSTRUMENTATION before continuing.

## Examples

```
/shannon:why "Login button does nothing on Safari mobile"
/shannon:why "Deploy preview returns 502 on Vercel since yesterday"
```
