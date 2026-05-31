# Functional validation guide

> The Iron Rule. The one invariant Shannon will not compromise on.

## The Iron Rule, stated

> Validation evidence is real-system output captured to disk and cited specifically. Mocks, stubs, fixtures, and `*.test.*` files are not evidence. They are theater.

## Why

Tests pass without proving anything. We've all shipped a green CI build that broke users at runtime. The failure mode: the test exercised a fake; the user exercised the real thing. The discrepancy is invisible until it ships.

Functional validation closes the gap by *not allowing* the fake in the first place. Every claim of "X works" must cite a screenshot, curl response, CLI exit code, simulator recording, or other artifact from the real system.

## The five pillars in functional-validation terms

1. **Embedded sub-agent skills** — the validator agent has `functional-validation` baked into AGENT.md. It cannot "forget" to apply the rule.
2. **Orchestration** — when `/shannon:dispatch --mode parallel` spawns workers, each worker spawn fires `subagent-governance` hook injecting IRON RULE into stderr before the worker runs.
3. **Iron Rule validation** — this whole document.
4. **Meta-judge consensus** — judges score evidence against the rubric, not against vibes.
5. **Self-instrumented** — `scripts/doctor.py` and `/shannon:audit --scope completion-evidence` mechanically verify evidence presence.

## What counts as evidence

| Platform | Evidence type | Capture command |
|---|---|---|
| iOS | Simulator screenshot or recording | `xcrun simctl io <id> screenshot path.png` |
| Web frontend | Browser screenshot via Claude in Chrome / Playwright headed mode | `mcp__Claude_in_Chrome__navigate` + screenshot tool |
| Backend API | curl response body + headers + status code | `curl -i URL > evidence.txt` |
| CLI | Binary stdout/stderr + exit code | `./bin > evidence.txt 2>&1; echo "rc=$?" >> evidence.txt` |
| Full-stack | All of the above per surface | per-surface capture |

What does NOT count as evidence:

- "Tests pass" without the test output in the transcript
- "The build succeeded" without the post-build user-facing behavior verified
- "Looks good to me" without a cited artifact
- A `*.test.*` file's results (they don't exist in v1 — see Iron Rule)

## What's forbidden

The `block-fab-files` hook refuses Write/Edit on these path patterns:

- `*.test.<ext>` (e.g., `foo.test.js`)
- `*.spec.<ext>`
- `tests/`, `__tests__/`, `__mocks__/`, `mocks/`, `fixtures/`, `stubs/`

The `post-action-discipline` hook flags these content patterns:

- `jest.fn(`, `sinon.stub`, `vi.fn(`
- `faker.name`, `faker.address`, `faker.company`
- `MockedFunction`
- `describe(`, `it(` at the start of a line (test scaffolding)

If you genuinely need one of these (e.g., editing an existing project that has a test file you didn't write), the hooks are advisory (`exit 2`, not `exit 1`) — you'll see the warning but the action proceeds. The intent is to surface the discipline, not to force-cripple legitimate work in non-Shannon-pure environments.

## How the gates work

### evidence-gate (skill)

Six questions, applied before any completion claim. ANY single "no" answer refuses completion:

1. Is there an evidence file path I can `cat`?
2. Does the file have non-zero size?
3. Does the file show the actual real-system behavior (not just a build success)?
4. Is the evidence dated within the last hour?
5. Was the evidence captured AFTER the change being claimed?
6. Does the evidence match the specific claim (not adjacent behavior)?

### completion-gate (skill)

Mechanical final check before TaskUpdate(status=completed):

- All cited gate-criteria from the plan have been checked off
- Every check-off references a specific evidence file
- No criteria marked "skipped" or "deferred"

### refusal-discipline (skill)

If any gate refuses, `refusal-discipline` writes `REFUSAL.md` with:

```markdown
# REFUSAL

## What was claimed
<the claim, verbatim>

## Why refused
<specific cited blocker>

## Required to resolve
<specific actions: capture missing evidence, re-run failed validation, address cited gap>
```

Refusal is a first-class outcome. There is no `--force` flag. The user sees specifically what's missing and fixes it.

## The harness loop

Two harnesses ensure validation works end-to-end:

- **SDK harness** (`scripts/harness/sdk_runner.py`) drives Shannon via Python `claude_agent_sdk`
- **Tmux harness** (`scripts/harness/tmux_runner.py`) drives Shannon via the `claude` CLI in a tmux pane

Both target the same 5 benchmarks (one per pillar). Either failing blocks release.

See [docs/DEV_HARNESS.md](DEV_HARNESS.md) for the runbook.

## Cross-references

- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — the layers that enforce this
- [docs/SKILLS_CATALOG.md](SKILLS_CATALOG.md) — `functional-validation`, `no-fakes-discipline`, `evidence-gate`, `completion-gate`, `refusal-discipline` skills
- [docs/DEV_HARNESS.md](DEV_HARNESS.md) — the validation harnesses
- [docs/CONTRIBUTING.md](CONTRIBUTING.md) — how the Iron Rule applies to new contributions
- `.planning/BRIEF.md` — the original framing
