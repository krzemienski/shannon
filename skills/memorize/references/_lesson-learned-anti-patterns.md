# Engineering Anti-Patterns

> The recurring failure shapes that show up across enough sessions to deserve a name. lesson-learned mines git history and session transcripts for these; this reference is the catalog.

## How to use this reference

When reflecting on a session or a commit range:
1. Scan for patterns from the catalog below
2. For each match, write a lesson in the form: `Pattern X observed at <location>. Remedy: <Y>.`
3. Cap at 1-2 lessons per reflection cycle (dominant-gap discipline)

If no pattern from the catalog fits, the issue might be a novel one — add it to the catalog AFTER it shows up in 2+ sessions.

## Catalog

### AP-01: Symptom-fix-without-root-cause

The reported issue's surface symptom got patched; the underlying cause is untouched.

**Sign:** Same class of bug reappears in a different place within weeks.

**Remedy:** Run `skills/root-cause-tracing/` before fixing. Document the trace in the commit message so future maintainers can verify the cause was reached.

### AP-02: Refactor-and-feature-in-one-commit

Behavior change AND structural change bundled. When the commit later needs to be reverted, both go.

**Sign:** Commit message includes "+ refactor" or "and cleanup."

**Remedy:** Atomic commits — one logical change per commit. Refactors land BEFORE the feature, separately.

### AP-03: Type-system-bypassed

`any` / `unknown` / `cast<>` / `# type: ignore` used to silence the type checker instead of fixing the underlying mismatch.

**Sign:** New occurrences of these escape hatches in the diff.

**Remedy:** When tempted to bypass the type system, treat the bypass as a finding. Track it. The bypassed line is usually where the next bug lands.

### AP-04: God function / God file

Single function or file grew beyond ~300 lines / ~7 responsibilities.

**Sign:** New code lands inside an already-large function. File length growth in unrelated PRs.

**Remedy:** Decompose BEFORE adding to the god surface. Apply the single-responsibility heuristic.

### AP-05: Premature abstraction

Abstraction layer introduced for a single use case that may never have a second.

**Sign:** Interface with one implementation. Generic name with concrete-only behavior. Plugin architecture with one plugin.

**Remedy:** Wait for the third use case (Rule of Three). Two cases can usually be coordinated explicitly without an abstraction.

### AP-06: Mock-then-forget

A mock was introduced for a temporary reason; the temporary reason ended; the mock remains.

**Sign:** Mock-related code in production paths. Long-lived `if MOCK_MODE: ...` branches.

**Remedy:** Delete mocks aggressively. If a mock is needed long-term, it gets a quality bar (see `skills/reality-verification/references/mock-quality-checks.md`).

### AP-07: Test-the-implementation-not-the-behavior

Tests assert internal call sequences instead of observable behavior. Refactoring breaks tests despite behavior being preserved.

**Sign:** Tests heavy on `assertCalled` / spies / `expect(mock).toHaveBeenCalledWith(...)`.

**Remedy:** Test the input/output relationship, not the implementation. Refactor-safe tests stay green on internal restructuring.

### AP-08: Premature optimization

Code restructured for performance before profiling identified it as the bottleneck.

**Sign:** Comments like "// optimized for speed." Manual memoization in unhot paths. Hand-rolled SIMD when stdlib was fast enough.

**Remedy:** Profile first. Optimize only what shows up in the profile. Document the BEFORE/AFTER measurement.

### AP-09: Distributed deadlock by mutex order

Two services / threads acquire two resources in different orders, leading to deadlock under load.

**Sign:** Production incidents under traffic spike. "Worked in dev" / "passes tests."

**Remedy:** Establish a global lock-acquisition order. Document it. Static-analyze for violations.

### AP-10: Silent failure

`try: ... except: pass` (or equivalent). Errors disappear; debugging future failures is brutal because the trail is severed.

**Sign:** Bare excepts in the diff. Empty error handlers. Errors logged to /dev/null.

**Remedy:** Never swallow silently. At minimum, log with full context. Better: surface the error to a place that gets attention (alerting, dashboard).

### AP-11: Time-based test

Test relies on `sleep()` / wall-clock comparisons to coordinate async work. Flaky under load.

**Sign:** `time.sleep(0.1)` in tests. `setTimeout(check, 100)`. "Sometimes fails, retry."

**Remedy:** Use event-based synchronization. Wait for a signal, not a duration. If the test framework doesn't support events, fix the framework.

### AP-12: Singleton-everywhere

Global state accessed from many places. Tests interfere with each other. Order of test runs matters.

**Sign:** `getInstance()` / `MyClass._instance` patterns. Tests must run in a specific order.

**Remedy:** Pass dependencies explicitly. Singletons are sometimes necessary (loggers, config) but should be the exception, not the default.

### AP-13: Config-as-code-without-validation

Config files (YAML, JSON, env vars) consumed without schema validation. Typos / missing fields cause runtime errors.

**Sign:** `config["api_key"]` style reads with no upfront validation.

**Remedy:** Validate config at load time against a schema (Pydantic, Zod, etc.). Crash early with a clear message, not late with a confusing one.

### AP-14: Branch-rot

Long-lived feature branch that diverges from main, becomes painful to merge.

**Sign:** Branch is months old. Author "needs to refresh from main" repeatedly. Conflicts pile up.

**Remedy:** Aggressive branch hygiene: short-lived branches (days, not weeks). Frequent merges or rebases. Feature flags instead of long branches.

### AP-15: Documentation-debt

Significant decisions made in chat / Slack / a meeting; never written down. New maintainer can't reconstruct the reasoning.

**Sign:** "Why is this code this way?" with no traceable answer.

**Remedy:** Decision records (ADR-style). One per significant decision. Lives in the repo, not in chat.

### AP-16: Test-on-CI-only-machine

Tests pass on CI but fail locally (or vice versa). Difference is unaccounted for.

**Sign:** "Works on my machine" or "Works on CI." Environment-specific assertions.

**Remedy:** Standardize the test environment. Docker for tests. CI runs the same containers locals do.

### AP-17: Catch-all-then-rethrow

`try: do_thing(); except Exception as e: raise Exception(f"Error: {e}")` — the wrapper hides the original exception type and traceback.

**Sign:** Generic `Exception` / `Error` re-raises losing the original type.

**Remedy:** Either let it propagate untouched, or wrap with `raise X from e` (Python) / `throw new X({cause: e})` (JS).

### AP-18: Magic constants without names

Numbers / strings appearing in code without names explaining their meaning.

**Sign:** `if x > 30: ...` with no comment explaining why 30. `factor = 2.7818`.

**Remedy:** Named constants with docstrings. The name documents intent; the value documents the calibration.

### AP-19: Tests-as-documentation

The only place a feature's expected behavior is documented is the test file. Test reads like a spec.

**Sign:** PR review comment: "What's this supposed to do?" — answer: "Read the test."

**Remedy:** Tests verify; docs describe. Both. A test-as-spec rots when the test stops being trusted (flaky, skipped, etc.).

### AP-20: Premature retire

A piece of code marked "deprecated" / "to be removed" but still actively used. Confusion about which path to follow.

**Sign:** "Deprecated" warnings in code that's still imported in 47 places. Replacement doesn't exist yet.

**Remedy:** Don't mark deprecated until the replacement is ready AND the migration plan is written. "We should remove this someday" isn't deprecation, it's wishful thinking.

## Catalog usage in lesson-learned

```yaml
lesson:
  pattern: AP-10  # Silent failure
  observed_at: "commit a3f4b9c, line 142 of session_manager.py"
  context: "added try/except to suppress a database connection error"
  remedy: "log + alert; don't suppress. Surface the connection issue."
  applicability: "every code path that wraps a network or DB call"
```

The remedy field is the actionable output. Without it, the lesson is just an observation.

## Cross-references

- `skills/lesson-learned/` — parent skill
- `references/se-principles.md` — sibling reference (the positive principles vs these anti-patterns)
- `skills/reflect/` — uses this catalog to produce per-session lessons
- `skills/reflect/references/gap-taxonomy.md` — process-level gaps (vs code-level anti-patterns here)
- `skills/root-cause-tracing/` — addresses AP-01 specifically
