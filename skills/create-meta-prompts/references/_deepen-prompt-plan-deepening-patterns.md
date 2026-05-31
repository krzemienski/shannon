# Deepening Patterns

This reference is loaded by Phase 4 (Inject or Strengthen Validation) and Phase 5 (Synthesize and Rewrite) of `deepen-prompt-plan`. It supplies the concrete XML templates, validation-gate patterns, and before/after rewrite examples that the deepening pass applies.

## Mock-detection preamble

Inject at the TOP of any document that describes work to be built and executed.

```xml
<mock_detection_protocol>
Before executing any task in this document, check intent:
- Tempted to create *.test.*, *_test.*, *Tests.*, test_* files: STOP
- Tempted to import mock libraries (nock, jest.mock, msw, responses, URLProtocol): STOP
- Tempted to use in-memory database (SQLite :memory:, H2): STOP
- Tempted to add TEST_MODE, NODE_ENV=test, --mock flags: STOP

Fix the REAL system instead. There is one mode: the mode users experience.
No exceptions. Iron Rule applies.
</mock_detection_protocol>
```

If the document is a prompt rather than a plan, place the protocol after the role/identity section and before the workflows.

## Validation-gate template

Inject one gate per task or per logical unit of work. Each gate is BLOCKING — execution cannot proceed past a FAILed gate without fixing the real system.

```xml
<validation_gate id="VG-{N}" blocking="true">
  <prerequisites>
    [What must be running and healthy BEFORE the gate executes]
    Example: "Backend on :3000 returns 200 from /health; database has migrations applied"
  </prerequisites>
  <execute>
    [The real-system interaction — curl, screenshot, CLI invocation, etc.]
    Example: "curl -fsS -X POST http://localhost:3000/api/users -d '...' "
  </execute>
  <capture>
    [Command(s) that save output to evidence/ under e2e-evidence convention]
    Example: "tee e2e-evidence/<run-id>/journey/step-NN-create.body.json"
  </capture>
  <pass_criteria>
    [SPECIFIC, OBSERVABLE, MEASURABLE — defined NOW, not during execution]
    Example: "HTTP 201 status, body contains non-null `id` field, side-effect row visible in users table"
  </pass_criteria>
  <review>
    [Explicit step where the operator READS the captured evidence]
    Example: "Read tool on response.body.json; jq .id to confirm; psql query to verify DB row"
  </review>
  <verdict>
    PASS: cite each evidence file + line range that proves the criteria met; advance to next gate
    FAIL: write the failure mode; fix the REAL system; re-run from <prerequisites>
  </verdict>
  <mock_guard>
    If tempted to mock anything to make this gate pass: STOP. Fix the system instead.
  </mock_guard>
</validation_gate>
```

## Gate manifest

Append at the end of any document with validation gates.

```xml
<gate_manifest>
  <total_gates>{N}</total_gates>
  <sequence>VG-1 → VG-2 → ... → VG-N</sequence>
  <policy>All gates BLOCKING. No advancement on FAIL.</policy>
  <evidence_dir>e2e-evidence/&lt;run-id&gt;/</evidence_dir>
  <regression>
    If ANY gate FAILS during a run, fix the system AND re-run from the failed gate.
    Do NOT skip. Do NOT mark "partial PASS". Re-run fully.
  </regression>
  <final_gate>evidence-gate (6-question refusal-discipline) BEFORE marking complete.</final_gate>
</gate_manifest>
```

## Decision rewrite pattern

Weak decision before deepening:

> We will use JWT for authentication.

After deepening:

```xml
<decision id="D1">
  <statement>Use JWT access tokens (15-minute expiry) with refresh-token rotation.</statement>
  <rationale>
    OWASP Session Management Cheat Sheet (2024-01) recommends short-lived access tokens
    with refresh rotation for stateless APIs. The existing codebase already exposes
    `AuthProvider` protocol (src/auth/AuthManager.swift:1-80) which expects token-based
    auth, so JWT slots in without invasive refactor.
  </rationale>
  <alternatives_considered>
    <alternative name="session cookies">
      Rejected because the API is consumed by both web and native clients; cookies are
      problematic for native and require CSRF mitigation we don't currently have.
    </alternative>
    <alternative name="long-lived JWT (24h)">
      Rejected on OWASP guidance — long-lived tokens cannot be revoked without a
      blacklist, which defeats the stateless property.
    </alternative>
  </alternatives_considered>
  <sources>
    <source>OWASP Session Management Cheat Sheet (2024-01)</source>
    <source>codebase: src/auth/AuthManager.swift:1-80</source>
  </sources>
</decision>
```

## Risk rewrite pattern

Weak risk before deepening:

> Risk: tokens could be stolen.

After deepening:

```xml
<risk id="R3" severity="high" likelihood="medium">
  <description>
    Access token exfiltration via logs or telemetry. A leaked token grants
    full access for up to 15 minutes.
  </description>
  <mitigations>
    <mitigation>
      Logger middleware (src/middleware/logger.ts:23) already redacts the
      `authorization` header. Add the same redaction for any custom auth headers.
    </mitigation>
    <mitigation>
      Refresh tokens are HttpOnly cookies, not accessible to JS — limits the
      blast radius of an XSS to one access token.
    </mitigation>
    <mitigation>
      Add monitoring on 401 response rate; sudden spikes indicate possible
      token testing.
    </mitigation>
  </mitigations>
  <residual_risk>
    A user on a compromised device remains vulnerable for the access-token
    lifetime. This is the explicit security trade-off; documented and accepted.
  </residual_risk>
</risk>
```

## Task rewrite pattern

Weak task before deepening:

> Task 3: Build the login endpoint.

After deepening:

```xml
<task id="T3" depends_on="T2" platform="node">
  <description>
    Add POST /api/auth/login endpoint that issues a JWT access token + refresh
    cookie on valid credentials.
  </description>
  <files>
    - src/routes/auth.ts (new)
    - src/services/authService.ts (new)
    - tests/ — NONE. No test files. Iron Rule.
  </files>
  <approach>
    Conform to the existing AuthProvider pattern. Use bcrypt for password
    verification (already a project dependency, see package.json:34).
  </approach>
  <verify>
    See validation_gate VG-3 below.
  </verify>
  <validation_gate id="VG-3" blocking="true">
    <prerequisites>Backend on :3000; database with at least one user row</prerequisites>
    <execute>
      curl -fsS -X POST http://localhost:3000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"correct-password"}'
    </execute>
    <capture>
      tee e2e-evidence/&lt;run&gt;/auth/step-01-login.body.json;
      curl writes -w "%{http_code}" to step-01-login.status.txt
    </capture>
    <pass_criteria>
      HTTP 200; body has non-null `accessToken` (JWT format, 3 dot-separated segments);
      response sets `refreshToken` cookie with HttpOnly + Secure + SameSite=Strict;
      decoded access token has `sub`, `exp` within 15 minutes from `iat`.
    </pass_criteria>
    <review>
      Read step-01-login.body.json; node -e "console.log(JSON.parse(atob(token.split('.')[1])))"
      to inspect claims; check curl -D output for Set-Cookie headers.
    </review>
    <verdict>PASS → advance to T4 | FAIL → fix endpoint → re-run from prerequisites</verdict>
    <mock_guard>Do NOT mock bcrypt, JWT, or DB. Real system end to end.</mock_guard>
  </validation_gate>
</task>
```

## Prompt rewrite patterns

For prompts (not plans), apply these specialized patterns.

### Role tightening

Weak:

> You are a helpful assistant.

Deepened:

```xml
<role>
  You are the Phase 3 implementation subagent for Shannon Framework v7. Your sole job
  is to apply skill-rewrite operations defined in .v7/synthesis/v7-plan.md section B.
  You do NOT make architectural decisions, you do NOT skip operations, you do NOT
  write test files.
</role>
<audience>The next phase consumer (Phase 4 functional-validation subagent)</audience>
<allowed_tools>Read, Write, Edit, Glob, Grep — no Bash for git operations</allowed_tools>
<voice>Terse, deliverable-focused, no preamble or recap</voice>
```

### Workflow phasing

Weak:

> Do the steps.

Deepened:

```xml
<workflow>
  <phase id="0" name="precondition">
    Verify the input document exists and is readable. If missing, STOP and request.
  </phase>
  <phase id="1" name="apply" transitions_to="2 on success | 0 on missing input">
    Apply each migration block in v7-plan.md section B in order. One commit per migration.
  </phase>
  <phase id="2" name="verify" transitions_to="3 on PASS | 1 on FAIL">
    Run the verification block at end of section B. If any check fails, return to phase 1
    for the specific migration that failed.
  </phase>
  <phase id="3" name="report" transitions_to="end">
    Emit PHASE-3-SUMMARY.md per the template.
  </phase>
</workflow>
```

### Output schema

Weak:

> Output your findings.

Deepened:

````xml
<output_specification format="markdown-with-xml-blocks">
  Write to: .v7/runs/phase-3/SUMMARY.md
  Structure:
  ```xml
  <summary>
    <files_changed count="N">
      <file path="..." operation="created|modified|deleted">brief description</file>
    </files_changed>
    <verification_results>
      <check name="..." status="PASS|FAIL" evidence="path/to/proof"/>
    </verification_results>
    <next_phase_handoff>One sentence on what Phase 4 needs to know.</next_phase_handoff>
  </summary>
  ```
  Maximum 500 lines. No prose preamble.
</output_specification>
````

## XML formatting principles

- Tag names describe content, not formatting (`<rationale>` not `<paragraph>`)
- Attributes carry metadata (`id`, `severity`, `weight`, `depends_on`)
- Nest for hierarchy (`<task><validation_gate>...`)
- Self-close empty elements (`<check name="..." status="PASS" evidence="..." />`)
- Keep prose in regular Markdown; XML only for structured / parseable content
- Always close opened tags — orphan tags break downstream parsers

## Size budget rules

For a deepening pass on a ~600-word PLAN.md (about 3,000 chars):
- Acceptable growth: up to ~2× (to 6,000 chars / ~1,200 words)
- Strong concern: 3× growth (to 9,000 chars)
- Forbidden: 5× growth — at that point you are rewriting, not deepening

For longer documents (>1500 words) the growth budget tightens — under 30%. Every addition must displace or replace weak content rather than appending.

## Before/after compactness

A deepened section is BETTER than the original in the same or similar number of words, not just longer.

Weak (3 words): "We will monitor."

Deepened (still compact, ~40 words):
```xml
<mitigation>
  Add Datadog monitor on POST /api/auth/login 401 rate. Alert at >5% over 5 minutes
  (baseline ~0.5%). Existing log structure (src/middleware/logger.ts:34) is
  Datadog-compatible — no new instrumentation code needed.
</mitigation>
```

40 words is acceptable for what it adds: specificity, threshold, baseline, owner.

## Anti-patterns in deepening

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Adding generic "insights" not tied to a specific gap | Cosmetic enrichment without rationale | Every addition must close an identified gap |
| Rewriting prose that was already good | Inflates the document; risks regressing intent | Leave strong sections alone; cite their score=0 in the table |
| Replacing existing rationale with "improved" rationale | Loses author's intent | Preserve the original phrasing; add additional context |
| Switching all prose to XML | Reduces human readability | Keep XML for structured content; prose stays prose |
| Increasing detail without increasing testability | "More thorough" without making it provable | Every added requirement must connect to a measurable check |
