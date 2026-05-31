# Interview Examples

> Worked examples of the 3-phase interview algorithm applied to real prompts. Use these as exemplars when running interviews.

## Example 1 — A clear feature request

**User input:**
> Add JWT authentication to the API using jose, with httpOnly cookies. Refresh rotation per OWASP. Don't touch the user model.

**Phase 1 — Understand**

Everything is in the input. No questions needed. Inferred structure:

```yaml
intent:
  noun: "feature"
  short_name: "JWT auth"
  goal: "Add JWT-based auth to the API"
  scope:
    in: ["API endpoints", "auth middleware", "cookie handling"]
    out: ["user model schema"]
  constraints:
    must:
      - "Use jose library"
      - "httpOnly cookies (no client-side token storage)"
      - "Refresh rotation per OWASP"
      - "Don't touch user model"
  deferred: []
```

**Phase 2 — Propose**

3 approaches:

```
Approach A: All-at-once
  - Replace session auth on all endpoints in one PR
  - Pros: Simple, no dual-mode
  - Cons: Higher risk; one PR to roll back
  - Recommended: NO (risk)

Approach B: Phased per-endpoint group (RECOMMENDED)
  - Migrate auth endpoints first, then mutation endpoints, then read endpoints
  - Pros: Each phase reversible independently
  - Cons: 3 PRs instead of 1
  - Recommended: YES

Approach C: Long-term dual-mode
  - Keep session auth, add JWT alongside, switch by feature flag
  - Pros: Easy rollback
  - Cons: Adds complexity that lives forever
  - Recommended: NO (technical debt)
```

User picks B.

**Phase 3 — Store**

Write to `.planning/intake/jwt-auth-intake.md` with approach B + all constraints.

---

## Example 2 — A vague request that needs Phase 1 questions

**User input:**
> Clean up the user system.

**Phase 1 — Understand**

Almost nothing in the input. Ask 3 questions:

```
1. What specifically about the user system feels "unclean"?
   (Bug? Tech debt? Confusing API? Slow queries?)
2. What's the smallest version of done — full rewrite, or targeted fix?
3. Any module or pattern you definitely want me to preserve?
```

User responds:
> The login flow has 4 different code paths that do similar things. I want to consolidate them. Don't change the database schema.

Now Phase 1 can proceed:

```yaml
intent:
  noun: "refactor"
  short_name: "consolidate login flow"
  goal: "Reduce the 4 login code paths to a single canonical implementation"
  scope:
    in: ["login flow code", "auth middleware"]
    out: ["database schema", "user model"]
  constraints:
    must: ["No DB schema changes"]
    prefer: ["Single canonical login path"]
  deferred: ["Which of the 4 paths is the canonical one — propose"]
```

**Phase 2 — Propose**

```
Approach A: Pick one path, replace others (RECOMMENDED if one is genuinely canonical)
  - Identify the cleanest existing path; refactor others to call it
  - Pros: Minimal new code
  - Cons: Inherits whatever issues the chosen path has

Approach B: Write a new canonical path, replace all 4
  - Greenfield the canonical login handler; route all 4 to it
  - Pros: Fresh slate, no inherited issues
  - Cons: New code introduces new bugs

Approach C: Merge incrementally (path 1 + 2 first, then 3, then 4)
  - 3 separate consolidations, each small
  - Pros: Each step shippable
  - Cons: 3 PRs, slower
```

Ask user which one. They pick C.

**Phase 3 — Store**

Write `.planning/intake/login-consolidation-intake.md`.

---

## Example 3 — Conflict in user intent

**User input:**
> Make the API faster. Use whatever caching tech we want. Must be backwards compatible.

**Phase 1 — Understand**

Inferred goal: improve API latency. Constraint inferred: don't change response shape.

But: "Whatever caching tech we want" + "must be backwards compatible" can conflict — e.g., adding a Redis cache layer requires deployment changes that arguably break "backwards compatible" if interpreted strictly.

Question to ask:

```
"Backwards compatible" can mean: (a) response shapes unchanged, (b) no
deployment/infra changes, (c) both. Which do you mean?
```

User clarifies: "response shapes only — infra changes are fine."

Now Phase 1 proceeds:

```yaml
intent:
  noun: "performance"
  short_name: "API latency improvement"
  goal: "Reduce p99 API latency"
  scope:
    in: ["API responses", "caching layer", "DB queries", "infra"]
    out: ["response shape changes"]
  constraints:
    must: ["Response shapes unchanged"]
    prefer: ["Open-source caching tech"]
    forbid: ["Changes that break API client consumers"]
  deferred: ["Specific caching tech — propose 2-3"]
```

**Phase 2 — Propose**

3 caching options:

```
Approach A: Redis (read-through cache)
Approach B: Local in-memory (Caffeine-style)
Approach C: CDN edge cache for read endpoints
```

User picks A.

**Phase 3 — Store**

Write intake.md.

---

## Example 4 — A research request

**User input:**
> Research how other teams handle SSO at scale.

**Phase 1 — Understand**

Few constraints. Need to clarify scope.

```
"At scale" — what's our scale roughly? 1k users? 100k? 1M+?
"Other teams" — any particular industry / stack you want to learn from?
Output format — written report, decision matrix, or a slide deck?
```

User: "100k users, SaaS like ours, written report with a comparison table."

```yaml
intent:
  noun: "research"
  short_name: "SSO patterns at scale"
  goal: "Survey SSO approaches used by 100k-user SaaS companies; produce a written report with comparison table"
  scope:
    in: ["SSO providers", "session management", "auth federation", "user provisioning"]
    out: ["non-SaaS contexts", "<10k or >10M user scale"]
  constraints:
    must: ["Written report", "Comparison table"]
    prefer: ["At least 5 reference companies"]
  deferred: []
```

**Phase 2 — Propose**

For research, "approaches" means research methodology, not solution choice:

```
A: Survey published architecture posts + comparison
B: Case studies (3-5 deep dives) + cross-cutting synthesis
C: Vendor analysis (Okta vs Auth0 vs Cognito vs custom)
```

User picks B.

**Phase 3 — Store**

`.planning/intake/sso-research-intake.md`.

---

## Example 5 — Skipping the interview

Not every request needs an interview. Skip when:

- The user already wrote a structured spec (intent + approach + constraints all explicit)
- The task is trivial (`fix typo in README.md`)
- The request is a continuation of established context (`add another field to that schema`)

If you'd be asking zero questions and proposing zero alternatives because everything's clear, the interview is overhead. Skip to planning.

---

## Anti-patterns from real interviews

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Asking 8 questions for a clear request | User annoyance: "I told you everything" | Ask only what input doesn't answer |
| Proposing 5 approaches | User decision fatigue | 2-3 approaches max |
| No approach marked "recommended" | User has to choose blind | Always recommend one, name reasons |
| Phase 3 storage skipped | Intent lost on context drop | Always write intake.md |
| Intake.md without approach choice | Successor agent doesn't know what to plan | Always include the chosen approach |

## Cross-references

- `references/algorithm.md` — the 3-phase algorithm in detail
- `skills/interview-framework/` — parent skill
- `skills/plan-author/` — what comes after the interview
- `skills/spec-workflow/` — alternate consumer of intake.md
