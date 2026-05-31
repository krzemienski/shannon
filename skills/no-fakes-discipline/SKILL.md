---
name: no-fakes-discipline
description: Active iron-rule enforcement against fake substitutes for the real system. Prevents circumventing validation gates by creating mock/stub implementations. ALWAYS use when the user says "add a fake", "substitute the call", "fixture-based response", "fallback mode", "fake the response", "shim the endpoint", or when intent to bypass real-system validation appears. Detects substitution attempts and injects refusal stderr. Covers mock detection, rationalization patterns, real-system debugging, integration failure diagnosis.
triggers:
  - "add a fake"
  - "substitute the call"
  - "fixture-based response"
  - "fallback mode"
  - "fake the response"
  - "shim the endpoint"
required_hooks:
  - block-fab-files
  - post-action-discipline
---

# No Fakes Discipline

Active enforcement skill. Detects intent to substitute the real system; injects refusal stderr. Codifies Shannon's stricter posture than upstream "no-mocking-validation-gates": **there are no tests in Shannon. No CI-fixture carve-outs. No "just for local development" exception.**

## The Violation This Prevents

When facing integration challenges (timeouts, API issues, CLI problems, slow backends, expensive sandbox accounts), there's a temptation to:

1. Create "mock" or "test" endpoints that return fake data
2. Add "fallback" modes that bypass the real system
3. Rationalize "it's just for testing" or "it's just temporary" when Shannon explicitly forbids substitution
4. Write "fixture" files that hard-code expected responses
5. Add `if (process.env.NODE_ENV === 'test')` guards that branch around the real call

**This is NEVER acceptable in Shannon. The runtime enforces NO mocking, stubs, or placeholder data EVER.**

## Pattern Detection — Rationalizations to Recognize

Watch for these — they all mean the discipline is about to fail:

- "The CLI isn't responding, let me create a mock mode"
- "This will help with testing while we debug"
- "I'll add a fallback that returns realistic data"
- "The infrastructure is working, we just need test data"
- "Just for local development"
- "Just a temporary substitute until the real one comes online"
- "I'll stub this endpoint so the UI work isn't blocked"
- "Let me hardcode the response shape so I can keep building"

**If you catch yourself thinking ANY of these, STOP IMMEDIATELY.** This skill exists for exactly this moment.

## When This Skill Fires

- **PreToolUse:Write attempting to create a forbidden file** → `block-fab-files` hook fires (no-fakes-discipline is the contract this hook enforces). Forbidden patterns: `*.test.*`, `*.spec.*`, `tests/**`, `__tests__/**`, `mocks/**`, `fixtures/**` (as substitute responses, not seed data), `**/test-double*`.
- **User prompt contains substitution intent** → InvocationLayer surfaces this skill BEFORE the assistant writes any code. The assistant must reply with refuse-with-alternative.
- **Edit tool target inserts mock-shaped code** — branching on `NODE_ENV === 'test'`, `if mockMode`, hardcoded JSON literals where a real fetch belongs.

## The Correct Approach

When integration fails:

1. **DIAGNOSE** — why isn't the real system responding?
   - Check the CLI is on PATH
   - Verify API credentials / authentication
   - Check for process conflicts on the port
   - Review error logs
   - Test the network path with `curl -v`

2. **FIX** — address the actual root cause
   - Update PATH environment
   - Fix authentication
   - Resolve process conflicts
   - Debug the actual integration
   - Open the upstream issue if it's not yours to fix

3. **VERIFY** — confirm the real system works
   - Test with actual CLI commands
   - Capture real output
   - Validate end-to-end flow

## Real-System Alternatives (Shannon's substitution table)

| Tempted by | Real-system alternative |
|---|---|
| Substitute HTTP server | Start a real dev server on a free port |
| Substitute the database | Seed local SQLite/Postgres with real data |
| Substitute auth | Real OAuth dev app with test credentials, or a real session cookie |
| Substitute filesystem | A real `/tmp/<run-id>/` directory |
| Substitute API response | Real API call against sandbox tier |
| Substitute a slow upstream | Increase your timeout, OR fix the upstream, OR accept the wall-clock — never fake |
| Substitute an expensive paid API | Real sandbox-tier credentials. If sandbox doesn't exist, that's a real bug to file. |

## Red Flags in Code

**NEVER write code like:**

```swift
// BAD: Mock fallback
if !claudeAvailable {
    return mockResponse()
}

// BAD: Test mode bypass
if input.prompt.hasPrefix("__TEST__") {
    return fakeChatStream()
}

// BAD: "Realistic" fake data
let mockStream = AsyncThrowingStream { continuation in
    continuation.yield(.assistant(fakeMessage))
}
```

**ALWAYS write code like:**

```swift
// GOOD (Swift): Fail clearly when system unavailable
guard await executor.isAvailable() else {
    throw Abort(.serviceUnavailable, reason: "Claude CLI not available")
}

// GOOD (Swift): Use real system
let stream = executor.execute(prompt: input.prompt, ...)
return StreamingService.createSSEResponse(from: stream, on: req)
```

```typescript
// GOOD (TypeScript/Next.js): Fail clearly when system unavailable
const health = await fetch(`${BACKEND_URL}/health`);
if (!health.ok) {
  return NextResponse.json(
    { error: "Backend service unavailable" },
    { status: 503 }
  );
}

// GOOD (TypeScript): Use real system, never mock the SDK
import { query } from "@anthropic-ai/claude-agent-sdk";
delete process.env.CLAUDECODE; // Required in dev to prevent nested session rejection
const result = await query({ prompt, tools });
return NextResponse.json(result);
```

```typescript
// BAD (TypeScript): Mock fallback
const getResponse = async (prompt: string) => {
  if (process.env.NODE_ENV === "test") {
    return { content: "Mock AI response" }; // NEVER DO THIS
  }
  return await query({ prompt });
};

// BAD (TypeScript): Fake data endpoint
app.get("/api/test/sessions", (req, res) => {
  res.json([{ id: "fake-1", title: "Mock Session" }]); // NEVER DO THIS
});
```

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Create a "mock mode" fallback when the real system times out | Hides the real integration bug; mock data passes validation gates that real data would fail | Diagnose the timeout root cause (DNS, auth, process conflicts) and fix the real system |
| Add `if (process.env.NODE_ENV === "test")` guards that return fake data | Test-mode bypasses create two code paths — the mock path is never validated against real behavior | Remove the guard; use the real system in all environments |
| Rationalize "it's just temporary for debugging" | Temporary mocks become permanent; no one removes them once the feature "works" | Log the real error, fix it, and validate with the real system |
| Return hardcoded "realistic" data when an API call fails | Realistic fakes pass visual inspection but mask data-shape mismatches, auth failures, and rate limits | Let the failure propagate with a clear error message so it gets fixed |
| Add a "fixture file" that mirrors the API response shape | Fixtures rot — the moment the real API changes, your fixture lies | Hit the real API; if the rate limit is the issue, fix the rate limit |
| Carve out "just CI fixtures" exception | Anthropic's upstream skill allows this. Shannon does NOT — there are no tests in Shannon | Apply the iron rule uniformly; no CI carve-out |

## Iron Rules

- **No "just temporary" exception.** Temporary means present.
- **No "fallback mode" — fallbacks are substitutes wearing a hat.**
- **No "just for tests" — there are no tests in Shannon.**
- **No "just for CI" — Shannon's runtime is its own CI.**
- **No "edit existing fixture" — if you find one in legacy code, refuse the edit and surface it as a finding** (pre-existing legacy substitutes are out of scope, but extending them is not).

## Shannon Runtime Integration

- **PreToolUse:Write `block-fab-files` hook** — the mechanical refusal layer. Refuses writes to forbidden paths; no override flag.
- **InvocationLayer hint mechanism** — when user prompt contains substitution intent, this skill surfaces BEFORE the assistant writes code.
- **Stricter than upstream:** Shannon overrides `no-mocking-validation-gates`'s "writing actual production feature flags / creating test fixtures for CI pipelines with explicit user approval / building development seed scripts" carve-outs. In Shannon, only seed scripts that load REAL schemas with REAL data and that are clearly outside the runtime path are acceptable, and those are not substitutes.

## When NOT to Use

- Edit to existing legacy code containing pre-existing substitute patterns — Shannon's iron rules forbid CREATING new substitutes; pre-existing ones in legacy code are out of scope for this session (surface them as findings instead).
- Writing actual production feature flags (real on/off switches for real features, not mock bypasses).
- Development seed scripts that load REAL data into REAL schemas and are explicitly outside the runtime path.

## Conflicts

- `functional-validation` — Complementary. functional-validation provides the real-system validation protocol; this skill prevents substitution attempts that would short-circuit it.
- `e2e-validate` — Complementary. Both enforce real-system execution.
- `no-mocking-validation-gates` (upstream) — Shannon does NOT adopt this as a separate skill. This Shannon skill subsumes it under a stricter posture per v7 Conflict 2 resolution.

## Related Skills

- `functional-validation` — the protocol this skill protects from substitution
- `evidence-gate` — gate that would refuse a substituted system as missing evidence
- `completion-gate` — outer mechanical gate that catches substitutions at Phase 10
- `refusal-discipline` — emits `REFUSAL.md` when a substitution attempt blocks completion
- `verification-before-completion` — lightweight per-claim check that catches "I'm done" claims backed by substitutes

## The Bottom Line

**If the real system doesn't work, FIX THE REAL SYSTEM.**

Creating mock implementations:
- Violates the validation methodology
- Hides real bugs
- Creates false confidence
- Wastes time on throw-away code
- Breaks trust with the user

The validation gate exists precisely to ensure real functionality. Circumventing it defeats the entire purpose.


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `no-mocking-validation-gates`

# No Mocking Validation Gates

In Shannon, this discipline is owned by `no-fakes-discipline` — Shannon's
stricter merged form of the upstream skill. This file exists as a
discoverability pointer so that anyone reaching for the upstream-named skill
lands in the right place, and as a self-contained fallback when
`no-fakes-discipline` is not loaded.

**For Shannon runs, prefer `no-fakes-discipline`.** It is functionally a
superset of this skill with a stricter posture (no CI-fixture carve-out, no
"just for tests" exception — there are no tests in Shannon).

The content below is preserved verbatim so the patterns are usable as a
standalone fallback.

## The Violation This Prevents

When facing integration challenges (timeouts, API issues, CLI problems), there's a temptation to:
1. Create "mock" or "test" endpoints that return fake data
2. Add "fallback" modes that bypass the real system
3. Rationalize "it's just for testing" when the plan explicitly forbids mocking

**This is NEVER acceptable when the project specifies "NO mocking, stubs, or placeholder data EVER".**

## The Pattern to Recognize

Watch for these rationalizations:
- "The CLI isn't responding, let me create a mock mode"
- "This will help with testing while we debug"
- "I'll add a fallback that returns realistic data"
- "The infrastructure is working, we just need test data"

**If you catch yourself creating ANY of these, STOP IMMEDIATELY.**

## The Correct Approach

When integration fails:

1. **DIAGNOSE** - Why isn't the real system responding?
   - Check if the CLI is in PATH
   - Verify API credentials/authentication
   - Check for process conflicts
   - Review error logs

2. **FIX** - Address the actual root cause
   - Update PATH environment
   - Fix authentication
   - Resolve process conflicts
   - Debug the actual integration

3. **VERIFY** - Confirm the real system works
   - Test with actual CLI commands
   - Capture real output
   - Validate end-to-end flow

## Red Flags in Code

**NEVER write code like:**
```swift
// BAD: Mock fallback
if !claudeAvailable {
    return mockResponse()
}

// BAD: Test mode bypass
if input.prompt.hasPrefix("__TEST__") {
    return fakeChatStream()
}

// BAD: "Realistic" fake data
let mockStream = AsyncThrowingStream { continuation in
    continuation.yield(.assistant(fakeMessage))
}
```

**ALWAYS write code like:**
```swift
// GOOD (Swift): Fail clearly when system unavailable
guard await executor.isAvailable() else {
    throw Abort(.serviceUnavailable, reason: "Claude CLI not available")
}

// GOOD (Swift): Use real system
let stream = executor.execute(prompt: input.prompt, ...)
return StreamingService.createSSEResponse(from: stream, on: req)
```

```typescript
// GOOD (TypeScript/Next.js): Fail clearly when system unavailable
const health = await fetch(`${BACKEND_URL}/health`);
if (!health.ok) {
  return NextResponse.json(
    { error: "Backend service unavailable" },
    { status: 503 }
  );
}

// GOOD (TypeScript): Use real system, never mock the SDK
import { query } from "@anthropic-ai/claude-agent-sdk";
delete process.env.CLAUDECODE; // Required in dev to prevent nested session rejection
const result = await query({ prompt, tools });
return NextResponse.json(result);
```

```typescript
// BAD (TypeScript): Mock fallback
const getResponse = async (prompt: string) => {
  if (process.env.NODE_ENV === "test") {
    return { content: "Mock AI response" }; // NEVER DO THIS
  }
  return await query({ prompt });
};

// BAD (TypeScript): Fake data endpoint
app.get("/api/test/sessions", (req, res) => {
  res.json([{ id: "fake-1", title: "Mock Session" }]); // NEVER DO THIS
});
```

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Create a "mock mode" fallback when the real system times out | Hides the real integration bug; mock data passes validation gates that real data would fail | Diagnose the timeout root cause (DNS, auth, process conflicts) and fix the real system |
| Add `if (process.env.NODE_ENV === "test")` guards that return fake data | Test-mode bypasses create two code paths — the mock path is never validated against real behavior | Remove the guard; use the real system in all environments |
| Rationalize "it's just temporary for debugging" | Temporary mocks become permanent; no one removes them once the feature "works" | Log the real error, fix it, and validate with the real system |
| Return hardcoded "realistic" data when an API call fails | Realistic fakes pass visual inspection but mask data-shape mismatches, auth failures, and rate limits | Let the failure propagate with a clear error message so it gets fixed |

## Related Skills

- `no-fakes-discipline` — Shannon's stricter merged form (PREFERRED in Shannon)
- `functional-validation` — Full validation protocol (philosophy + platform routing)
- `e2e-validate` — Execution engine with workflows, scripts, and templates
- `evidence-gate` — Shannon's per-claim evidence-based completion verification
- `gate-validation-discipline` — discoverability pointer to evidence-gate / completion-gate
- `verification-before-completion` — Pre-completion behavioral checks

## When NOT to Use

- Writing actual production feature flags (not mock bypasses)
- Creating test fixtures for CI pipelines with explicit user approval (NOTE: Shannon does NOT honor this carve-out — see `no-fakes-discipline` for the stricter Shannon stance)
- Building development seed scripts that clearly label data as synthetic
- When `no-fakes-discipline` is loaded (use it instead — it subsumes this skill with stricter rules)

## Conflicts

- `no-fakes-discipline` — Shannon's stricter merged form. Shannon's v7 Conflict 2 resolution merges this skill INTO `no-fakes-discipline`. Use `no-fakes-discipline` as the authoritative Shannon discipline; this skill is a discoverability pointer + standalone fallback.
- `functional-validation`: Complementary — this skill prevents mocking, functional-validation provides the real validation protocol
- `e2e-validate`: Complementary — both enforce real-system testing

## The Bottom Line

**If the real system doesn't work, FIX THE REAL SYSTEM.**

Creating mock implementations:
- Violates the validation methodology
- Hides real bugs
- Creates false confidence
- Wastes time on throw-away code
- Breaks trust with the user

The validation gate exists precisely to ensure real functionality. Circumventing it defeats the entire purpose.
