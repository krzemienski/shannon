# Team Coordination Protocol (Phase 2 of full-functional-audit)

This reference is loaded by Phase 2 (PLAN — Assign Validation Work) of `full-functional-audit`. It expands the resource-mutex rules, team-template wiring, and parallel-vs-exclusive classification that allow multiple validator subagents to operate without colliding on shared resources.

## The core problem

A simulator can only show one app at a time. A simulator can only be tapped by one operator at a time. A simulator screenshot taken during a different operator's interaction shows the wrong screen.

Same for the backend: code edits to the backend codebase by one team member during another's curl test corrupt the test. Two `xcodebuild` invocations on the same workspace fight for derived data.

The protocol enforces mutex on shared exclusive resources and parallelism only where it is safe.

## Resource classification

| Resource | Class | Why |
|---|---|---|
| Simulator (iOS, macOS) | EXCLUSIVE | Only one app can be foreground; only one tap can register at a time |
| Real device (USB-attached) | EXCLUSIVE | Same as simulator |
| Backend process | SINGLETON | One backend on one port; concurrent writers collide on port |
| Backend code edits | EXCLUSIVE | Two writers can produce broken intermediate states |
| iOS code edits | EXCLUSIVE | Same as backend code edits |
| Database (write) | EXCLUSIVE | Concurrent writers in the same scenario invalidate test isolation |
| Database (read) | PARALLEL | Read-only queries are concurrency-safe |
| Reading the codebase | PARALLEL | No state mutation; any number of readers |
| curl against running backend | PARALLEL | The backend is the singleton; clients can be many |
| agent-browser sessions | PARALLEL (per-session) | Each session has its own browser process |
| Evidence writes | PARALLEL (per-directory) | Each validator writes to its own evidence subdir |
| Inventory file (read) | PARALLEL | Read-only after Phase 1 sealed |

## Mutex ownership

The team-builder agent owns the simulator and backend mutexes. Every validator that needs an EXCLUSIVE resource must:

1. Request the lock from team-builder
2. Receive an acknowledgment
3. Hold the lock for as short as possible
4. Release on completion
5. Never assume the lock is held across messages — re-acquire if interrupted

The lock mechanism is conceptual; in practice the team-builder serializes EXCLUSIVE work by NOT dispatching two exclusive sub-tasks at the same time.

## Team templates

### iOS / macOS team

```
team-builder (orchestrator)
├── meta-judge (Phase 1 inventory + rubric generation, read-only, parallel)
├── team-validator (Phase 3 curl checks against backend, parallel)
└── team-qa (Phase 3 UI validation, requires simulator lock)
```

Sequencing within an audit run:

1. team-builder reads the inventory
2. meta-judge runs Phase 1 in parallel with team-validator running backend-only checks
3. team-qa serially walks each screen — one screen at a time — holding the simulator lock
4. team-validator continues in parallel as long as no code edits are in flight
5. Phase 4 remediations are EXCLUSIVE — team-builder pauses all validators, applies the fix, rebuilds, then resumes

### Web / Full-Stack team

```
team-builder (orchestrator)
├── meta-judge (inventory + rubric, read-only, parallel)
├── team-validator (Phase 3 curl checks, parallel)
├── team-qa (Phase 3 browser validation via agent-browser, parallel sessions)
└── team-qa-integration (cross-layer checks, parallel)
```

Web is more parallelizable than iOS because each agent-browser session is independent. The constraints become:
- Backend code edits remain EXCLUSIVE
- Database state remains shared — careful with test data overlap

### API-only team

```
team-builder
├── meta-judge (route inventory + rubric)
└── team-validator (curl validation, fully parallel — backend is the singleton)
```

For an API-only audit, parallelism is bounded only by the backend's capacity. Run as many curl validators as the backend handles.

## Dispatch patterns

### Single-message parallel dispatch (CRITICAL)

When the team-builder dispatches multiple parallel agents, the dispatch MUST be in a single message. Sequential message-per-agent kills parallelism (each agent runs to completion before the next starts).

```
BAD (sequential):
  Message 1: "team-validator, validate /api/users"
  [wait for completion]
  Message 2: "team-validator, validate /api/orders"
  [wait for completion]

GOOD (parallel):
  Message 1: spawn team-validator-1 on /api/users
             spawn team-validator-2 on /api/orders
             spawn team-validator-3 on /api/products
             — all in one Task tool block
```

The PreToolUse:Task hook in Shannon enforces this rule by detecting and rejecting serial dispatch when parallel was intended.

### Sequential dispatch (required when ordering matters)

```
team-qa walks screens in order:
  1. HomeView (returns simulator lock)
  2. DetailView (acquires lock, returns lock)
  3. SettingsView (acquires lock, returns lock)
```

Screens MUST be sequential because they all need the simulator.

### Competitive dispatch (Phase 4 fixes)

When a screen FAILs in Phase 3, dispatch the fix as a competitive task: 2 candidates produce fix attempts, meta-judge generates a rubric, judge picks the better fix.

```
Phase 4 dispatch:
  fixer-1: write fix attempt A
  fixer-2: write fix attempt B
  meta-judge: generate rubric for "good fix"
  judge: score both against rubric → winner
  team-builder: apply winner, rebuild, return to Phase 3 for re-validation
```

## Backend code-edit serialization

Code edits during an audit (Phase 4 remediation) are the highest-risk concurrency event. Protocol:

1. team-builder broadcasts "PAUSE" to all validators
2. Validators ACK and stop in-flight work at the next safe checkpoint
3. team-builder applies the edit, rebuilds, restarts backend
4. team-builder polls backend /health until 200
5. team-builder broadcasts "RESUME" with the new commit SHA
6. Validators that were mid-screen re-validate from screen start (state may have changed)

Validators must NOT continue using cached responses from before the edit — the contract may have changed.

## Test data isolation

When multiple validators write to a shared database, they will collide unless test data is isolated.

### Strategy A — unique namespaces per validator

Each validator writes records with a unique prefix:
- team-validator-1 → `audit-v1-*` data
- team-validator-2 → `audit-v2-*` data

Read queries filter by prefix. Cleanup deletes only the validator's own records.

### Strategy B — read-only validations

For audits that don't mutate data (just exercise GETs), no isolation needed.

### Strategy C — fresh database per audit run

For comprehensive audits, spin up a dedicated database container per run, populate from a known seed, tear down at end. Most expensive but cleanest.

## Communication patterns

### Verdict reporting

Each validator writes its verdict to its OWN file, never the shared inventory. The team-builder aggregates at end.

```
e2e-evidence/<run-id>/audit/
  INVENTORY.md         (Phase 1 output, read-only after Phase 1)
  validator-1/         (team-validator-1 writes here)
    verdict.md
    step-NN-*.png
  validator-2/
    verdict.md
  qa-1/                (team-qa writes here)
    verdict.md
    step-NN-*.png
  VERDICT.md           (Phase 5 aggregate, written by team-builder)
```

### Cross-validator broadcasts

When a validator finds a bug that probably affects other validators, it writes a NOTICE file:

```
e2e-evidence/<run-id>/audit/notices/
  notice-001-auth-token-expiry-15min.md
```

Other validators check `notices/` at the start of each new screen / endpoint. If a relevant notice exists, they adjust their expectations.

## Remediation discipline (Phase 4)

The hardest discipline in a parallel audit is NOT to "log and continue." Every FAIL must be fixed before the audit proceeds. This is non-negotiable.

Operational rules:
- No "we'll fix it in the next sprint"
- No "conditionally PASS"
- No "skip this screen"
- Time pressure reduces P2 coverage, NOT remediation rigor
- An audit with unfixed FAILs is incomplete, not finished

## Performance heuristics

| Inventory size | Recommended team size |
|---|---|
| < 5 screens | Just `functional-validation`; full audit is overkill |
| 5–15 screens | 2 validators (one team-qa, one team-validator) |
| 15–40 screens | 3 validators + meta-judge for the inventory |
| 40+ screens | Full template; consider splitting the audit by feature area into sub-runs |

## Coordination failures and recovery

| Failure | Symptom | Recovery |
|---|---|---|
| Simulator lock not released | Validators report "sim busy" or screenshot wrong app | team-builder forces release; restart simulator if needed |
| Backend port conflict | Second backend startup fails | Kill conflicting process; verify port range allocation per validator |
| Database state corruption | Test query returns unexpected data | Roll back to seed; re-run validators that depend on the seed |
| Code-edit-during-audit | Validators report intermittent failures | Pause all, rebuild, broadcast resume |
| Parallel dispatch was actually serial | Audit takes 10× expected time | Verify single-message dispatch; check PreToolUse:Task hook |

## Final aggregation (Phase 5)

The team-builder aggregates per-validator verdicts into a single VERDICT.md:

```markdown
# Audit Verdict — <project> — <timestamp>

## Summary

- Total interactions: 42
- PASS: 39
- FAIL: 0 (all remediated)
- DEFERRED (P2 time-cut): 3

## Per-screen verdicts

| Screen | Interactions | Pass | Fail | Notes |
|---|---|---|---|---|
| HomeView | 5 | 5 | 0 | step-01..05 |
| ... |

## Remediations applied

- R1: Fix orphan POST /agent-queue → POST /queue (commit abc123)
- R2: Increase login timeout from 5s to 10s (commit def456)

## Evidence index

See e2e-evidence/<run-id>/audit/INDEX.md
```

This file feeds `completion-gate` for the outer run verdict.
