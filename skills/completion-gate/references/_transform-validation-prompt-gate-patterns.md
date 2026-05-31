# Gate Patterns

> Reusable patterns for injecting validation gates into prompts. A gate is a phase-boundary check with explicit PASS criteria and required evidence.

## Anatomy of a validation gate

Every gate has four parts:

```yaml
gate:
  name: "<short description>"
  phase: "<which phase boundary this fires at>"
  pass_criteria:
    - "<specific, observable condition 1>"
    - "<specific, observable condition 2>"
  required_evidence:
    - "<file path / transcript marker / system state>"
  fail_action: "<what happens on fail — retry, escalate, abort>"
```

If any of the four are missing, it's not a gate. It's a vibe-check.

## Pattern: Build gate

Fires after a build phase. Wraps `cargo build` / `npm build` / `go build` / `xcodebuild` etc.

```yaml
gate:
  name: "build green"
  phase: "after-build, before-execute"
  pass_criteria:
    - "build command exits with code 0"
    - "no warnings (or warnings explicitly accepted)"
    - "build artifact exists at expected path"
  required_evidence:
    - "transcript line: 'BUILD SUCCEEDED' or equivalent"
    - "file: ./target/release/<binary> exists"
  fail_action: "retry once; on second fail, abort and report"
```

Inject this gate by appending to the implementation prompt:

```
Build the project. The following GATE applies before any execute step:

[GATE: build green]
- Run the build command appropriate to the project (cargo build / npm run build / etc.).
- Capture full stdout + stderr to e2e-evidence/build.log.
- Verify exit code is 0; if not, output the last 50 lines of the log and STOP.
- Confirm the build artifact exists at its expected path before proceeding.
```

## Pattern: Execute gate

Fires after the binary / service is launched. Confirms the system is running.

```yaml
gate:
  name: "execute reachable"
  phase: "after-execute, before-validate"
  pass_criteria:
    - "process running"
    - "health endpoint or smoke command returns 200 / 0"
    - "first-load latency below threshold"
  required_evidence:
    - "process ID captured"
    - "curl response or smoke output"
  fail_action: "kill stale processes, retry; on second fail, abort"
```

## Pattern: Side-effect gate

Fires after a mutation. Confirms the mutation actually happened.

```yaml
gate:
  name: "side-effect verified"
  phase: "after-mutation"
  pass_criteria:
    - "the mutation's observable result exists"
    - "the result matches the expected shape"
  required_evidence:
    - "readback (curl GET after POST, db query after insert, file read after write)"
    - "diff captured between before and after state"
  fail_action: "investigate — mutation may have partially succeeded; never silently re-run"
```

This is the gate that catches "POST returned 201 but DB has no row" — a class of bug pure response-checking misses.

## Pattern: No-mocks gate

Fires inside any validation phase. Refuses mocks/stubs introduced during the work.

```yaml
gate:
  name: "no mocks"
  phase: "every step of a validation phase"
  pass_criteria:
    - "no test_*.py, *_test.go, *.test.tsx files created"
    - "no functions named mock_*, stub_*, fake_*"
    - "no skip-real-system flags introduced"
  required_evidence:
    - "git status during validation — diff is review-able"
    - "PreToolUse:Write hook log shows zero refusals (or refusals were respected)"
  fail_action: "revert the offending change; restart validation"
```

This is the Iron Rule gate. In Shannon it's enforced by the `block-fab-files` hook AND by the gate-validation-discipline skill, in tandem.

## Pattern: Transcript-evidence gate

Fires at the verdict step. Refuses verdicts without surfaced output.

```yaml
gate:
  name: "verdict requires transcript evidence"
  phase: "before-pass-claim"
  pass_criteria:
    - "the command that produced the verdict appears in the transcript"
    - "its output (or a substantial excerpt) appears in the transcript"
    - "the verdict cites a specific line / file / count from that output"
  required_evidence:
    - "transcript content — the gate inspects it directly"
  fail_action: "REFUSE the PASS claim; relabel as INDETERMINATE"
```

The most important gate. Without it, "tests pass" is a fluent fiction.

## Pattern: Schema-conformance gate

Fires after structured output is produced. Validates against a schema.

```yaml
gate:
  name: "schema conformance"
  phase: "after-output-produced"
  pass_criteria:
    - "output parses as the declared format (JSON, YAML, etc.)"
    - "output matches the declared schema (all required fields present, types correct)"
  required_evidence:
    - "schema definition (JSON Schema, Pydantic model, TypeScript interface)"
    - "parse + validate command output"
  fail_action: "retry with format reminder; on second fail, abort"
```

For LLM outputs that need to be machine-readable.

## Pattern: Convergence gate

Fires inside a loop. Decides whether to iterate again or exit.

```yaml
gate:
  name: "converged"
  phase: "after-each-iteration"
  pass_criteria:
    - "metric improved less than X% over last N iterations"
    OR
    - "metric reached target threshold"
    OR
    - "max-iterations reached"
  required_evidence:
    - "per-iteration metric log"
    - "comparison vs. prior iteration"
  fail_action: "loop back for another iteration"
  exit_action: "report final metric, summarize history"
```

Used by `loop-runner`, `autopilot-runner`, `ralph`, `goal-loop-orchestrator`. Convergence prevents infinite loops.

## Pattern: Stall-detection gate

Fires inside a loop alongside the convergence gate.

```yaml
gate:
  name: "stall detected"
  phase: "after-each-iteration"
  pass_criteria:
    - "same failure category + same root file 3 consecutive iterations"
    - "no progress on dominant findings 2 consecutive iterations"
  required_evidence:
    - "per-iteration finding categorization"
    - "diff log showing what changed (if anything) between iterations"
  fail_action: "EXIT loop with STALL verdict; escalate to user with diagnostic"
```

Stall detection is the safety valve that prevents loop_runner from spinning forever.

## How to inject gates into a prompt

For ANY prompt that produces a verdict, completion claim, or output that downstream consumers rely on, append a gate block:

```
After completing the task, the following GATE applies:

[GATE: <name>]
Pass criteria:
  - <criterion 1>
  - <criterion 2>
Required evidence:
  - <evidence 1>
On fail:
  - <action>

Apply this gate before claiming completion. If you can't satisfy it, output a
FAIL verdict with the missing evidence enumerated. Do NOT claim PASS with
incomplete evidence.
```

This is what `transform-validation-prompt` skill does — takes an arbitrary prompt and injects the appropriate gate block(s).

## Choosing which gates to inject

| Prompt produces | Gate pattern(s) |
|-----------------|-----------------|
| Code that needs to compile | Build gate |
| A service that needs to run | Execute gate |
| A mutation | Side-effect gate |
| A test verdict | Transcript-evidence gate |
| Validation work | No-mocks gate + Transcript-evidence gate |
| Structured output (JSON, etc.) | Schema-conformance gate |
| A loop iteration | Convergence + Stall-detection gates |
| A multi-phase plan | Phase-transition gates per `spec-workflow` |

## Gate-injection anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| "Soft" gates ("try to ensure...") | Easy to rationalize past | Hard gates with explicit PASS criteria |
| Pass criteria without evidence requirements | Verdict can be claimed without showing work | Always pair PASS criteria with required evidence |
| Gates with no fail action | The gate triggers but nothing happens | Specify retry / abort / escalate explicitly |
| Stacking 8 gates on a tiny phase | Overhead exceeds value | Pick the 1-2 most relevant gates per phase |
| Gates without phase scoping | Confused about when the gate fires | Specify the phase boundary explicitly |

## Cross-references

- `skills/transform-validation-prompt/` — parent skill (injects these gates)
- `skills/gate-validation-discipline/` — the discipline behind the gates
- `skills/no-mocking-validation-gates/` — companion no-mocks discipline
- `skills/plan-author/` — composes gates into plan phases
- `skills/spec-workflow/references/phase-transitions.md` — the phase-level transition gates
- `skills/functional-validation/` — the Iron Rule that gates enforce
