---
name: functional-validation
description: End-to-end no-mocks validation through real system execution. ALWAYS use when the user says "validate this", "prove it works", "functional validation", "no mocks", "ensure feature works", "validate the feature", or when tempted to write test files. Builds, runs, exercises UI, captures evidence (screenshots, curl, CLI stdout), applies gate validation. Iron rule — real system in, evidence-cited verdict out. Covers iOS/macOS, CLI, Backend API, Web Frontend, and Full-Stack validation with evidence-based PASS/FAIL gates.
triggers:
  - "validate this"
  - "prove it works"
  - "functional validation"
  - "no mocks"
  - "ensure feature works"
  - "validate the feature"
required_hooks:
  - post-action-discipline
---

# Functional Validation

## The Iron Rule

```
IF the real system doesn't work, FIX THE REAL SYSTEM.
NEVER create mocks, stubs, test doubles, or test files.
ALWAYS validate through the same interfaces real users experience.
```

## Before You Validate

Ask yourself:
- **What does PASS look like?** Define specific, observable criteria BEFORE capturing evidence. "App works" is not a criteria. "Dashboard shows 3 active sessions with green status indicators" is.
- **What platform am I validating?** Detect from project files (see table below). Wrong platform = wrong validation approach = wasted time.
- **Is the system running?** Backend, database, external services — start them ALL before validating. Partial systems produce misleading failures.
- **Am I about to write a test file?** If yes, STOP. You are violating the Iron Rule. Fix the real system instead. The `block-fab-files` PreToolUse:Write hook will refuse the write, but the hook is a backstop — the discipline lives here.

## Platform Detection and Routing

| Indicator | Platform | Reference | Key Tool |
|-----------|----------|-----------|----------|
| `.xcodeproj`, `.xcworkspace` | iOS/macOS | **MANDATORY READ**: [ios-validation.md](references/ios-validation.md) | `xcrun simctl` + screenshots |
| `Cargo.toml`, `go.mod`, `pyproject.toml` with `[project.scripts]`, CLI binary | CLI | **MANDATORY READ**: [cli-validation.md](references/cli-validation.md) | Binary/module execution + exit codes |
| REST routes, OpenAPI spec | Backend API | **MANDATORY READ**: [api-validation.md](references/api-validation.md) | `curl` + response verification |
| React/Vue/Svelte, `package.json` | Web Frontend | **MANDATORY READ**: [web-validation.md](references/web-validation.md) | agent-browser + screenshots |
| Both frontend and backend | Full-Stack | Read BOTH api + web references | Integration through UI |

**Do NOT load** references for platforms that don't apply. Loading all four wastes context.

## Mock Detection — The Red Flags

These thoughts mean you're about to violate the Iron Rule. **STOP immediately.**

| The Thought | Why It's Wrong | What To Do Instead |
|-------------|---------------|---------------------|
| "Let me add a mock fallback for testing" | Mocks test mock behavior, not real behavior. You'll get a green light on broken code. | Fix why the real dependency isn't available. Start it. |
| "I'll write a quick unit test to verify" | Unit tests can't catch integration issues — the API returns 200 but the UI shows "No Data" because the JSON key changed. | Run the real app, look at the real UI. |
| "I'll stub this database" | In-memory DBs have different behavior (no constraints, no migrations, different SQL dialect). Your test passes, production crashes. | Start a real database instance. |
| "The real system is too slow/complex" | If it's too slow for you, it's too slow for users. That's a real bug. | Fix the performance issue. That IS the work. |
| "I'll add a test mode flag" | Test mode flags create two code paths. The production path is the one that breaks, and you're not testing it. | There is one mode: production. Test that. |
| "Just for local development" | "Just for local" artifacts get committed, merged, and deployed. Mock data leaks into production. It happens every time. | Use the same setup a user would. |

## The Validation Protocol

### 1. Start Real System and Execute

Start ALL real dependencies (backend, database, external services). Poll health endpoints — don't proceed until every dependency returns 200. Then execute through the platform's user interface. See your platform reference file for the specific build/launch/interaction sequence.

### 2. Capture Evidence

Every validation MUST produce reviewable evidence under Shannon's evidence convention:

```
e2e-evidence/<run-id>/<journey>/step-NN-<desc>.<ext>
```

| Platform | Evidence | How to Capture |
|----------|----------|----------------|
| iOS/macOS | Screenshots | `xcrun simctl io booted screenshot path.png` |
| CLI | Terminal output | `./binary args 2>&1 \| tee output.txt` |
| API | Response bodies | `curl -s url \| tee response.json \| jq .` |
| Web | Browser screenshots | `agent-browser screenshot --output path.png` |

The `post-action-discipline` hook refuses zero-byte artifacts at gate time. The `block-fab-files` hook refuses any `*.test.*`, `*.spec.*`, `tests/`, or `__tests__/` write attempt.

### 3. Verify Evidence (THE CRITICAL STEP)

**Capturing evidence without reviewing it is worse than not capturing it** — it creates false confidence.

For every piece of evidence:
1. **READ it** — use the Read tool for screenshots, `cat` for text
2. **Check against PASS criteria** — the criteria you defined BEFORE validation
3. **Note discrepancies** — anything unexpected is either a bug or wrong criteria
4. **Write a verdict** — PASS with citation (file, not directory; line ranges where relevant), or FAIL with what went wrong

### 4. When Validation FAILS

This is where most workflows break. When you get a FAIL:

| Failure Type | Diagnosis | Fix |
|--------------|-----------|-----|
| App shows error dialog | Read the error text. Check backend logs. | Fix the API or error handling. |
| Screenshot shows wrong screen | Navigation failed. Check deep link URL or tap coordinates. | Fix navigation, increase wait time. |
| API returns 500 | Check server logs for stack trace. | Fix the backend handler. |
| CLI exits non-zero | Read stderr output. | Fix the reported error. |
| Black/blank screenshot | App hasn't rendered yet. | Increase sleep time after launch. |
| Data not showing | Backend not running, or wrong endpoint. | Verify backend health, check API prefix. |

**After fixing, RE-VALIDATE from step 1.** Partial re-validation misses regressions.

### 5. Apply Gate Validation

Invoke the `evidence-gate` skill — the 5-question binary checklist (READ / VIEW / EXAMINE / CITE / Skeptic-agree). Any "no" → REFUSE the completion claim and route to `refusal-discipline` to emit `REFUSAL.md`.

## Multi-Platform Validation

If your change touches multiple platforms (e.g., API + Web, CLI + API, Mobile + Backend), validate the deepest dependency first:

```
Database → Backend API → Frontend/CLI/Mobile
```

A frontend bug might actually be a backend bug. Validate bottom-up to isolate failures correctly. Load the reference file for each platform you're validating.

## Evidence Quality Standards

Not all evidence is equal. High-quality evidence:

| Quality | Example | Why It Matters |
|---------|---------|----------------|
| **Good** | Screenshot showing "41 sessions" badge on Home screen | Proves specific data loaded correctly |
| **Bad** | Screenshot showing Home screen exists | Proves nothing about data correctness |
| **Good** | curl response with `{"total": 41, "items": [...]}` | Proves API returns expected data |
| **Bad** | curl response with `200 OK` | Proves endpoint exists, not correctness |
| **Good** | CLI output: `Processed 150 files in 2.3s` | Proves functionality AND performance |
| **Bad** | CLI output: `Done` | Proves it finished, not that it worked |

## Shannon Runtime Integration

- **Evidence path convention:** `e2e-evidence/<run-id>/<journey>/step-NN-<desc>.<ext>` — every artifact lands here. `evidence-indexing` skill writes per-directory `README.md` + `INDEX.md`.
- **Hooks that enforce the Iron Rule:**
  - `block-fab-files` (PreToolUse:Write) — refuses `*.test.*`, `*.spec.*`, `tests/`, `__tests__/`, `mocks/` paths.
  - `post-action-discipline` (Post-phase) — refuses zero-byte evidence artifacts before gate.
- **Citation discipline:** "file, not directory. Line ranges where relevant." A claim of PASS without a specific file path is not a claim.
- **Gate integration:** Always followed by `evidence-gate` (per-claim 5-question), then `completion-gate` (outer mechanical, the final completion gate in `/shannon:cook`).

### Worked Example

```
Feature: "Add password reset link to login page"

1. pnpm build → exit 0 (real build, no flags)
2. pnpm dev → server up on :3000 (poll /health until 200)
3. agent-browser navigate /login → screenshot
   e2e-evidence/run-2026-05-27/login-journey/step-01-login-loaded.png
4. agent-browser click "Forgot password" → screenshot
   e2e-evidence/run-2026-05-27/login-journey/step-02-reset-modal.png
5. agent-browser fill email → submit → screenshot
   e2e-evidence/run-2026-05-27/login-journey/step-03-email-sent-toast.png
6. Read all three screenshots; verify PASS criteria
7. evidence-gate → PASS
   Citations: step-01-login-loaded.png, step-02-reset-modal.png, step-03-email-sent-toast.png
```

## When to use

- Marking a feature complete
- Pre-merge / pre-deploy / pre-ship
- Verifying a bug fix worked
- Validating a UI redesign
- Any time the assistant claimed "done"

## When NOT to use

- Pure type-system change with no runtime behavior shift (typecheck is enough)
- Documentation-only commit
- File rename with no semantic change
- Use `e2e-validate` instead when you need the full platform-routed analyze → plan → execute → fix → audit pipeline

## NEVER

- **NEVER write test files** (`.test.ts`, `_test.go`, `Tests.swift`, `test_*.py`) — they test abstractions, not the real system. A passing test suite with a broken app is worse than no tests at all.
- **NEVER mock HTTP clients** (`URLProtocol`, `nock`, `httptest`, `responses`) — mocked responses don't change when the real API changes. Your mock says 200, the real API says 404.
- **NEVER use in-memory databases** (`SQLite :memory:`, `H2`) — they accept invalid SQL, skip migration issues, and have different concurrency behavior. Your "test" passes, production crashes.
- **NEVER render components in isolation** (Testing Library, Storybook for validation) — a component working alone proves nothing about the integrated system. Props change, contexts differ, API responses vary.
- **NEVER claim PASS without reading evidence** — file existence is not verification. A screenshot of a crash dialog is still a `.png` file. A curl response of `{"error": "not found"}` is still a 200-byte JSON file.
- **NEVER validate against a "test" configuration** — if you need `TEST_MODE=true` for it to work, it doesn't work. There is one mode: the mode users experience.
- **NEVER skip re-validation after a fix** — fixing one thing can break another. The ONLY way to know is to re-run the full validation.
- **NEVER fabricate evidence.** Quote real CLI stdout. Real screenshot pixels. Real HTTP response bodies.
- **NEVER use compilation success as proof of function.** Build pass ≠ feature works. Always exercise the running system.

## Related Skills

- `evidence-gate` — 5-question per-claim refusal checklist (run AFTER capturing evidence, BEFORE marking complete)
- `completion-gate` — outer mechanical evaluator for the final completion gate in `/shannon:cook`
- `refusal-discipline` — emits `REFUSAL.md` when a gate refuses
- `verification-before-completion` — lightweight per-commit / per-PR pre-claim check
- `no-fakes-discipline` — active enforcement against substitution attempts
- `evidence-indexing` — per-directory `README.md` + `INDEX.md` for every evidence dir
- `visual-inspection` — per-screenshot QA protocol before marking UI evidence as PASS
- `e2e-validate` — platform-routed umbrella with analyze/plan/execute/fix/audit/report workflows
- `ios-validation-runner` — five-phase iOS validation (SETUP → RECORD → ACT → COLLECT → VERIFY)


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `e2e-validate`

<iron_rule>
```
IF the real system doesn't work, FIX THE REAL SYSTEM.
NEVER create mocks, stubs, test doubles, or test files.
NEVER write .test.ts, _test.go, Tests.swift, test_*.py, or any test harness.
ALWAYS validate through the same interfaces real users experience.
ALWAYS capture evidence. ALWAYS review evidence. ALWAYS write verdicts.
```
</iron_rule>

<mock_detection>
These thoughts mean you are about to violate the Iron Rule. STOP immediately:

- "Let me add a mock fallback" → Fix why the real dependency is unavailable
- "I'll write a quick unit test" → Run the real app, look at the real output
- "I'll stub this database" → Start a real database instance
- "The real system is too slow" → That is a real bug. Fix it.
- "I'll add a test mode flag" → There is one mode: production. Test that.
- "Just for local development" → Use the same setup a user would
</mock_detection>

<platform_detection>
Detect the project platform by scanning the codebase. Check these indicators IN ORDER and assign the FIRST match. If multiple apply, use the combined platform type.

| Priority | Indicator Files | Platform | Validation Reference |
|----------|----------------|----------|---------------------|
| 1 | `.xcodeproj`, `.xcworkspace`, `Package.swift` | **ios** | references/_e2e-validate-ios-validation.md |
| 2 | `Cargo.toml` with `[[bin]]`, `go.mod` with `main.go`, `pyproject.toml` with `[project.scripts]`, `package.json` with `"bin"` | **cli** | references/_e2e-validate-cli-validation.md |
| 3 | REST routes, `routes/`, OpenAPI spec, `swagger.json`, Express/FastAPI/Flask/Gin/Actix handlers WITHOUT frontend files | **api** | references/_e2e-validate-api-validation.md |
| 4 | React/Vue/Svelte/Angular, `pages/`, `app/`, `src/components/`, `index.html` WITHOUT backend routes | **web** | references/_e2e-validate-web-validation.md |
| 5 | Frontend framework files AND backend routes/handlers | **fullstack** | references/_e2e-validate-fullstack-validation.md |
| 6 | None of the above | **generic** | references/_e2e-validate-generic-validation.md |

Detection script:
```bash
detect_platform() {
  local HAS_IOS=0 HAS_CLI=0 HAS_API=0 HAS_WEB=0

  [ -n "$(find . -maxdepth 3 -name '*.xcodeproj' -o -name '*.xcworkspace' -o -name 'Package.swift' 2>/dev/null | head -1)" ] && HAS_IOS=1

  [ -f Cargo.toml ] && grep -q '\[\[bin\]\]' Cargo.toml 2>/dev/null && HAS_CLI=1
  [ -f go.mod ] && [ -f main.go -o -d cmd/ ] && HAS_CLI=1
  [ -f pyproject.toml ] && grep -q '\[project.scripts\]' pyproject.toml 2>/dev/null && HAS_CLI=1
  [ -f package.json ] && grep -q '"bin"' package.json 2>/dev/null && HAS_CLI=1

  local API_SIGNALS=$(find . -maxdepth 3 \( -name 'routes*' -o -name 'handlers*' -o -name 'controllers*' -o -name 'swagger*' -o -name 'openapi*' \) 2>/dev/null | head -1)
  [ -n "$API_SIGNALS" ] && HAS_API=1

  local WEB_SIGNALS=$(find . -maxdepth 3 \( -name '*.jsx' -o -name '*.tsx' -o -name '*.vue' -o -name '*.svelte' -o -name 'next.config*' -o -name 'vite.config*' -o -name 'angular.json' \) 2>/dev/null | head -1)
  [ -n "$WEB_SIGNALS" ] && HAS_WEB=1

  [ "$HAS_IOS" -eq 1 ] && echo "ios" && return
  [ "$HAS_CLI" -eq 1 ] && echo "cli" && return
  [ "$HAS_WEB" -eq 1 ] && [ "$HAS_API" -eq 1 ] && echo "fullstack" && return
  [ "$HAS_API" -eq 1 ] && echo "api" && return
  [ "$HAS_WEB" -eq 1 ] && echo "web" && return
  echo "generic"
}
```

**Load ONLY the reference file for the detected platform.** Loading all references wastes context. For fullstack, load BOTH api-validation.md and web-validation.md.
</platform_detection>

<evidence_standards>
Every validation MUST produce reviewable evidence saved to `e2e-evidence/`:

| Platform | Evidence Type | Capture Method |
|----------|--------------|----------------|
| iOS | Screenshots + video + logs | `xcrun simctl io`, `log stream` |
| CLI | Terminal output + exit codes | `./binary args 2>&1 \| tee output.txt` |
| API | HTTP responses + status codes | `curl -s url \| tee response.json \| jq .` |
| Web | Browser screenshots + console | agent-browser |
| Full-Stack | All of the above, bottom-up | DB → API → Frontend |

Evidence quality:
- **GOOD**: Screenshot showing "41 sessions" badge on dashboard
- **BAD**: Screenshot showing dashboard exists
- **GOOD**: curl response with `{"total": 41, "items": [...]}`
- **BAD**: curl response with just `200 OK`
- **GOOD**: CLI output: `Processed 150 files in 2.3s`
- **BAD**: CLI output: `Done`

**Capturing evidence without reviewing it is WORSE than not capturing it.** For EVERY piece of evidence: READ it → CHECK against PASS criteria → NOTE discrepancies → WRITE verdict.
</evidence_standards>

<validation_order>
Always validate bottom-up through the dependency stack:

```
Database → Backend API → Frontend / CLI / Mobile
```

A frontend bug might actually be a backend bug. Validate the deepest dependency first. For each layer, define PASS criteria BEFORE capturing evidence.
</validation_order>

<intake>
Parse the command arguments to determine the workflow. Arguments are passed via $ARGUMENTS from the slash command.

Supported argument flags (combinable):

| Flag | Effect |
|------|--------|
| `--analyze` | Scan codebase, detect platform, identify all user journeys and endpoints. Output analysis only. |
| `--plan` | After analysis, generate a validation plan with PASS criteria for every journey. Requires approval before execution. |
| `--execute` | Run the full validation plan. If no plan exists, analyze + plan + execute. |
| `--fix` | When validation fails, attempt to fix the code and re-validate. |
| `--audit` | Run validation and save a detailed audit report without fixing anything. |
| `--report` | Generate/export a markdown report of the last validation run. |
| `--ci` | Non-interactive mode: no approval prompts, auto-execute everything. |
| `--platform <type>` | Override auto-detection. Values: ios, cli, api, web, fullstack. |
| `--scope <path>` | Limit validation to a specific module or directory. |
| `--parallel` | Use sub-agents for parallel research and validation phases. |
| `--verbose` | Detailed output including all curl responses, full CLI output, etc. |

Default (no flags): `--analyze --plan --execute` with approval gate between plan and execute.
</intake>

<routing>
| Parsed Intent | Workflow | Reference Files to Load |
|---------------|----------|------------------------|
| `--analyze` only | [workflows/analyze.md](workflows/analyze.md) | Platform-specific reference |
| `--plan` (with or without --analyze) | [workflows/plan.md](workflows/plan.md) | Platform reference + templates/validation-plan.md |
| `--execute` | [workflows/execute.md](workflows/execute.md) | Platform reference |
| `--fix` | [workflows/fix-and-revalidate.md](workflows/fix-and-revalidate.md) | Platform reference |
| `--audit` | [workflows/audit.md](workflows/audit.md) | Platform reference + templates/audit-report.md |
| `--report` | [workflows/report.md](workflows/report.md) | templates/e2e-report.md |
| Default (no flags) | [workflows/full-run.md](workflows/full-run.md) | Platform reference + all templates |
| `--ci` | [workflows/ci-mode.md](workflows/ci-mode.md) | Platform reference |

**After reading the workflow, follow it exactly.**
</routing>

<reference_index>
Platform-specific validation guides (load only what applies):

| File | Platform | Contents |
|------|----------|----------|
| references/_e2e-validate-cli-validation.md | CLI apps | Build, execute, capture output, verify exit codes |
| references/_e2e-validate-api-validation.md | Backend APIs | Start server, health check, curl requests, verify JSON |
| references/_e2e-validate-web-validation.md | Web frontends | Browser automation, screenshots, responsive testing |
| references/_e2e-validate-ios-validation.md | iOS/macOS | Simulator, screenshots, video, logs, deep links |
| references/_e2e-validate-fullstack-validation.md | Full-stack | Bottom-up integration: DB → API → Frontend |
| references/_e2e-validate-generic-validation.md | Other/unknown | Adaptive validation for non-standard projects |
</reference_index>

<workflow_index>
| Workflow | Purpose |
|----------|---------|
| workflows/analyze.md | Codebase scanning, platform detection, journey mapping |
| workflows/plan.md | Generate validation plan with PASS criteria |
| workflows/execute.md | Run validation, capture evidence, write verdicts |
| workflows/fix-and-revalidate.md | Fix failures and re-run validation |
| workflows/audit.md | Read-only validation run, no code changes |
| workflows/report.md | Generate/export validation report |
| workflows/full-run.md | Complete analyze → plan → approve → execute pipeline |
| workflows/ci-mode.md | Non-interactive continuous integration mode |
</workflow_index>

<template_index>
| Template | Purpose |
|----------|---------|
| templates/validation-plan.md | Structured plan with gates per journey |
| templates/audit-report.md | Read-only audit with findings |
| templates/e2e-report.md | Full report with evidence references |
| templates/verdict.md | Per-journey PASS/FAIL verdict format |
</template_index>

<script_index>
| Script | Purpose |
|--------|---------|
| scripts/detect-platform.sh | Auto-detect project platform type |
| scripts/health-check.sh | Poll service health endpoints |
| scripts/evidence-collector.sh | Initialize evidence directory structure |
| scripts/api-validator.sh | Automated curl-based API validation |
| scripts/web-validator.mjs | agent-browser-based web validation |
| scripts/ios-validator.sh | iOS simulator validation (adapted from ios-validation-runner) |
</script_index>

<success_criteria>
A complete e2e-validate run produces:
- Platform correctly detected (or overridden)
- Every user journey identified and documented
- PASS criteria defined BEFORE evidence capture
- Evidence captured for every journey step
- Every piece of evidence READ and reviewed (not just existence-checked)
- PASS/FAIL verdict written for every journey with evidence references
- Failed journeys include root cause analysis
- If --fix: code changes made, re-validation passed
- Final report saved to `e2e-evidence/report.md`
- Zero mocks, zero stubs, zero test files created
</success_criteria>

## Relationship to functional-validation

Per Shannon v1 design and v1 absorption decision, Shannon keeps BOTH skills:

- **`e2e-validate`** (this skill) — platform-routing umbrella. Owns the analyze → plan → execute → fix → audit → report pipeline, the platform detection script, the workflows/ and templates/ directories. Reach for this when you want the full structured run with intake flags.
- **`functional-validation`** — Shannon-runtime-integrated worker. Owns the per-journey Iron Rule discipline, the evidence-path convention (`e2e-evidence/<run-id>/<journey>/step-NN-<desc>.<ext>`), the integration with Shannon hooks (`block-fab-files`, `post-action-discipline`), the citation discipline. Reach for this when you're validating a single feature or bug fix and don't need the full pipeline.

They compose: `e2e-validate --execute` calls into `functional-validation` per journey. Inside any single journey, `functional-validation`'s rules apply.

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Capturing evidence without reviewing it | Creates false confidence — a screenshot of a crash dialog is still a .png file | READ every piece of evidence, CHECK against PASS criteria, WRITE verdict |
| Validating frontend before backend | Frontend bugs might actually be backend bugs — wrong diagnosis wastes time | Always validate bottom-up: Database → Backend API → Frontend |
| Defining PASS criteria after evidence capture | Confirmation bias makes you see what you expect instead of what's there | Define specific, observable PASS criteria BEFORE capturing any evidence |
| Loading all platform reference files | Wastes context on irrelevant platform guides | Detect platform first, load ONLY the matching reference file |
| Writing mocks or test files "to supplement" validation | Violates the Iron Rule — mocks test mock behavior, not real behavior | Fix the real system; validate through real user interfaces only |

## When NOT to Use

- Validating a single feature or bug fix (use `functional-validation` for targeted validation)
- Projects that use TDD with mocks by design (Shannon refuses; out of scope)
- Code review or architecture assessment (no real-system execution needed)
- Performance profiling (use dedicated profiling tools)

## Conflicts

- `functional-validation` — Overlapping scope but layered, not opposed. Use `e2e-validate` for the full platform-aware workflow with scripts, evidence directories, and reports. Use `functional-validation` for the core philosophy and single-feature validation. Layering preserved in v1 design.

## Related Skills

- `functional-validation` — protocol this skill implements per journey; Shannon-runtime-integrated worker
- `evidence-gate` — per-claim 6-question gate this skill's outputs are checked against
- `completion-gate` — outer mechanical gate that consumes this skill's report
- `no-fakes-discipline` — enforces the Iron Rule against mocks that this skill embeds
- `ios-validation-runner` — used when platform=ios for simulator + video + log capture
- `full-functional-audit` — uses this skill as engine in its Phase 3 EXECUTE
- `full-ui-experience-audit` — invokes this skill as optional Phase 6 final pass
- `plan-author` — generates structured validation plans with PASS criteria
- `autopilot-runner` — `/shannon:autopilot` invokes this skill as the analyze→plan→execute→fix→audit→report engine
- `refusal-discipline` — emits `REFUSAL.md` when this skill's verdict is FAIL
