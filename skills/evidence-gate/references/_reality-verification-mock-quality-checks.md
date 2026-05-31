# Mock-Quality Checks

> When mocks DO exist in a codebase (e.g., as a legitimate testing pattern), how to verify they aren't lying. Mock-quality scrutiny applied to whatever mocks remain after the no-mocking-validation-gates have done their work.

## When this reference applies

Shannon's default position is no mocks during validation. But mocks legitimately exist in production codebases for:

- Unit tests of pure logic (no I/O involved)
- Third-party services where sandbox mode doesn't exist
- Long-running async work (queue, scheduler) where test acceleration is required
- Hardware-dependent code (sensors, GPIO) where the real hardware isn't in CI

When mocks exist, they need quality scrutiny — because a mock that lies is worse than no test at all.

This reference covers the scrutiny patterns. Pair with `references/goal-detection-patterns.md` for the full reality-verification pass.

## Quality dimensions

A mock's quality has six dimensions:

### 1. Fidelity to real behavior

Does the mock behave like the real thing?

```python
# Real Stripe API behavior:
# - rate-limited (429 on burst)
# - returns specific error shapes
# - takes 100-500ms

# Low-fidelity mock:
def mock_stripe_charge(amount):
    return {"status": "succeeded"}

# High-fidelity mock:
def mock_stripe_charge(amount):
    if simulated_rate_limit_hit():
        return {"status": "error", "code": "rate_limited", "retry_after": 60}, 429
    time.sleep(random.uniform(0.1, 0.5))  # match real latency
    if amount > MAX_ALLOWED:
        return {"status": "error", "code": "amount_too_large"}, 400
    return {"status": "succeeded", "charge_id": fake_uuid()}, 200
```

The high-fidelity mock catches code paths the low-fidelity one hides.

**Check:** does the mock model error cases? Latency? Rate limits? If not, code that depends on those behaviors is untested.

### 2. Coverage of error paths

Real systems fail in ways mocks often don't simulate:

- Network timeout (not connection error — actual hang)
- Partial response (200 status, but body cuts off mid-stream)
- Slow response (200 eventually, but after 30s)
- Authentication revoked mid-request
- Response with invalid schema (200 + malformed body)

Low-quality mocks return either success or a single canned failure. High-quality mocks model the FULL failure distribution.

**Check:** does the test suite exercise each error path the mock can produce? If the mock only returns one error type, the system's response to other error types is untested.

### 3. Schema match

The mock's response shape must match the real system's. If the real Stripe response has 47 fields and the mock has 5, code that reads field 6 fails differently than the mock suggests.

```python
# Real response (truncated):
{
  "id": "ch_abc",
  "amount": 1000,
  "currency": "usd",
  "metadata": {...},
  "outcome": {"network_status": "approved_by_network", ...},
  "payment_method_details": {...},
  ... 40 more fields
}

# Low-fidelity mock:
{"id": "ch_abc", "amount": 1000}
```

Code accessing `response.outcome.network_status` will work in tests (mock returns None which the code silently handles) but fail in prod when the field has a real value the code doesn't handle.

**Check:** sample a recent REAL response. Diff against the mock's response shape. Are all fields present? Are types correct?

### 4. Drift over time

Real systems evolve. APIs add fields, deprecate others, change error codes. Mocks are static — they reflect the API as it was when written.

**Check:** when was the mock last updated? Compare to when the real API was last changed (changelog, version bump, API doc update). Stale mocks are mocks that lie.

A useful discipline: contract-test the mock against a real API snapshot quarterly. Differences = mock drift = a bug waiting to happen.

### 5. Mutation side effects

Real systems persist things. Mocks usually don't — calling `mock_db.insert(...)` doesn't actually mutate any state.

Code that relies on mutation order, idempotency, or state-derived behavior is untested when the mock doesn't persist.

```python
# Real:
db.insert(user)
db.update(user.id, name="new")  # works because user exists

# Low-fidelity mock:
mock_db.insert(user)  # no-op
mock_db.update(user.id, name="new")  # would fail in prod (user doesn't exist)
                                      # but mock says "OK" — false PASS
```

**Check:** does the mock maintain state across calls? If not, multi-call sequences are not actually validated.

### 6. Test-discoverable vs. accidentally-active

A mock should be CLEARLY identifiable as a mock when reading test output. If it isn't, debugging is brutal.

Naming conventions:
- `MockX` / `FakeX` / `StubX` — explicit
- `class StripeClient` overridden to return fakes — ambiguous (looks like real code)

If a test fails on "Stripe returned wrong shape" and you spend an hour debugging Stripe before realizing the test was using a mock the whole time, the mock failed in name-discoverability.

**Check:** can a reviewer reading the test output IMMEDIATELY tell which calls hit mocks vs real systems? If not, naming needs to improve.

## The "mock-was-the-bug" pattern

A specific failure mode that mock-quality checks catch:

```
Real bug: production code mishandles 429 rate limits.

Mock behavior: always returns 200.

Test: passes.

Production: fails when traffic spikes.
```

The mock didn't model the failure mode that caused the production bug. The test would have caught the bug if the mock simulated 429s.

The reality-verification question: "are the mocks teaching the code to handle ONLY the cases the mocks simulate, vs the cases that actually occur?"

## Mock-quality verdict template

```yaml
mock: <name>
real_system: <what it stands in for>

quality:
  fidelity:        HIGH | MEDIUM | LOW  (matches real behavior shape)
  error_coverage:  HIGH | MEDIUM | LOW  (models multiple failure modes)
  schema_match:    HIGH | MEDIUM | LOW  (response fields match)
  staleness:       FRESH | RECENT | STALE  (vs real API changelog)
  state_modeled:   YES | NO              (persists across calls)
  discoverable:    YES | NO              (named so reviewers know it's a mock)

verdict: ACCEPTABLE | NEEDS_IMPROVEMENT | REPLACE_WITH_REAL
```

A mock scoring LOW on 2+ dimensions: replace with real (sandbox / docker / hardware).
A mock scoring LOW on 1 dimension: improve before next release.
A mock scoring HIGH across the board: legitimate, keep, contract-test quarterly.

## When to replace a mock with real

Even if the mock scores HIGH on quality, sometimes replacement is right:

- Real sandbox exists and is reliable → use it (Stripe Test mode, AWS LocalStack)
- Real local instance is fast enough → use it (real Postgres in Docker)
- Mock maintenance cost > integration cost → drop the mock, integrate with real

The default direction is replace-with-real. Mocks are tactical, not strategic.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Single-success-case mock | Tests don't exercise error paths | Model error distribution |
| Stale mock | Doesn't match current real system | Contract-test quarterly |
| Stateless mock for stateful service | Multi-call sequences not validated | Maintain state across calls |
| Indiscernible mock (looks like real) | Debugging is brutal | Name explicitly |
| Mock that always succeeds | False confidence | Model failures explicitly |
| Mock-then-mock-the-mock cascade | Layers of misdirection | Each test should mock at most one boundary |

## Cross-references

- `skills/reality-verification/` — parent skill
- `references/goal-detection-patterns.md` — sibling reference
- `skills/no-mocking-validation-gates/` — addresses cases where the mock shouldn't have existed
- `skills/no-fakes-discipline/` — addresses the philosophical position on mocks
- `skills/functional-validation/` — Iron Rule for validation work
