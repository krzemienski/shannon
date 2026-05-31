---
name: plan-author
description: Linear hierarchical plan author producing plan.md + phase-NN.md files. Plans-as-prompts framing — PLAN.md IS the prompt that executes the phase. ALWAYS use when the user says "plan this", "create plan", "implementation plan", "write a plan", "draft plan", or invokes /shannon:plan, /shannon:plan-author, /shannon:plan-author, /shannon:plan-deep, or /shannon:prd. Each phase has measurable transcript-provable success criteria and an embedded validation gate. Scope-atomic (2-3 tasks max per file).
triggers:
  - "plan this"
  - "create plan"
  - "implementation plan"
  - "write a plan"
  - "draft plan"
---

# plan-author


## Codebase-first discipline (load-bearing)

**Before any planning logic runs, this skill REQUIRES that the planning context already contains the output of:**

1. `codebase-analysis` — the 5-scientist parallel repo survey (inventory + deps + entry-points + proving-cmds + module-map)
2. `skill-inventory` — the filesystem-scanned skill catalogue (no MCP; reads ~/.claude/ + plugin caches + settings.json enabledPlugins)
3. `library-docs-fetch` — fetched documentation for every third-party library identified by codebase-analysis Stream 2 (deps-summary.md)

If ANY of these three are missing, plan-author MUST refuse to produce a plan and instead emit a `REFUSAL.md` instructing the caller to first run `/shannon:scope` (which orchestrates all four streams in parallel: codebase + skills + observability + library-docs).

This is the operational form of the user's MANDATORY CODE BASE ANALYSIS rule. Planning without surveying the existing code is the source of plan-vs-reality drift. Refusal is the correct response, not "good enough" guesses.

### How plans cite the pre-flight outputs

Every plan task references one of:

- **A specific file or module** (from codebase-analysis Stream 1 or Stream 5):
  `Task 3.2: Refactor src/api/handlers/auth.ts (cited in module-map.md as the auth boundary)`
- **A specific skill** (from skill-inventory directly-relevant table):
  `Task 4.1: Invoke 'Skill: agent-toolkit:codex-plan' for the detailed design subphase (matched trigger "detailed implementation plan")`
- **A specific proving-command** (from codebase-analysis Stream 4):
  `Task 5.3: Validate via 'pnpm test:integration' (proving-commands.json line 12)`
- **A specific library docs section** (from library-docs-fetch output):
  `Task 6.2: Use the React Server Components API as documented in e2e-evidence/<run-id>/library-docs/react.md § "Server Components" (fetched from https://react.dev/reference/rsc/server-components)`

No plan task says "consider using a planning skill" or "look at the auth code" without a concrete citation. The pre-flight made these citable; the plan must use them.


Backs `/shannon:plan`, `/shannon:plan-author` (per candidate), `/shannon:plan-author` (per round), `/shannon:plan-deep`, `/shannon:prd` (PRD mode).

Adopts the framing of anthropic-skills/create-plans while preserving Shannon's gate-in-phase canonical structure, iron rules, and downstream-command integration.

## Essential principles

### plans_are_prompts

PLAN.md is not a document that gets later transformed into a prompt. **PLAN.md IS the prompt.** When you write a phase, you are writing the prompt that will execute it. Every section of the phase file is read literally by the downstream executor (`/shannon:autopilot`, `/shannon:exec`, `/shannon:loop`).

Implication: no "process" prose. No "the team should …". Direct, second-person, instruction-mode language.

### scope_control_via_atomicity

Plans must complete within ~50% of context to maintain consistent quality.

Context-degradation curve (per anthropic create-plans):
- 0-30%: peak quality
- 30-50%: good quality
- 50-70%: degrading
- 70%+: poor (rushed, self-lobotomizing)

**Aggressive atomicity rule:** Each phase file caps at **2-3 tasks**. Better 10 small high-quality phases than 3 large degraded ones. Each commit is surgical.

File naming sorts chronologically:
```
plans/<date>-<slug>/01-01-PLAN.md
plans/<date>-<slug>/01-02-PLAN.md
plans/<date>-<slug>/01-03-PLAN.md
```

### hierarchy_BRIEF_to_PLAN

Adopted from create-plans. Shannon now ships the full hierarchy, not just plan/phase:

```
.planning/
  BRIEF.md            # one-paragraph problem statement (intent)
  ROADMAP.md          # phase list with milestones, no implementation detail
  RESEARCH.md         # findings from library-docs-fetch / codebase-research
  FINDINGS.md         # synthesis of research relevant to plan
  PLAN.md             # this skill's primary output (overview)
  phase-NN-<slug>.md  # individual phase files (the actual prompts)
  SUMMARY.md          # written after each phase completes
```

`/shannon:plan` writes BRIEF→ROADMAP→PLAN→phase-* in one invocation when starting fresh. `/shannon:plan-deep` adds RESEARCH/FINDINGS in front.

### deviation_rules (embedded in plan, no flow break)

Plans are guides, not straitjackets. During execution:

1. **Auto-fix bugs** — broken behavior discovered mid-phase → fix immediately, document in SUMMARY.md.
2. **Auto-add missing critical** — security/correctness gaps → add immediately, document.
3. **Auto-fix blockers** — can't proceed → fix immediately, document.
4. **Ask about architectural** — major structural changes → STOP and ask user.
5. **Log enhancements** — nice-to-haves → append to ISSUES.md, continue.

Only Rule 4 requires user intervention. All deviations recorded in the phase SUMMARY.md with rule applied + commit hash.

### domain_expertise_loading

Before writing a phase plan, scan for domain expertise:

```bash
ls ~/.claude/skills/expertise/ 2>/dev/null
```

If domain inferred from keywords (macOS, iOS, Unity, MIDI, Agent SDK, Python workflow, UI design), load the matching `expertise/<domain>` skill for context. Loading expertise selectively keeps the plan-author context lean (5k vs 20-27k tokens).

### anti_enterprise_patterns

NEVER include in a Shannon plan:
- Team structures, roles, RACI matrices
- Sprint ceremonies, standups, retros
- Stakeholder management, alignment meetings
- Multi-week estimates, resource allocation
- Documentation for documentation's sake

If it sounds like corporate PM theater, delete it.

### transcript_provable_success_criteria

Every success criterion must be demonstrable from the executor's own transcript (per northstar/goal-engineering). Use the 4-part recipe (cross-link: `skills/goal-engineering/SKILL.md`):

- **End state** — one measurable outcome.
- **Check** — exact command producing proof.
- **Constraints** — must-not-break list.
- **Bound** — turn or wall-clock budget.

Example (GOOD):
> `curl -s localhost:3000/api/items | jq '.items | length'` returns ≥ 1; HTTP 200; no error messages on stderr; completes within 60s.

Example (BAD — rejected by plan-author):
> "Endpoint works correctly."

## Behavior contract

1. Read user brief.
2. Read project context: `CLAUDE.md`, `docs/codebase-summary.md`, `docs/system-architecture.md`, `docs/code-standards.md`.
3. **Context scan**: check for existing `.planning/BRIEF.md`, `.planning/ROADMAP.md`, `.planning/phases/` — if present, this is a resume.
4. **Domain detection**: scan `~/.claude/skills/expertise/`; infer domain from keywords; confirm with user.
5. **Pre-plan interview (GREENFIELD only)**: invoke `skills/interview-framework/SKILL.md` for intake (intent-based depth scaling). Skip for TRIVIAL or REFACTOR intent.
6. Decompose into phases. Each phase:
   - Atomic (2-3 tasks max)
   - File-scoped (explicit Modify/Create/Delete lists)
   - Has 4-part transcript-provable success criteria
   - Has embedded validation gate (no separate gate files)
7. Write `plans/<date>-<slug>/`:
   - `plan.md` (overview, ≤80 lines, phase list with status)
   - `phase-NN-<name>.md` ... one per phase
   - `BRIEF.md` (when starting from raw intent)
8. Final phase is always validation (real-system exercise + evidence gate) for any user-facing change.

## Phase file canonical structure

```markdown
# Phase NN: <name>

## Context Links
- BRIEF.md, ROADMAP.md, RESEARCH.md, FINDINGS.md (as applicable)
- Related reports / files / docs

## Overview
- Priority: <high | medium | low>
- Status: <pending | in_progress | completed>
- Description: <one paragraph>

## Key Insights
- <bullets from research / scout>

## Requirements
- Functional: <list>
- Non-functional: <perf, security, a11y>

## Architecture
- <diagrams or prose>

## Related Code Files
- Modify: <file paths>
- Create: <file paths>
- Delete: <file paths>

## Implementation Steps
1. <numbered, ≤3 atomic tasks>
2. ...

## Todo List
- [ ] <item>
- [ ] <item>

## Success Criteria (4-part)
- **End state:** <one measurable outcome>
- **Check:** <exact command producing proof>
- **Constraints:** <must-not-break list>
- **Bound:** <turn or wall-clock budget>

## Validation Gate
- Skill: functional-validation | visual-inspection | api-validation | …
- Real system to exercise: <server | simulator | CLI invocation>
- Journey to execute: <step-by-step>
- Evidence required: <screenshot | response body | log tail>
- PASS criterion: <specific>
- FAIL → consequence: halt + refusal-discipline OR retry via /shannon:fix
- Evidence path: e2e-evidence/<run-id>/phase-NN/

## Risk Assessment
- <likelihood × impact + mitigation>

## Security Considerations
- <auth, input validation, secrets>

## Deviation Rules (embedded)
- Bugs found mid-phase → auto-fix, document.
- Missing critical → auto-add, document.
- Blockers → auto-fix, document.
- Architectural changes → STOP, ask user.
- Enhancements → log to ISSUES.md, continue.

## Next Steps
- Dependencies: <other phases>
- Follow-up: <future work>
```

## When to use

- `/shannon:plan` invocation
- `/shannon:plan-author` per-candidate spawn
- `/shannon:plan-author` per-round spawn
- `/shannon:plan-deep` (with RESEARCH/FINDINGS prepended)
- `/shannon:prd` PRD mode

## Iron rules

- Every phase has 4-part transcript-provable success criteria — no "feature works" vague language.
- Every user-facing phase has a validation gate.
- **No phase claims "tests pass" or "test coverage" as success.** Phases never include test files.
- File ownership explicit per phase (Modify/Create/Delete).
- Plans-as-prompts: the phase file IS the executor prompt. No prose addressed to humans-only.
- Atomicity: 2-3 tasks max per phase file.
- Anti-enterprise: no RACI, no ceremonies, no stakeholder talk.

## Cross-references

- `skills/goal-engineering/SKILL.md` — Success Criteria 4-part recipe authority.
- `skills/interview-framework/SKILL.md` — pre-plan intake for GREENFIELD.
- `skills/plan-deepen/SKILL.md` — one-shot hardening of an existing plan.
- `skills/plan-author/SKILL.md` — author↔red-teamer iteration loop.
- `skills/plan-author/SKILL.md` — multi-perspective consensus.
- `skills/plan-author/SKILL.md` — gate injection (called by `/shannon:plan-deep`).
- `skills/library-docs-fetch/SKILL.md` — standards-to-skill mapping (Phase 0).
- `skills/library-docs-fetch/SKILL.md` — documentation research mode (invoked from `/shannon:scope` or `/shannon:research`).
- `skills/prd-clarity/SKILL.md` — 100-point rubric before `/shannon:prd` emission.


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `plan-author`

# plan-author

Backs `/shannon:plan-author`. Iterative convergence between author and red-teamer.

## Layering note

Three distinct hardening modes — pick the one matching your need:

| Skill | Mode | Use when |
|---|---|---|
| `plan-author` (this) | **Iteration loop** (author ↔ red-teamer for N rounds) | Plan needs iterative tempering; max-rounds budget known |
| `plan-deepen` (GM-044) | **One-shot hardening** of an existing plan with selective focus | Plan exists, just stress-test it once |
| `plan-author` | **Parallel candidates** with distinct lenses + tournament-judge | Multiple viable approaches need head-to-head comparison |

Cross-links:
- `skills/plan-deepen/SKILL.md` — one-shot, confidence-scored, selective deepening.
- `skills/plan-author/SKILL.md` — multi-candidate consensus.
- `skills/gepetto/SKILL.md` — optional cross-model external review (Gemini + Codex) bolt-on for high-stakes rounds.

## Behavior contract

For round 1..max-rounds:

1. **Round 1**: `plan-author` agent produces draft.
2. `red-teamer` agent reviews draft; emits findings tagged BLOCKING / HIGH / MEDIUM / LOW.
3. **Round N (N>1)**: `plan-author` reads previous round's critique; produces revised draft.
4. **Convergence check**: red-teamer in round N reports ≤1 BLOCKING finding → CONVERGED.
5. Each round writes:
   - `plans/converge-<run-id>/round-<N>/draft.md`
   - `plans/converge-<run-id>/round-<N>/critique.md`
6. **On convergence**: promote final draft to `plans/<date>-<slug>/`; archive `converge-<run-id>/` to `_history/`.
7. **On non-convergence at max-rounds**: ship the best-scoring round anyway with a `NON_CONVERGED.md` note explaining why.

## Optional cross-model external review hook

For high-stakes plans (auth, payments, data migration, security-critical), an additional cross-model review can run **between** round N and round N+1, or as a final-round gate.

Invoke `skills/gepetto/SKILL.md` review step:

```bash
# Optional: external multi-LLM review of current round's draft
# Requires gemini and codex CLIs available; document as optional
gemini --review plans/converge-<run-id>/round-<N>/draft.md \
  > plans/converge-<run-id>/round-<N>/gemini-review.md
codex --review plans/converge-<run-id>/round-<N>/draft.md \
  > plans/converge-<run-id>/round-<N>/codex-review.md
```

If either external CLI is unavailable: log "external review unavailable" to `round-<N>/critique.md` and continue with same-model red-team only. Cross-model review is a **bolt-on, never required**.

Findings from external reviews are merged into the next round's critique. Each external finding must still cite file:line; otherwise it is rejected.

## Promote / archive convention

- **Promoted plan** (final, CONVERGED): `plans/<date>-<slug>/plan.md` + `phase-*.md`.
- **Archived rounds**: `plans/_history/converge-<run-id>/round-<N>/{draft.md,critique.md,gemini-review.md,codex-review.md}`.
- **NON_CONVERGED.md** (max-rounds without convergence): top-level note in promoted dir explaining which round was selected (best score by red-teamer count of BLOCKING/HIGH findings) and what's still outstanding.

## When to use

- Topic where author and critic perspectives are productive (security review, perf review).
- Plan needs iterative hardening but not full tournament.
- Time-bounded planning with quality bar.

## When NOT to use

- Decision needs multiple distinct lenses simultaneously → use `/shannon:plan-author`.
- Plan already exists, only needs one-shot stress-test → use `/shannon:plan-deep` (skills/plan-deepen).
- Small change with obvious plan → use `/shannon:plan`.

## Iron rules

- Each round MUST produce a NEW draft — re-emitting prior round unchanged = invalid.
- Red-teamer MUST cite `file:line` per finding.
- Max-rounds is hard. No silent overrun.
- Cross-model external review (gepetto) is **optional**; never block on it.
- External findings must cite `file:line`; ungrounded "this could break" rejected.

## Absorbed from `plan-author`

# plan-author

Backs `/shannon:plan-author`. Tournament-style consensus planning. Shannon-unique skill — no reference equivalent in anthropic-skills, northstar, or ralph.

## Behavior contract

1. Read user problem statement.
2. **Determine candidate perspectives** (default 3): security-first, performance-first, simplicity-first. Configurable to add: scalability-first, accessibility-first, cost-first.
3. **Spawn N `plan-author` agents in parallel via `Task`** (single message, parallel block — per dispatch-parallel discipline). Each gets:
   - The same problem statement
   - A distinct **lens prompt** (see `references/_plan-tournament-lens-prompts.md`)
   - Isolated output directory: `plans/tournament-<run-id>/candidate-<N>/`
4. After all candidates emit plans: spawn `red-teamer` agent per candidate. Red-teamer reads candidate plan, emits findings BLOCKING/HIGH/MEDIUM/LOW with cited `file:line` per finding.
5. **Score candidates:**
   - +10 per HIGH or BLOCKING avoided vs other candidates
   - -5 per BLOCKING introduced (security holes, scope inversions)
   - -2 per HIGH introduced
   - +5 simplicity bonus (lowest line count, fewest phases) — KISS
6. **Cross-pollination step (NEW):** before promoting the winner, the winning candidate reads every loser's red-team findings. For each finding the winner did not already address, the winner explicitly decides: import / discard. Decisions logged in `plans/tournament-<run-id>/CROSS_POLLINATION.md`.
7. **Optional pre-promotion human gate (NEW):** if any candidate's red-team findings include BLOCKING in (auth | payments | data-migration | privacy | security | crypto), pause and present a one-page summary to the user before promotion. Default: skip the gate.
8. Select winner. Write `plans/tournament-<run-id>/VERDICT.md` citing score breakdown + selection reasoning + cross-pollination decisions.
9. Promote winner to `plans/<date>-<slug>/`. Move losers to `plans/_rejected/tournament-<run-id>/`.

## Lens prompts

Per-perspective lens prompt content is documented in `references/_plan-tournament-lens-prompts.md`. Each lens prompt prepends to the standard plan-author prompt with explicit constraints:

| Lens | Optimizes for | Hard constraints |
|---|---|---|
| security-first | Threat surface minimization | Every input validated, authn/authz before logic, secrets via env, least-privilege |
| performance-first | Latency / throughput | Caching layer named, N+1 ruled out, p95 target stated |
| simplicity-first | Fewest moving parts | No new infra unless justified, one language preferred, ≤3 phases |
| scalability-first | 10x growth headroom | Stateless services, queue-based async, horizontal scaling path |
| accessibility-first | WCAG 2.2 AA + assistive tech | Semantic HTML, keyboard nav, aria labels, contrast ≥4.5 |
| cost-first | Cloud bill minimization | No always-on infra, serverless where possible, free tier exploited |

See `references/_plan-tournament-lens-prompts.md` for full lens-prompt text bodies.

## When to use

- High-stakes decisions where multiple approaches exist.
- Cross-cutting concerns (security AND performance AND simplicity all matter).
- Pre-architecture-review.

## When NOT to use

- Routine feature with obvious approach.
- Speed-critical iteration (tournament is 3× wall time).
- Tight scope where one perspective dominates.

## File ownership

- **Coordinator**: writes `VERDICT.md` and `CROSS_POLLINATION.md` ONLY.
- **Candidate-N**: writes ONLY `candidate-<N>/` subdirectory.
- **Red-teamer**: writes ONLY `candidate-<N>/red-team-findings.md`.

## Iron rules

- Lens prompts are non-interchangeable. A security-first candidate cannot quietly drop the threat-surface analysis.
- Red-teamer findings cite `file:line`. Ungrounded "this might break" rejected.
- Cross-pollination decisions logged with rationale per imported/discarded finding.
- Pre-promotion human gate triggers only on BLOCKING in named domains. Otherwise auto-promote.

## Absorbed from `plan-author`

<essential_principles>

<principle name="solo_developer_plus_claude">
You are planning for ONE person (the user) and ONE implementer (Claude).
No teams. No stakeholders. No ceremonies. No coordination overhead.
The user is the visionary/product owner. Claude is the builder.
</principle>

<principle name="plans_are_prompts">
PLAN.md is not a document that gets transformed into a prompt.
PLAN.md IS the prompt. It contains:
- Objective (what and why)
- Context (@file references)
- Tasks (type, files, action, verify, done, checkpoints)
- Verification (overall checks)
- Success criteria (measurable)
- Output (SUMMARY.md specification)

When planning a phase, you are writing the prompt that will execute it.
</principle>

<principle name="scope_control">
Plans must complete within ~50% of context usage to maintain consistent quality.

**The quality degradation curve:**
- 0-30% context: Peak quality (comprehensive, thorough, no anxiety)
- 30-50% context: Good quality (engaged, manageable pressure)
- 50-70% context: Degrading quality (efficiency mode, compression)
- 70%+ context: Poor quality (self-lobotomization, rushed work)

**Critical insight:** Claude doesn't degrade at 80% - it degrades at ~40-50% when it sees context mounting and enters "completion mode." By 80%, quality has already crashed.

**Solution:** Aggressive atomicity - split phases into many small, focused plans.

Examples:
- `01-01-PLAN.md` - Phase 1, Plan 1 (2-3 tasks: database schema only)
- `01-02-PLAN.md` - Phase 1, Plan 2 (2-3 tasks: database client setup)
- `01-03-PLAN.md` - Phase 1, Plan 3 (2-3 tasks: API routes)
- `01-04-PLAN.md` - Phase 1, Plan 4 (2-3 tasks: UI components)

Each plan is independently executable, verifiable, and scoped to **2-3 tasks maximum**.

**Atomic task principle:** Better to have 10 small, high-quality plans than 3 large, degraded plans. Each commit should be surgical, focused, and maintainable.

**Autonomous execution:** Plans without checkpoints execute via subagent with fresh context - impossible to degrade.

See: references/_create-plans-scope-estimation.md
</principle>

<principle name="human_checkpoints">
**Claude automates everything that has a CLI or API.** Checkpoints are for verification and decisions, not manual work.

**Checkpoint types:**
- `checkpoint:human-verify` - Human confirms Claude's automated work (visual checks, UI verification)
- `checkpoint:decision` - Human makes implementation choice (auth provider, architecture)

**Rarely needed:** `checkpoint:human-action` - Only for actions with no CLI/API (email verification links, account approvals requiring web login with 2FA)

**Critical rule:** If Claude CAN do it via CLI/API/tool, Claude MUST do it. Never ask human to:
- Deploy to Vercel/Railway/Fly (use CLI)
- Create Stripe webhooks (use CLI/API)
- Run builds/tests (use Bash)
- Write .env files (use Write tool)
- Create database resources (use provider CLI)

**Protocol:** Claude automates work → reaches checkpoint:human-verify → presents what was done → waits for confirmation → resumes

See: references/_create-plans-checkpoints.md, references/_create-plans-cli-automation.md
</principle>

<principle name="deviation_rules">
Plans are guides, not straitjackets. Real development always involves discoveries.

**During execution, deviations are handled automatically via 5 embedded rules:**

1. **Auto-fix bugs** - Broken behavior → fix immediately, document in Summary
2. **Auto-add missing critical** - Security/correctness gaps → add immediately, document
3. **Auto-fix blockers** - Can't proceed → fix immediately, document
4. **Ask about architectural** - Major structural changes → stop and ask user
5. **Log enhancements** - Nice-to-haves → auto-log to ISSUES.md, continue

**No user intervention needed for Rules 1-3, 5.** Only Rule 4 (architectural) requires user decision.

**All deviations documented in Summary** with: what was found, what rule applied, what was done, commit hash.

**Result:** Flow never breaks. Bugs get fixed. Scope stays controlled. Complete transparency.

See: workflows/execute-phase.md (deviation_rules section)
</principle>

<principle name="ship_fast_iterate_fast">
No enterprise process. No approval gates. No multi-week timelines.
Plan → Execute → Ship → Learn → Repeat.

**Milestone-driven:** Ship v1.0 → mark milestone → plan v1.1 → ship → repeat.
Milestones mark shipped versions and enable continuous iteration.
</principle>

<principle name="milestone_boundaries">
Milestones mark shipped versions (v1.0, v1.1, v2.0).

**Purpose:**
- Historical record in MILESTONES.md (what shipped when)
- Greenfield → Brownfield transition marker
- Git tags for releases
- Clear completion rituals

**Default approach:** Extend existing roadmap with new phases.
- v1.0 ships (phases 1-4) → add phases 5-6 for v1.1
- Continuous phase numbering (01-99)
- Milestone groupings keep roadmap organized

**Archive ONLY for:** Separate codebases or complete rewrites (rare).

See: references/_create-plans-milestone-management.md
</principle>

<principle name="anti_enterprise_patterns">
NEVER include in plans:
- Team structures, roles, RACI matrices
- Stakeholder management, alignment meetings
- Sprint ceremonies, standups, retros
- Multi-week estimates, resource allocation
- Change management, governance processes
- Documentation for documentation's sake

If it sounds like corporate PM theater, delete it.
</principle>

<principle name="context_awareness">
Monitor token usage via system warnings.

**At 25% remaining**: Mention context getting full
**At 15% remaining**: Pause, offer handoff
**At 10% remaining**: Auto-create handoff, stop

Never start large operations below 15% without user confirmation.
</principle>

<principle name="user_gates">
Never charge ahead at critical decision points. Use gates:
- **AskUserQuestion**: Structured choices (2-4 options)
- **Inline questions**: Simple confirmations
- **Decision gate loop**: "Ready, or ask more questions?"

Mandatory gates:
- Before writing PLAN.md (confirm breakdown)
- After low-confidence research
- On verification failures
- After phase completion with issues
- Before starting next phase with previous issues

See: references/_create-plans-user-gates.md
</principle>

<principle name="git_versioning">
All planning artifacts are version controlled. Commit outcomes, not process.

- Check for repo on invocation, offer to initialize
- Commit only at: initialization, phase completion, handoff
- Intermediate artifacts (PLAN.md, RESEARCH.md, FINDINGS.md) NOT committed separately
- Git log becomes project history

See: references/_create-plans-git-integration.md
</principle>

</essential_principles>

<context_scan>
**Run on every invocation** to understand current state:

```bash
# Check git status
git rev-parse --git-dir 2>/dev/null || echo "NO_GIT_REPO"

# Check for planning structure
ls -la .planning/ 2>/dev/null
ls -la .planning/phases/ 2>/dev/null

# Find any continue-here files
find . -name ".continue-here.md" -type f 2>/dev/null

# Check for existing artifacts
[ -f .planning/BRIEF.md ] && echo "BRIEF: exists"
[ -f .planning/ROADMAP.md ] && echo "ROADMAP: exists"
```

**If NO_GIT_REPO detected:**
Inline question: "No git repo found. Initialize one? (Recommended for version control)"
If yes: `git init`

**Present findings before intake question.**
</context_scan>

<domain_expertise>
**Domain expertise lives in `~/.claude/skills/expertise/`**

Before creating roadmap or phase plans, determine if domain expertise should be loaded.

<scan_domains>
```bash
ls ~/.claude/skills/expertise/ 2>/dev/null
```

This reveals available domain expertise (e.g., macos-apps, iphone-apps, unity-games, nextjs-ecommerce).

**If no domain skills found:** Proceed without domain expertise (graceful degradation). The skill works fine without domain-specific context.
</scan_domains>

<inference_rules>
If user's request contains domain keywords, INFER the domain:

| Keywords | Domain Skill |
|----------|--------------|
| "macOS", "Mac app", "menu bar", "AppKit", "SwiftUI desktop" | expertise/macos-apps |
| "iPhone", "iOS", "iPad", "mobile app", "SwiftUI mobile" | expertise/iphone-apps |
| "Unity", "game", "C#", "3D game", "2D game" | expertise/unity-games |
| "MIDI", "MIDI tool", "sequencer", "MIDI controller", "music app", "MIDI 2.0", "MPE", "SysEx" | expertise/midi |
| "Agent SDK", "Claude SDK", "agentic app" | expertise/with-agent-sdk |
| "Python automation", "workflow", "API integration", "webhooks", "Celery", "Airflow", "Prefect" | expertise/python-workflow-automation |
| "UI", "design", "frontend", "interface", "responsive", "visual design", "landing page", "website design", "Tailwind", "CSS", "web design" | expertise/ui-design |

If domain inferred, confirm:
```
Detected: [domain] project → expertise/[skill-name]
Load this expertise for planning? (Y / see other options / none)
```
</inference_rules>

<no_inference>
If no domain obvious from request, present options:

```
What type of project is this?

Available domain expertise:
1. macos-apps - Native macOS with Swift/SwiftUI
2. iphone-apps - Native iOS with Swift/SwiftUI
3. unity-games - Unity game development
4. swift-midi-apps - MIDI/audio apps
5. with-agent-sdk - Claude Agent SDK apps
6. ui-design - Stunning UI/UX design & frontend development
[... any others found in expertise/]

N. None - proceed without domain expertise
C. Create domain skill first

Select:
```
</no_inference>

<load_domain>
When domain selected, use intelligent loading:

**Step 1: Read domain SKILL.md**
```bash
cat ~/.claude/skills/expertise/[domain]/SKILL.md 2>/dev/null
```

This loads core principles and routing guidance (~5k tokens).

**Step 2: Determine what references are needed**

Domain SKILL.md should contain a `<references_index>` section that maps planning contexts to specific references.

Example:
```markdown
<references_index>
**For database/persistence phases:** references/_create-plans-core-data.md, references/_create-plans-swift-concurrency.md
**For system integration:** references/_create-plans-appkit-integration.md
**Always useful:** references/_create-plans-swift-conventions.md
</references_index>
```

**Step 3: Load only relevant references**

Based on the phase being planned (from ROADMAP), load ONLY the references mentioned for that type of work.

```bash
# Example: Planning a database phase
cat ~/.claude/skills/expertise/macos-apps/references/_create-plans-core-data.md
cat ~/.claude/skills/expertise/macos-apps/references/_create-plans-swift-conventions.md
```

**Context efficiency:**
- SKILL.md only: ~5k tokens
- SKILL.md + selective references: ~8-12k tokens
- All references (old approach): ~20-27k tokens

Announce: "Loaded [domain] expertise ([X] references for [phase-type])."

**If domain skill not found:** Inform user and offer to proceed without domain expertise.

**If SKILL.md doesn't have references_index:** Fall back to loading all references with warning about context usage.
</load_domain>

<when_to_load>
Domain expertise should be loaded BEFORE:
- Creating roadmap (phases should be domain-appropriate)
- Planning phases (tasks must be domain-specific)

Domain expertise is NOT needed for:
- Creating brief (vision is domain-agnostic)
- Resuming from handoff (context already established)
- Transition between phases (just updating status)
</when_to_load>
</domain_expertise>

<intake>
Based on scan results, present context-aware options:

**If handoff found:**
```
Found handoff: .planning/phases/XX/.continue-here.md
[Summary of state from handoff]

1. Resume from handoff
2. Discard handoff, start fresh
3. Different action
```

**If planning structure exists:**
```
Project: [from BRIEF or directory]
Brief: [exists/missing]
Roadmap: [X phases defined]
Current: [phase status]

What would you like to do?
1. Plan next phase
2. Execute current phase
3. Create handoff (stopping for now)
4. View/update roadmap
5. Something else
```

**If no planning structure:**
```
No planning structure found.

What would you like to do?
1. Start new project (create brief)
2. Create roadmap from existing brief
3. Jump straight to phase planning
4. Get guidance on approach
```

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| "brief", "new project", "start", 1 (no structure) | `workflows/create-brief.md` |
| "roadmap", "phases", 2 (no structure) | `workflows/create-roadmap.md` |
| "phase", "plan phase", "next phase", 1 (has structure) | `workflows/plan-phase.md` |
| "chunk", "next tasks", "what's next" | `workflows/plan-chunk.md` |
| "execute", "run", "do it", "build it", 2 (has structure) | **EXIT SKILL** → Use `/run-plan <path>` slash command |
| "research", "investigate", "unknowns" | `workflows/research-phase.md` |
| "handoff", "pack up", "stopping", 3 (has structure) | `workflows/handoff.md` |
| "resume", "continue", 1 (has handoff) | `workflows/resume.md` |
| "transition", "complete", "done", "next" | `workflows/transition.md` |
| "milestone", "ship", "v1.0", "release" | `workflows/complete-milestone.md` |
| "guidance", "help", 4 | `workflows/get-guidance.md` |

**Critical:** Plan execution should NOT invoke this skill. Use `/run-plan` for context efficiency (skill loads ~20k tokens, /run-plan loads ~5-7k).

**After reading the workflow, follow it exactly.**
</routing>

<hierarchy>
The planning hierarchy (each level builds on previous):

```
BRIEF.md          → Human vision (you read this)
    ↓
ROADMAP.md        → Phase structure (overview)
    ↓
RESEARCH.md       → Research prompt (optional, for unknowns)
    ↓
FINDINGS.md       → Research output (if research done)
    ↓
PLAN.md           → THE PROMPT (Claude executes this)
    ↓
SUMMARY.md        → Outcome (existence = phase complete)
```

**Rules:**
- Roadmap requires Brief (or prompts to create one)
- Phase plan requires Roadmap (knows phase scope)
- PLAN.md IS the execution prompt
- SUMMARY.md existence marks phase complete
- Each level can look UP for context
</hierarchy>

<output_structure>
All planning artifacts go in `.planning/`:

```
.planning/
├── BRIEF.md                    # Human vision
├── ROADMAP.md                  # Phase structure + tracking
└── phases/
    ├── 01-foundation/
    │   ├── 01-01-PLAN.md       # Plan 1: Database setup
    │   ├── 01-01-SUMMARY.md    # Outcome (exists = done)
    │   ├── 01-02-PLAN.md       # Plan 2: API routes
    │   ├── 01-02-SUMMARY.md
    │   ├── 01-03-PLAN.md       # Plan 3: UI components
    │   └── .continue-here-01-03.md  # Handoff (temporary, if needed)
    └── 02-auth/
        ├── 02-01-RESEARCH.md   # Research prompt (if needed)
        ├── 02-01-FINDINGS.md   # Research output
        ├── 02-02-PLAN.md       # Implementation prompt
        └── 02-02-SUMMARY.md
```

**Naming convention:**
- Plans: `{phase}-{plan}-PLAN.md` (e.g., 01-03-PLAN.md)
- Summaries: `{phase}-{plan}-SUMMARY.md` (e.g., 01-03-SUMMARY.md)
- Phase folders: `{phase}-{name}/` (e.g., 01-foundation/)

Files sort chronologically. Related artifacts (plan + summary) are adjacent.
</output_structure>

<reference_index>

- Structure deep-dive (directory layout, hierarchy rules)
- Format specs (handoff, plan)
- Context-management patterns
- Domain-expertise authoring guide

Until then, follow the inline guidance in this SKILL.md.
</reference_index>

<templates_index>
All in `templates/`:

| Template | Purpose |
|----------|---------|
| brief.md | Project vision document with current state |
| roadmap.md | Phase structure with milestone groupings |
| phase-prompt.md | Executable phase prompt (PLAN.md) |
| research-prompt.md | Research prompt (RESEARCH.md) |
| summary.md | Phase outcome (SUMMARY.md) with deviations |
| milestone.md | Milestone entry for MILESTONES.md |
| issues.md | Deferred enhancements log (ISSUES.md) |
| continue-here.md | Context handoff format |
</templates_index>

<workflows_index>
All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| create-brief.md | Create project vision document |
| create-roadmap.md | Define phases from brief |
| plan-phase.md | Create executable phase prompt |
| execute-phase.md | Run phase prompt, create summary |
| research-phase.md | Create and run research prompt |
| plan-chunk.md | Plan immediate next tasks |
| transition.md | Mark phase complete, advance |
| complete-milestone.md | Mark shipped version, create milestone entry |
| handoff.md | Create context handoff for pausing |
| resume.md | Load handoff, restore context |
| get-guidance.md | Help decide planning approach |
</workflows_index>

<success_criteria>
Planning skill succeeds when:
- Context scan runs before intake
- Appropriate workflow selected based on state
- PLAN.md IS the executable prompt (not separate)
- Hierarchy is maintained (brief → roadmap → phase)
- Handoffs preserve full context for resumption
- Context limits are respected (auto-handoff at 10%)
- Deviations handled automatically per embedded rules
- All work (planned and discovered) fully documented
- Domain expertise loaded intelligently (SKILL.md + selective references, not all files)
- Plan execution uses /run-plan command (not skill invocation)
</success_criteria>

## Absorbed from `plan-author`

# plan-author

Backs the gate-injection step of `/shannon:plan-deep` and the planning phase of `/shannon:validate`. Adopts anthropic-skills/plan-author's evidence-compounding regression model + mock-detection preamble + platform-detection table, while preserving Shannon's iron rule (no "tests pass" gates) and gate-in-phase canonical structure.

Sibling: `skills/transform-validation-prompt/SKILL.md` retrofits gates into an external/raw prompt that didn't ship with them.

## Mock-detection preamble

**MANDATORY**: every PLAN.md produced by this skill begins with the following preamble. The preamble fires the no-fakes-discipline before any gate is read:

```markdown
## Mock-Detection Preamble

This plan validates against the REAL system. Any phase that satisfies its gate by:

- mocking the unit under test,
- stubbing the production dependency,
- returning hard-coded "success" fixtures,
- counting `toHaveBeenCalled` in lieu of an end-state assertion,
- declaring `tests pass` or `coverage ≥ N%` as the success criterion,

…is REFUSED. The evidence in `evidence/` must come from the real binary, the real server,
the real simulator, or the real CLI. See `skills/no-fakes-discipline/SKILL.md`.

If a real system cannot be exercised, the phase is incomplete. Halt and ask.
```

## Scope-with-gates discipline

Gates roughly **double** plan size. Plan **2-3 tasks per plan file, not 5-7**. Better 12 small validated plans than 4 large unvalidated ones.

A phase with a gate is the unit of validation. Atomicity protects both the plan and the gate from inflation.

## Behavior contract

1. Read a base plan (from `plan-author`) OR a feature brief.
2. Insert the mock-detection preamble at the top of the produced plan.
3. **Platform detection** (see table below): scan the base plan for surface keywords; map to evidence tool.
4. For each phase in the plan: derive a validation gate using the gate template.
5. **Evidence-compounding**: each phase's gate prerequisites include "Phase 1..N-1 still pass with their gates." Phase N gate exercises 1..N-1 regression before asserting N. Catches downstream regression.
6. Emit the gate inline in the phase file (NOT a separate file — gate is part of the phase, per Shannon convention).
7. Emit the **gate manifest tail** at the end of `plan.md` summarizing all gates.
8. Set up `evidence/` directory with the `vg{N}-{desc}.{ext}` naming convention.
9. Refuse if the base plan has a phase claiming "tests pass" or "test coverage" as a gate.

## Platform-detection table

Scan the base plan for these signals and choose the evidence tool. The first match wins; document the chosen platform in `plan.md` under a `## Platform` section.

| Signal in plan | Platform | Evidence tool | Evidence type |
|---|---|---|---|
| `.swift`, simulator, Xcode, iOS, watchOS, visionOS | iOS / macOS | xcodebuild, `xcrun simctl`, screenshot | screenshot, console log |
| `argparse`, `commander`, CLI binary, exit code | CLI | direct binary execution, exit-code capture | stdout, stderr, exit code |
| REST, GraphQL, OpenAPI, route handler, `app.get` | API | curl, httpie, fetch | response body, status, headers |
| React, Vue, Svelte, HTML page, browser | Web frontend | Playwright MCP, browser automation, screenshot | screenshot, DOM dump, console |
| both web + API + DB | Full-stack | combination of above | journey-level evidence |
| none of the above | Generic | bash + filesystem | stdout, file diff |

## Gate template (per phase)

```markdown
## Validation Gate (phase NN)

### Prerequisites (evidence-compounding)
- Phase 1..N-1 gates pass when re-exercised (regression check).
- Required artifacts present: <list>.

### Execute
- Real system to exercise: <server | simulator | CLI invocation>
- Journey to execute: <step-by-step actions>
- Command(s): <exact command>

### Capture
- Evidence saved to: `evidence/phase-NN/vg{N}-{desc}.{ext}`
- Filename convention: `vg{phase-NN}-{slug}.{ext}` (e.g., `vg02-login-flow.png`)

### Pass criteria
- <specific assertion 1, transcript-provable>
- <specific assertion 2>

### Review
- Reviewer: functional-validation skill | visual-inspection | api-validation | …
- Mock guard: gate REFUSED if evidence shows mock/stub/fixture in the path under test.

### Verdict
- PASS → proceed to next phase; archive evidence.
- FAIL → halt + refusal-discipline OR retry via `/shannon:fix`. Do NOT silently re-run.
```

## BAD / GOOD success criteria examples

| BAD (rejected) | GOOD (accepted) |
|---|---|
| "It works." | `curl -s localhost:3000/health` returns `{"status":"ok"}` with HTTP 200 |
| "Tests pass." | `xcodebuild test` exit 0 AND screenshot of running app shows logged-in state |
| "Login works." | curl POST /login with valid creds → 200 + JWT in body; curl GET /me with that JWT → 200 + user object |
| "UI looks good." | Playwright screenshot of /dashboard at 1280×800 matches `evidence/phase-03/vg03-dashboard.png` baseline (visual-inspection skill verdict PASS) |
| "Coverage ≥ 80%." | (REFUSED — coverage is not a real-system gate) |

## Evidence directory layout

```
plans/<date>-<slug>/
├── plan.md                          # mock-detection preamble + gate manifest tail
├── phase-01-<slug>.md               # gate inline
├── phase-02-<slug>.md               # gate inline + regression check on phase 1
├── ...
├── evidence/
│   ├── phase-01/
│   │   ├── vg01-build.log
│   │   └── vg01-health.json
│   ├── phase-02/
│   │   ├── vg02-login-flow.png
│   │   └── vg02-jwt-roundtrip.txt
│   └── ...
└── scripts/
    ├── collect-evidence.sh          # run per phase
    └── validate-gate.sh             # invoked by reviewer
```

## Gate manifest tail (appended to `plan.md`)

```markdown
## Gate Manifest

- Total gates: <N>
- Sequence: phase-01 → phase-02 → … → phase-NN
- All gates: BLOCKING (FAIL halts the plan).
- Evidence directory: `evidence/`
- Regression policy: phase-N includes phase-1..N-1 regression in its Prerequisites.
- Mock guard: enabled per gate.
- Platform: <ios | cli | api | web | full-stack | generic>
```

## When to use

- Phase 3 of `/shannon:plan-deep`.
- Phase 1 of `/shannon:validate` (planning).
- Standalone gate-injection on an existing plan that lacks them.

## When NOT to use

- Read-only changes (audits, doc updates).
- Pure refactor with no behavior change.

## Iron rules

- **No mock-based gates.** Gate must exercise real system.
- **No "tests pass" gates.** Refuse and rewrite.
- **Evidence path specified at gate-definition time** — not deferred.
- Gate is part of the phase, not a separate optional step.
- Mock-detection preamble is mandatory and not removable.
- Evidence-compounding: phase N regression-checks 1..N-1.
- Filename convention `vg{N}-{desc}.{ext}` is enforced.

## Cross-references

- `skills/transform-validation-prompt/SKILL.md` — sibling, retrofits gates into external prompts.
- `skills/no-fakes-discipline/SKILL.md` — mock-detection iron rule authority.
- `skills/functional-validation/SKILL.md` — default reviewer.
- `skills/visual-inspection/SKILL.md` — UI evidence reviewer.
- `skills/plan-author/SKILL.md` — produces the base plan this skill gates.
- `scripts/collect-evidence.sh`, `scripts/validate-gate.sh` — sibling scripts.
