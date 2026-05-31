# Do Patterns

This reference is loaded by `create-meta-prompts` step 1 when the user's selected purpose is **Do**. It defines the structural template for execution prompts — prompts that produce code, files, or artifacts directly.

## When to use Do patterns

The Do purpose covers: implement, build, create, fix, add, refactor, integrate, port, migrate. The output is an artifact (code, config, schema, docs) that lives in the project, not a research report or plan.

## Required structure

A Do prompt must contain these sections, in this order:

```markdown
# {Topic} — Do prompt

## Objective
One sentence: what artifact will exist when this prompt completes.

## Context
@-references to relevant files. Use !-bang for dynamic context (git status, ls).

## Pre-conditions
What must be true before this prompt can run (dependencies installed, services up, branch checked out).

## Tasks
Numbered, each task has:
- Type: implement / refactor / fix / add
- Files: absolute paths the task touches
- Action: imperative sentence ("create POST /api/users that …")
- Verify: how to confirm task succeeded
- Done: condition that means task is complete

## Validation Gates
One gate per task or per logical unit. Iron Rule. Real-system check.

## Output Specification
Where the final artifact lands and the structure of SUMMARY.md.

## Success Criteria
Concrete, measurable conditions.

## SUMMARY.md
Path: `.prompts/{n}-{topic}-do/SUMMARY.md`
Required fields: one-liner, version, files created, decisions needed, blockers, next step.
```

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Tasks without file paths | Implementer guesses where to write — wastes a turn | Always cite the target file path |
| Verification step is "tests pass" | Iron Rule violation; tests are mocks | Verify via real system — curl, screenshot, exit code |
| Single "do everything" task | Untrackable progress; partial failures invisible | Break into 2–5 tasks each with own verification |
| Output spec omitted | Downstream prompts cannot consume the result | Always specify where SUMMARY.md lives + its schema |
| No pre-conditions | First run wastes time discovering dependencies | List exact commands to verify environment |

## Template — minimal Do prompt

```markdown
# Add password reset endpoint — Do prompt

## Objective
A working POST /api/auth/password-reset endpoint exists that emails a reset link.

## Context
@src/routes/auth.ts
@src/services/email.ts
!git -C . log -1 --format='%h %s'

## Pre-conditions
- Backend builds: `npm run build` exit 0
- Database migrated: `npm run db:migrate` exit 0
- SendGrid API key present in .env

## Tasks
1. **Add route handler**
   - Files: src/routes/auth.ts
   - Action: Register POST /api/auth/password-reset that validates email, generates token (jose), stores in `password_resets` table, calls email service.
   - Verify: curl POST returns 202; row appears in `password_resets`.
   - Done: handler exists and is mounted in router

2. **Add email template**
   - Files: src/templates/password-reset.html
   - Action: Render link to `/reset/:token` with expiry note.
   - Verify: rendered HTML contains the token.

## Validation Gates
<validation_gate id="VG-1" blocking="true">
  <execute>curl -fsS -X POST http://localhost:3000/api/auth/password-reset -d '{"email":"test@example.com"}'</execute>
  <capture>tee evidence/reset.json</capture>
  <pass_criteria>Status 202; mocked email service NOT used; row in password_resets table</pass_criteria>
</validation_gate>

## Output Specification
- Files created: src/routes/auth.ts (modified), src/templates/password-reset.html (new)
- SUMMARY.md at .prompts/003-pwreset-do/SUMMARY.md

## Success Criteria
- VG-1 passes against running backend
- One row in password_resets with valid token
- Email service called once (verifiable via SendGrid sandbox dashboard)
```

## Code-execution chain notes

A Do prompt usually depends on a Plan prompt from earlier in the chain. Reference the plan via `@.prompts/002-{topic}-plan/{topic}-plan.md` in the Context section.

Do prompts MUST honor the Iron Rule. No test files written. No mocks. Validation via real system.

## SUMMARY.md schema for Do prompts

```markdown
# {Topic} — Do summary

**One-liner:** {what got built, in one substantive sentence}

**Version:** v1
**Date:** 2026-05-27

## Files created
- path/to/file1.ts (description)
- path/to/file2.html (description)

## Files modified
- path/to/existing.ts (added handler at lines NN-MM)

## Decisions needed
- {decision the user should make, or "None"}

## Blockers
- {external impediment, or "None"}

## Next step
{concrete forward action — usually the next prompt in the chain}
```
