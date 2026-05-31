# Software Engineering Principles

> The positive counterparts to `references/anti-patterns.md`. The principles that, applied consistently, prevent the anti-patterns from happening.

## Why principles vs rules

Rules are specific ("never use `any` in TypeScript"). Principles are general ("respect the type system"). Rules apply mechanically; principles require judgment.

Principles age better than rules. The rule "no `var` in JavaScript" was hot in 2015; it's now baseline. The principle "prefer immutable bindings" lives on.

This catalog is principles. Use it to derive rules for your specific context.

## Catalog

### SE-01: Single Responsibility (SRP)

A unit of code (function, class, module) has ONE reason to change.

**Operational meaning:** if you can describe a function's purpose using "and" / "also" — `parses input AND validates AND saves to db` — it's doing too much. Split.

**Effect:** changes localize. A change to validation doesn't risk breaking parsing.

### SE-02: Composition over inheritance

Build complex behavior by combining simple pieces, not by extending hierarchies.

**Operational meaning:** if you're 3 levels deep in a class hierarchy, you've usually overpaid for the indirection. Strategies / composition / dependency injection accomplish the same goals with less surface area.

**Effect:** rewriting one component doesn't ripple through descendants.

### SE-03: Make impossible states impossible

Use types to encode invariants. If a state shouldn't exist, the type system should refuse to construct it.

```typescript
// Bad:
type User = { name: string; email: string; verified: boolean; verifiedAt: Date }
// "verified: true, verifiedAt: undefined" is constructible — but shouldn't be

// Good:
type User = { name: string; email: string } & 
  ({ verified: false } | { verified: true; verifiedAt: Date })
// Now the invariant is type-enforced
```

**Effect:** entire bug classes disappear because they can't be expressed.

### SE-04: Fail fast, fail loud

When the system reaches an unexpected state, crash with maximum diagnostic information. Don't try to recover into an undefined behavior.

**Operational meaning:** `assert`, `panic`, `raise`, `throw` early. The further from the root cause an error surfaces, the harder it is to debug.

**Effect:** crashes happen in dev; production gets the diagnostics that prevent the crash from recurring.

### SE-05: Iron Rule of validation

Validate through the same interfaces real users use. Never validate against mocks.

**Operational meaning:** if you're writing a unit test that passes a mock to the function under test, you're testing the mock, not the function.

**Effect:** validation results predict production behavior, instead of merely correlating with it.

### SE-06: Boring tech for boring problems

Most problems are solved by mature, well-understood tools. Reach for novelty only when novelty pays for itself.

**Operational meaning:** Postgres over the new graph DB. JSON over the new binary format. Express over the new framework. Unless you have a specific need the boring choice can't satisfy.

**Effect:** team velocity is high because the tools are predictable. Bug surface is small because edge cases are well-documented.

### SE-07: YAGNI (You Aren't Gonna Need It)

Don't build flexibility for use cases that don't exist yet.

**Operational meaning:** when adding a parameter "in case we need it later" — don't. When designing a plugin system "for future extensibility" — don't. Build for the actual use cases.

**Effect:** smaller surface area. Less code to maintain. Easier to refactor when the actual need emerges.

### SE-08: DRY (Don't Repeat Yourself) — but with judgment

Repetition is bad when the duplicated pieces would change together. Repetition is FINE when the pieces happen to look similar but evolve independently.

**Operational meaning:** before abstracting two similar pieces, ask "if requirement X changes, would both need to change?" If yes → DRY them. If no → leave them.

**Effect:** prevents premature abstraction. Avoids forced-coupling where independence was healthier.

### SE-09: Make it work, make it right, make it fast — in that order

First: working but ugly. Then: refactor to clean. Then: profile and optimize hot paths.

**Operational meaning:** don't optimize before it works. Don't refactor before it works. Don't optimize before you've profiled.

**Effect:** time spent improving is spent on things that matter.

### SE-10: Explicit > implicit

When two solutions tie in other dimensions, prefer the one that's explicit about what it does.

**Operational meaning:** import all dependencies explicitly. Pass arguments instead of relying on globals. State what's being mutated. Use named parameters when call-site clarity matters.

**Effect:** code reads like it works.

### SE-11: Locality of behavior

Code that changes together should live together. When you read one piece, you should be able to predict what changes when.

**Operational meaning:** prefer collocation over separation. The Tailwind-style "utility classes next to elements" is one expression of this. The Rails-style "view, controller, model in different directories" sometimes violates it.

**Effect:** changes are local. Reading a feature doesn't require jumping across 12 files.

### SE-12: Reversibility

Decisions that are easy to reverse can be made fast. Decisions that are hard to reverse deserve careful consideration.

**Operational meaning:** schema migrations, infrastructure choices, public API shapes — these are hard to reverse. Refactoring internals, picking a library version, adopting a library — these are easy to reverse.

Apply more rigor to the hard-to-reverse decisions.

**Effect:** velocity stays high for tactical work; strategic work gets the consideration it deserves.

### SE-13: Operate on what you have, not what you wish you had

When the codebase isn't ideal, you have two choices: improve it OR work around it. The trap is wishing it were different and acting as if it were.

**Operational meaning:** if the existing pattern is messy, either fix it (and own that work) or live with it (and write code that fits it). Don't half-fix it and leave both patterns active.

**Effect:** consistent codebase. No "old way" + "new way" warzones.

### SE-14: Boring deployments

Deployments should be unremarkable. They should run from a button, finish predictably, and roll back cleanly.

**Operational meaning:** invest in deployment tooling. Run it every day. Make it boring through repetition.

**Effect:** small changes ship continuously. Large changes break into small changes. Outages from deployments approach zero.

### SE-15: The boy scout rule (with bounds)

Leave the code slightly better than you found it.

**Operational meaning:** while passing through unfamiliar code, fix the small thing — a typo in a comment, a deprecated import, an obvious bug. But: don't scope-creep your PR with unrelated cleanup. Surgical improvements only.

**Effect:** codebase decay reverses over time.

### SE-16: Documentation is part of the code

Code that's hard to understand is not done. Documentation in docstrings, README, ADR — wherever it lives, it's part of the deliverable.

**Operational meaning:** PR review includes documentation review. A working feature without docs is a half-shipped feature.

**Effect:** the next maintainer (or future-you) doesn't waste hours reconstructing intent.

### SE-17: Tests document expected behavior

Tests are the executable spec. When a test breaks, EITHER the behavior changed (and the test correctly caught it) OR the test was wrong.

**Operational meaning:** never edit a test to make it pass without first understanding why it failed. The pattern "test failed → I'll update the assertion" is a SE-17 violation.

**Effect:** the test suite stays trustworthy.

### SE-18: Trace the causal chain

When debugging, follow the causal chain back to the root, not to the first plausible culprit.

**Operational meaning:** "I changed X and it works now" — but do you know WHY X mattered? If not, the next manifestation of the same root cause is still ahead.

**Effect:** bug recurrence drops. Confidence in fixes is high because the fix is mechanistically justified.

### SE-19: Empathy for future maintainers

Most code is read more often than it's written. Optimize for the reader.

**Operational meaning:** clarity over cleverness. Names that describe intent. Comments that explain WHY (not WHAT). Tests that show intended usage.

**Effect:** onboarding is faster. Bus factor is higher.

### SE-20: When the rule conflicts with the principle, the principle wins

Rules are derived from principles for a context. When the context changes, rules become wrong. Principles age better.

**Operational meaning:** if your team's "no `var`" rule conflicts with a JS engine that requires `var` for closure semantics in some edge case — the rule is wrong, not the engine.

**Effect:** rules stay healthy. Stale rules get retired.

## Catalog usage in lesson-learned

```yaml
lesson:
  principle: SE-04  # Fail fast, fail loud
  observed_at: "commit f9c1d2e, session 2026-05-27"
  context: "added try/except to swallow rare auth failures"
  guidance: "These failures should propagate. The current code hides production
            issues. Refactor to alert + crash with diagnostic, not silently retry."
```

Cross-reference to the matching anti-pattern from `references/anti-patterns.md` is useful — every principle has a corresponding violation.

## Cross-references

- `skills/lesson-learned/` — parent skill
- `references/anti-patterns.md` — sibling reference (the negative space of these principles)
- `skills/reflect/` — uses this catalog when producing lessons
- `skills/spec-workflow/`, `skills/plan-author/` — apply principles at the spec / plan phase
