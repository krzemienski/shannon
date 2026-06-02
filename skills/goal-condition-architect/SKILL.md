---
name: goal-condition-architect
description: Transform any input into a single transcript-provable /goal completion condition. ALWAYS use when the user says "make a /goal", "set a goal", "goal condition", "transcript-provable end state", "airtight finish line", "design completion criteria", or "turn this into an autonomous run". Produces the four-part anatomy (end-state, checks, constraints, bound) and runs an adversarial harden pass before handing off.
triggers:
  - "make a /goal"
  - "set a goal"
  - "goal condition"
  - "transcript-provable end state"
  - "airtight finish line"
  - "design completion criteria"
  - "turn this into an autonomous run"
---

# goal-condition-architect

Turns any input — a voice ramble, a PLAN.md, a pasted spec, a Linear ticket — into a single, airtight Claude Code `/goal` completion condition that the evaluator can verify from the conversation transcript alone, without running any tools itself.

This is the **input shaping** half of the autonomy stack. The other half is `goal-loop-orchestrator` (running the goal). The end-to-end facade is `northstar`.

## When to use

- Any task that should "keep working until X" — the X must become a `/goal` condition.
- Migrating a vague chat request into an unattended autopilot run.
- Hardening a PLAN.md acceptance section so the evaluator can confirm completion.

## When NOT to use

- The task already has a complete `/goal` condition someone trusts.
- The success criterion is subjective ("makes the dashboard look nice") — those aren't transcript-provable. Refuse and explain.

## The four-part anatomy

Every `/goal` condition has exactly these four parts. If any is missing or vague, the condition is REFUSED and reshaped.

### 1. End-state

A single sentence describing the desired final state. Concrete nouns and verbs only.

- BAD: "Improve the login flow."
- GOOD: "The login endpoint returns HTTP 200 with a session cookie for valid credentials and HTTP 401 for invalid credentials, with no console errors during the request."

### 2. Checks (the proving commands)

Specific commands whose output the evaluator can read from the transcript. Three to seven checks, ordered. Each is paired with the expected signal.

- `pytest tests/auth/test_login.py -q` → final-line summary shows `0 failed`.
- `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3000/login -d valid.json` → output is `200`.
- `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3000/login -d invalid.json` → output is `401`.
- `grep -RE "(console|print)" src/auth | wc -l` → output is `0`.

### 3. Constraints (the forbidden moves)

What the agent is NOT allowed to do en route to satisfying the checks. Always include the canonical three:

- **No mocks/stubs/fixtures introduced** to satisfy the checks.
- **No tests deleted or skipped** to pass.
- **No `--force-complete` or equivalent override**.

Add task-specific constraints as needed:

- No new top-level dependencies in `package.json` unless approved.
- No edits to `archive/` or any read-only path.

### 4. Bound

The wall-clock or turn budget after which the run terminates regardless of progress. Bound is mandatory.

- `or stop after 60 turns`
- `or stop after 45 minutes`
- `or stop after 8 autopilot attempts`

The bound must be tied to a rationale recorded by the caller: "60 turns covers 4 features × ~15 turns each."

## The full condition shape

```
/goal Login endpoint returns 200 with session cookie for valid creds
and 401 for invalid creds, with no console errors during the request,
proven by:
  - `pytest tests/auth/test_login.py -q` shows "0 failed" in final line
  - `curl -X POST http://localhost:3000/login -d valid.json` returns 200
  - `curl -X POST http://localhost:3000/login -d invalid.json` returns 401
  - `grep -RE "(console|print)" src/auth | wc -l` returns 0
without introducing mocks/stubs/fixtures, without deleting or skipping
any test, without overriding the validation gate, or stop after 60 turns.
```

The evaluator reads this and the transcript, and answers "satisfied?" yes/no without running anything itself.

## The architect process

1. **Read the input.** Voice ramble, PLAN.md, ticket, doc — whatever the user dropped.
2. **Extract the end-state.** One sentence; if you can't, the input is too vague — ask one clarifying question or refuse.
3. **Detect the proving commands.** Read `package.json`, `pyproject.toml`, `Makefile`, CI config, `.github/workflows/`. Pick commands whose final-line summary is unambiguously parseable. If none exist, propose a new one.
4. **Write the constraints.** Always include the canonical three. Add task-specific ones drawn from the input.
5. **Pick a bound.** Tied to task size. Record the rationale.
6. **Adversarial harden.** Re-read the condition asking: "could a turn that didn't actually finish produce output the evaluator would rubber-stamp?" If yes, add a check or constraint that closes the hole.
7. **Present.** Output the full `/goal ...` line, the bound rationale, and a one-paragraph user confirmation.

## Adversarial harden — the most important step

The condition only matters if a no-op turn cannot pass it. Walk through these failure modes:

- **The "echoed PASS" attack.** Could the agent print "all tests pass" without running them? Counter: require the actual command name + final-line summary in the transcript.
- **The "comment-out" attack.** Could the agent satisfy the check by removing the test? Counter: constraint "no tests deleted or skipped."
- **The "fixture-ize" attack.** Could the agent monkey-patch the system under test? Counter: constraint "no mocks/stubs/fixtures introduced."
- **The "force-complete" attack.** Could the agent flip a flag and exit? Counter: constraint "no `--force-complete` or equivalent."
- **The "different test" attack.** Could the agent run a passing test and claim it covers the criterion? Counter: pin the test path in the check.

If any attack lands, **edit the condition until it doesn't.**

## The clarifier — at most one question

If the input is too vague to produce a transcript-provable condition, ask ONE clarifying question and stop. Don't grill the user. If even one good question can't unlock a condition, refuse and explain.

## Iron rules

- **Four parts. Always.** End-state, checks, constraints, bound. None optional.
- **Constraints always include the canonical three.**
- **Bound is mandatory.** No "until done" without a turn/time cap.
- **Adversarial harden is the last step before hand-off.** Skip it and the condition is fragile.
- **At most one clarifier.** If you need more, refuse.
- **Transcript-provable means the evaluator runs NO tools.** If a check requires the evaluator to execute something, rewrite it.

## Cross-references

- `skills/goal-loop-orchestrator/SKILL.md` — runs the condition this skill produces
- `northstar` — end-to-end facade combining this + the loop orchestrator
- `goal-workflow` — input → condition → run pipeline
- `goal-engineering` — deeper patterns + condition library cross-reference
- `condition-library` — reusable condition templates per project type
- `skills/autopilot-runner/SKILL.md` — Shannon-native consumer of well-formed conditions
- `skills/loop-runner/SKILL.md` — bounded loop that proves against these conditions


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `northstar`

# northstar

The top-level entry to the autonomy stack. Whenever the user describes substantial multi-turn work with a verifiable end state — even without saying "/goal" — northstar fires.

This is `goal-workflow` with a stronger trigger surface and a slightly different default posture: it leans toward running the condition rather than just presenting it (with explicit user consent).

## The five-step pipeline

1. **Capture the input.** Voice ramble, PLAN.md, ticket, current conversation, rough sketch.
2. **Architect the condition.** Delegate to `goal-condition-architect`.
3. **Adversarial harden.** Standard four-attack pass.
4. **Confirm with user.** Present the full `/goal` line. Default: ask "run it now? (y/N)".
5. **Run.** On yes, run `goal-loop-orchestrator` with preconditions check, live status, diagnose-on-stall.

## When to use

- The user said "until X is done" / "loop until passing" / "keep working".
- The user dropped a substantial spec/PRD/ticket and expects autonomous execution.
- Mentioned `/goal` explicitly.
- Described work with a verifiable end state (migration, refactor, test suite green, etc.) even without autonomy framing.

## When NOT to use

- The end state is subjective ("make the dashboard look nicer") — not transcript-provable.
- The task needs human approval between steps — use interactive `/shannon:cook`.
- Quick one-shot edit — just do it.
- Already inside an active `/goal` run — don't nest.

## The four condition anatomies

Same as `goal-condition-architect`:

1. **End-state** — concrete one-sentence description.
2. **Checks** — 3-7 specific proving commands with expected signals.
3. **Constraints** — canonical three (no mocks, no test deletion, no force-complete) plus task-specific.
4. **Bound** — turn/minute/attempt cap with rationale.

## Default trigger posture

Northstar is greedy: it fires on descriptions of substantial work even when the user doesn't say "/goal" or "autopilot." This is intentional — the autonomy stack should be reachable without remembering the exact incantation.

If you're not sure whether northstar fits, ask one question:
> "This sounds like a substantial run with a verifiable end state. Want me to set it up as a /goal so it runs to completion unattended?"

If yes → execute the five-step pipeline. If no → return to whatever the user actually wanted.

## Iron rules

- **Adversarial harden is non-negotiable.**
- **User confirms before run** (unless `--yes` was passed).
- **One northstar / one `/goal` at a time per session.**
- **Bound is mandatory.** Defaults if not user-supplied, with a one-line rationale.
- **STALLED requires a diagnosis report.** Never drop the user without next-step guidance.

## Cross-references

- `skills/goal-condition-architect/SKILL.md` — step 2 delegate
- `skills/goal-loop-orchestrator/SKILL.md` — step 5 delegate
- `goal-workflow` — slightly more conservative facade with `/shannon:goalify`
- `goal-engineering` — patterns
- `goal-orchestration` — orchestration patterns
- `condition-library` — reusable conditions
- `skills/autopilot-runner/SKILL.md` — Shannon-native multi-phase analog
- `deep-interview` (oh-my-claudecode plugin) — escalate here when too vague

## Absorbed from `goal-engineering`

# goal-engineering

The deep reference for writing robust `/goal` conditions. Where `goal-condition-architect` is the procedure, this is the patterns and the craft.

Use this skill when:
- A condition keeps stalling and you suspect it's the condition's fault.
- You're writing a condition for a domain you haven't goal-engineered before.
- You want to teach goal-writing to a team.

## The condition is a contract

A `/goal` condition is a contract between the user and the evaluator. Three properties make it strong:

1. **Specific** — every check is unambiguous. No "the tests pass" — pin the test path and the final-line summary shape.
2. **Achievable** — every check can be made true by code edits + executing commands. No checks that depend on third-party state outside the agent's reach.
3. **Falsifiable from transcript** — the evaluator can answer "satisfied?" without running anything itself.

If any property fails, the condition is fragile and the loop will produce noise instead of progress.

## Patterns for the four parts

### End-state patterns

| Pattern | Example | When |
|---|---|---|
| Endpoint-behavioral | "Login endpoint returns 200/401 correctly with cookie set" | Web/API |
| Test-suite-green | "All tests in `tests/auth/` pass under `pytest -q`" | Test-driven work |
| Lint/Type-clean | "`mypy --strict src/` and `ruff check src/` both exit 0" | Cleanup |
| Migration-complete | "All files under `src/legacy/` migrated to `src/v2/` shape, zero imports of `src/legacy/` remain" | Codemods/migrations |
| Build-passing | "`npm run build` exits 0 with no warnings about deprecated APIs" | Build hygiene |
| Performance-budget | "p95 latency on `/login` < 150ms over 100 sequential curl calls" | Perf |

### Check patterns — make every check parseable

Bad check (not parseable from transcript):
- `"the tests work"` — what tests? what's the signal?

Good check:
- `"`pytest tests/auth/ -q | tail -1` shows '14 passed' substring"` — pinned path, pinned shape.

Common parseable signals:

| Tool | Signal pattern |
|---|---|
| `pytest -q` | final line `==== N passed ===` |
| `cargo test` | final line `test result: ok. N passed; 0 failed` |
| `npm test` | summary line `Tests: N passed, N total` |
| `mypy` | exit code 0, no "error:" lines |
| `ruff check` | exit code 0, "All checks passed!" |
| `curl -w "%{http_code}"` | numeric status code |
| `grep -c` | numeric count |
| `wc -l` | numeric count |
| `git diff --shortstat` | "N files changed" line |

Avoid signals that depend on parsing complex stdout. Numeric counts and pinned substrings travel.

### Constraint patterns

The canonical three:
- **No mocks/stubs/fixtures introduced** to satisfy the checks.
- **No tests deleted or skipped.**
- **No `--force-complete` or equivalent override.**

Task-specific constraints to consider:

- "No new dependencies added to `package.json` / `Cargo.toml` / `pyproject.toml`."
- "No edits to `archive/` or any read-only path."
- "Diff under 500 lines (sanity)."
- "Commit messages follow Conventional Commits."
- "All changed files have updated/added tests in the same commit."

### Bound patterns

| Bound shape | Rationale shape |
|---|---|
| `60 turns` | "4 features × 15 turns each" |
| `45 minutes` | "SLA from caller; CI job time-bounded" |
| `8 attempts` (autopilot) | "complex multi-phase, give it room" |
| `200 tool calls` | "cost-bounded; ~$X budget" |

Never set a bound without a one-line rationale. The rationale survives runaway-loop investigations.

## Adversarial attack patterns

When hardening, walk through these:

| Attack | Counter |
|---|---|
| **Echoed PASS** — agent prints "all green" without running anything | Require the command name + final-line shape in transcript |
| **Comment-out** — agent satisfies a check by deleting the test | Constraint "no tests deleted or skipped" |
| **Fixture-ize** — agent monkey-patches the system under test | Constraint "no mocks/stubs/fixtures introduced" |
| **Force-complete** — agent flips a flag and exits | Constraint "no force-complete" |
| **Wrong-test** — agent runs a passing adjacent test and claims coverage | Pin the test path in the check |
| **Tautology** — check is `if x: pass` shaped, always passes | Re-read check; ensure it can fail |
| **Outside-tree** — agent edits CI config to skip the criterion | Constraint "no edits to `.github/`/`.gitlab-ci.yml`" |

## When a condition is fundamentally too vague

If the end-state can't be reduced to 3-7 transcript-parseable commands, the work is too qualitative for `/goal`. Options:

1. **Decompose** — split into multiple `/goal`s, each with concrete checks.
2. **Add an objective proxy** — "no console errors in browser test" is checkable; "looks nice" is not.
3. **Refuse** — return to the user with "this isn't a `/goal`-shaped task; here's why."

## Iron rules

- **Every check is pinned** (path + signal shape).
- **Every constraint reduces an attack surface.**
- **Every bound has a rationale.**
- **Adversarial harden before hand-off.**
- **No vague end-states.** If you can't write the check, the end-state isn't ready.

## Cross-references

- `skills/goal-condition-architect/SKILL.md` — the procedure
- `skills/goal-loop-orchestrator/SKILL.md` — the executor
- `condition-library` — reusable templates
- `northstar` + `goal-workflow` — facades
- `skills/no-fakes-discipline/SKILL.md` — reinforces "no mocks" constraint

## Absorbed from `condition-library`

# condition-library

A catalog of reusable `/goal` completion-condition templates. Each template is a starting point; `goal-condition-architect` always runs an adversarial harden pass before the condition is used.

Templates are organized by **shape** (what kind of end-state) × **stack** (what proving commands fit).

## Shape: test-suite-green

### Python (pytest)

```
/goal All tests in <test_path> pass under pytest, proven by:
  - `pytest <test_path> -q | tail -1` shows "0 failed" substring
  - `git diff --shortstat` shows no deletions of files under <test_path>
without introducing mocks/stubs/fixtures, without deleting or skipping
any test, without overriding the validation gate, or stop after 60 turns.
```

### Node (jest/vitest)

```
/goal All tests in <test_path> pass, proven by:
  - `npx jest <test_path> --silent | tail -10` shows "Tests:" line with "0 failed"
  - `git diff --shortstat <test_path>` shows no deletions
without introducing mocks/stubs/fixtures, without deleting or skipping
any test, without overriding the validation gate, or stop after 60 turns.
```

### Rust (cargo)

```
/goal All tests in the workspace pass, proven by:
  - `cargo test 2>&1 | tail -5` shows "test result: ok" line with "0 failed"
without introducing mocks/stubs/fixtures, without deleting or skipping
any test, without overriding the validation gate, or stop after 90 turns.
```

## Shape: lint-clean

### Python (ruff + mypy)

```
/goal `src/` passes strict lint and type checks, proven by:
  - `ruff check src/` exits 0 with "All checks passed!" in stdout
  - `mypy --strict src/ 2>&1 | tail -1` shows "Success: no issues found"
without disabling rules via inline comments, without adding rule ignores
to pyproject.toml, without overriding the validation gate, or stop after 50 turns.
```

### TypeScript (tsc + eslint)

```
/goal `src/` passes strict type and lint checks, proven by:
  - `npx tsc --noEmit` exits 0 with no error output
  - `npx eslint src/ --max-warnings 0` exits 0
without adding `eslint-disable` comments, without weakening tsconfig.json,
without overriding the validation gate, or stop after 50 turns.
```

## Shape: build-passing

```
/goal The project builds cleanly, proven by:
  - `<build_cmd> 2>&1 | tail -20` shows no "error" or "ERROR" lines
  - `<build_cmd>` exits 0
  - The build output artifact exists at <artifact_path>
without disabling build steps, without `// @ts-ignore` or equivalent,
without overriding the validation gate, or stop after 30 turns.
```

Common `<build_cmd>` values: `npm run build`, `cargo build --release`, `make`, `python -m build`, `mvn package`.

## Shape: migration-complete

```
/goal All files under <legacy_path> migrated to <new_path>, with no
imports of <legacy_path> remaining in <src_path>, proven by:
  - `find <legacy_path> -type f \( -name '*.py' -o -name '*.ts' \) | wc -l` returns 0
  - `grep -r 'from <legacy_path>' <src_path> | wc -l` returns 0
  - `grep -r 'import <legacy_path>' <src_path> | wc -l` returns 0
  - existing test suite passes: `<test_cmd>` exits 0
without deleting tests, without `# noqa` or equivalent suppressions,
without overriding the validation gate, or stop after 90 turns.
```

## Shape: api-contract

```
/goal The <endpoint> endpoint conforms to its contract, proven by:
  - `curl -s -o /dev/null -w "%{http_code}" -X POST <endpoint> -d <valid_payload>` returns 200
  - `curl -s -o /dev/null -w "%{http_code}" -X POST <endpoint> -d <invalid_payload>` returns <expected_error_code>
  - `curl -s -X POST <endpoint> -d <valid_payload> | jq -r '<response_schema_check>'` returns <expected_value>
without modifying the test payloads, without altering the route to
match the test instead of the contract, without overriding the
validation gate, or stop after 40 turns.
```

## Shape: perf-budget

```
/goal The <endpoint> endpoint meets its latency budget, proven by:
  - `for i in $(seq 1 100); do curl -w "%{time_total}\n" -s -o /dev/null <endpoint>; done | sort -n | awk 'NR==95'` returns a value < 0.15
  - the existing test suite continues to pass: `<test_cmd>` exits 0
without caching responses to game the measurement, without short-circuiting
the endpoint logic, without overriding the validation gate, or stop after 50 turns.
```

## Shape: deslop-clean

```
/goal The diff between <base_ref> and HEAD contains no AI slop signatures, proven by:
  - `grep -rE "(TODO: ai-generated|placeholder implementation|# stub for now)" <changed_paths> | wc -l` returns 0
  - `git diff <base_ref>..HEAD | grep -E "^\+.*\b(any|TODO|FIXME)\b" | wc -l` returns 0
  - existing test suite continues to pass: `<test_cmd>` exits 0
without reverting the underlying feature work, without weakening tests,
without overriding the validation gate, or stop after 30 turns.
```

## How to use a template

1. **Copy** the template that matches the end-state shape.
2. **Substitute** the `<...>` placeholders with concrete values from the project.
3. **Run `goal-condition-architect`** on the substituted condition — it will run the adversarial harden pass and may add task-specific checks.
4. **Confirm** with the user.
5. **Hand off** to `goal-loop-orchestrator` (or paste into `/goal`).

## Iron rules

- **Templates are starting points, not finished conditions.** Always run the architect harden pass.
- **Every check must be transcript-parseable.** If a template's check isn't parseable in your environment, replace it before hand-off.
- **The canonical three constraints are always present.** No template drops them.
- **The bound is a placeholder.** Tune it to the actual task size with a recorded rationale.

## Cross-references

- `skills/goal-condition-architect/SKILL.md` — runs the harden pass on these templates
- `goal-engineering` — patterns + attack catalog
- `skills/goal-loop-orchestrator/SKILL.md` — executes the resulting condition
- `northstar` + `goal-workflow` — facades that compose this with the architect and the orchestrator
