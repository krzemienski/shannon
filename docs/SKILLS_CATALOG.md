# Skills catalog

33 curated v1 skills. Each lives at `skills/<name>/SKILL.md` with progressive-disclosure `references/*.md`.

Skills activate via Claude Code's skill-trigger system (matching `triggers:` against user prompts) or via explicit `Skill: <name>` invocation.

## Catalog

| Skill | Description | Triggers | required_hooks | refs/ |
|---|---|---|---|---|
| `autopilot-runner` | Full-lifecycle autopilot orchestrator for /shannon:autopilot. ALWAYS use when the user says "autopilot", "run autonomously", "Spec→Plan→Execute→QA→Val… | `autopilot`, `run autonomously`, `Spec to plan to execute to QA to validate`, … | — | 0 |
| `codebase-analysis` | Parallelized repo-wide context survey via the sciomc scientists pattern (3-7 parallel agents with [FINDING:][EVIDENCE:][CONFIDENCE:] tags), with cross… | `analyze codebase`, `repo context`, `module map`, … | — | 0 |
| `completion-gate` | Final completion gate evaluator for Shannon runs. ALWAYS use when the user says "completion gate", "ship gate", "evaluate completion", "final gate", o… | `completion gate`, `ship gate`, `evaluate completion`, … | `evidence-gate`, `post-action-discipline` | 1 |
| `consensus-engine` | Multi-validator agreement gate with 5-state synthesis and multi-round debate iteration. ALWAYS use when the user says "consensus validation", "validat… | `consensus validation`, `validate with N reviewers`, `agreement gate`, … | — | 0 |
| `create-meta-prompts` | Create optimized prompts for Claude-to-Claude pipelines with research, planning, and execution stages. Use when building prompts that produce outputs … |  | — | 11 |
| `dispatch-parallel` | Launch N sub-agents in parallel, sequential, or competitive mode with meta-judge verification and per-target retry. ALWAYS use when the user says "do … | `do in parallel`, `parallel subagents`, `fan out tasks`, … | `subagent-governance` | 0 |
| `evidence-gate` | 6-question refusal-discipline checklist applied before any completion claim. ALWAYS use when the user says "marking complete", "task complete", "ready… | `marking complete`, `task complete`, `ready to ship`, … | `evidence-gate`, `post-action-discipline` | 2 |
| `evidence-indexing` | Maintain README.md (purpose) and INDEX.md (artifact enumeration) in every evidence directory. ALWAYS use when the user says "index evidence", "write e… | `index evidence`, `write evidence index`, `evidence INDEX.md`, … | — | 0 |
| `full-functional-audit` | Comprehensive functional audit of every screen, button, popover, sheet, and backend endpoint in an app. Explores codebase to build interaction invento… |  | — | 9 |
| `functional-validation` | End-to-end no-mocks validation through real system execution. ALWAYS use when the user says "validate this", "prove it works", "functional validation"… | `validate this`, `prove it works`, `functional validation`, … | `post-action-discipline` | 11 |
| `gepetto` | Creates detailed, sectionized implementation plans through research, stakeholder interviews, and multi-LLM review. Use when planning features that nee… |  | — | 5 |
| `goal-condition-architect` | Transform any input into a single transcript-provable /goal completion condition. ALWAYS use when the user says "make a /goal", "set a goal", "goal co… | `make a /goal`, `set a goal`, `goal condition`, … | — | 0 |
| `goal-loop-orchestrator` | Run a /goal condition to completion unattended with transcript-evidence Iron Rule, stall detection, turn/token budgeting, and headless-mode support. A… | `run /goal to completion`, `headless run`, `unattended turns`, … | — | 0 |
| `interview-framework` | Pre-plan intake interview with intent-based depth scaling and 3-phase Understand/Propose/Confirm algorithm. ALWAYS use when the user says "interview m… | `interview me`, `ask me questions`, `intake`, … | — | 2 |
| `judge` | LLM-as-judge evaluation of subagent outputs across all /shannon:dispatch* commands. ALWAYS use when the user says "judge outputs", "evaluate candidate… | `judge outputs`, `evaluate candidates`, `rank subagent results`, … | — | 0 |
| `library-docs-fetch` | Fetch documentation for every third-party library identified in the codebase. Reads deps-summary.md from codebase-analysis output; for each library, p… | `fetch docs`, `pull library docs`, `grab third-party documentation`, … | — | 0 |
| `loop-runner` | Bounded do-verify-reflect loop with transcript-evidence Iron Rule, stall detection, iteration banner, checklist artifact, and post-iteration cleanup. … | `ralph loop`, `iterate until done`, `do-verify-reflect`, … | — | 1 |
| `memorize` | Persist a session-derived pattern to memory, gated by the learner's three-question quality gate (non-Googleable + codebase-specific + hard-won). ALWAY… | `remember this`, `save lesson`, `memorize pattern`, … | — | 3 |
| `multi-agent-patterns` | Design multi-agent architectures for complex tasks. Use when single-agent context limits are exceeded, when tasks decompose naturally into subtasks, o… | `multi-agent design`, `agent architecture`, `subagent patterns`, … | `subagent-governance` | 0 |
| `no-fakes-discipline` | Active iron-rule enforcement against fake substitutes for the real system. Prevents circumventing validation gates by creating mock/stub implementatio… | `add a fake`, `substitute the call`, `fixture-based response`, … | `block-fab-files`, `post-action-discipline` | 0 |
| `observability-report` | Shannon-specific log reader for session, hook, and run-state diagnostics. ALWAYS use when the user says "session trace", "shannon doctor", "session lo… | `session trace`, `shannon doctor`, `session log audit`, … | — | 1 |
| `plan-author` | Linear hierarchical plan author producing plan.md + phase-NN.md files. Plans-as-prompts framing — PLAN.md IS the prompt that executes the phase. ALWAY… | `plan this`, `create plan`, `implementation plan`, … | — | 12 |
| `prompt-engineering-patterns` | Master advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability in production. Use when optimizing prompts… |  | — | 14 |
| `python-agent-sdk` | Build production-ready AI agents with the Claude Agent SDK for Python. ALWAYS use when the user says "agent SDK", "ClaudeSDKClient", "Python SDK harne… | `agent SDK`, `ClaudeSDKClient`, `Python SDK harness`, … | — | 0 |
| `reflect` | Self-refinement pass on prior output with dominant-gap discipline (≤ 3 gaps, most blocking first), reflective tone, transcript-proof requirement on pr… | `reflect on this`, `self-refine`, `self-improve this`, … | — | 1 |
| `refusal-discipline` | When evidence is missing, write a structured REFUSAL.md and stop. ALWAYS use when the user says "evidence gap", "missing citation", "gate unmet", "ref… | `evidence gap`, `missing citation`, `gate unmet`, … | `evidence-gate` | 0 |
| `root-cause-tracing` | Five-whys cascade plus Ishikawa cause-and-effect diagram for root cause analysis. BEFORE/AFTER reality-check state documentation. VF task injection fo… | `why is X happening`, `root cause`, `five whys`, … | — | 0 |
| `session-handoff` | Comprehensive handoff documents for seamless Shannon session transfers. ALWAYS use when the user says "session handoff", "save session state", "contex… | `session handoff`, `save session state`, `context handoff`, … | — | 0 |
| `skill-inventory` | Enumerate every skill available in the user Claude Code environment by READING THE FILESYSTEM. Skills live as files at known paths — there is no MCP t… | `find skills for this`, `what skills do I have`, `which skills apply here`, … | — | 0 |
| `spec-workflow` | Spec-driven development pipeline (research → requirements → design → tasks → implement). ALWAYS use when the user says "build a feature", "create a sp… | `build a feature`, `create a spec`, `spec-driven development`, … | — | 1 |
| `team-coordinator` | Multi-teammate orchestration lead. ALWAYS use when the user says "spawn team", "coordinate teammates", "multi-agent team", "team charter", "team plan"… | `spawn team`, `coordinate teammates`, `multi-agent team`, … | `subagent-governance`, `stop-semantics` | 0 |
| `tree-of-thoughts` | Tree of Thoughts exploration with 8-phase structure — exploration, pruning meta-judge (parallel), pruning judges, expansion, evaluation meta-judge (pa… | `tree of thoughts`, `explore branches`, `ToT reasoning`, … | — | 0 |
| `visual-inspection` | Systematic visual QA protocol for UI screenshots — iOS (Apple HIG), web (WCAG 2.2), and cross-platform. Evaluate layout, typography, contrast, touch t… | `visual audit`, `screenshot review`, `HIG check`, … | — | 3 |

## How skills load

1. **Standalone** — Claude Code matches user prompts against each skill's `triggers:` list. On match, the SKILL.md content is added to the conversation context.
2. **Embedded (Architecture C)** — when a skill is declared in an agent's `manifest.yml` under `embedded_skills:`, the build script (`build/embed-skills.py`) inlines its SKILL.md body into the agent's AGENT.md.

A single skill can be BOTH standalone and embedded.

## Mandatory brownfield analysis (not opt-in)

Per the user's CLAUDE.md MANDATORY CODE BASE ANALYSIS rule, every `/shannon:plan` and `/shannon:cook` run on a non-empty repo automatically runs `/shannon:scope` (4 parallel streams) as Step 0. This is the default, not a feature.

### The 4 scope streams

- **`codebase-analysis`** — parallel 5-scientist deep repo survey
- **`skill-inventory`** — FILESYSTEM-BASED enumeration (no MCP — reads `~/.claude/skills/`, project skills, plugin caches, settings.json `enabledPlugins`)
- **`observability-report`** — session-history context
- **`library-docs-fetch`** — fetches authoritative docs for every third-party library identified by codebase-analysis (`llms.txt` → homepage docs → Context7 MCP → GitHub README → REFUSAL.md)

The `planner` agent's first Iron Rule is `MANDATORY CODE BASE ANALYSIS`. The `plan-author` skill refuses to produce plans without all 3 pre-flight skills' output.

## Doctor.py contract (now 10 checks)

`scripts/doctor.py` runs 10 mechanical checks including the v0.1.4-added **body-reference scans**:

- Check 9: Skill body references — every `\`Skill: <name>\`` and `\`Task: <agent>\`` in any SKILL.md must resolve to a real v1 entity
- Check 10: Agent body references — same scan for AGENT.md bodies (embedded blocks excluded to avoid double-counting)

These checks were the architect-flagged highest-leverage fix from the v0.1.4 audit. They caught the body-level phantom references that the v0.1.0-v0.1.3 doctor missed.

## Required hooks contract

8 skills declare `required_hooks:`. `scripts/doctor.py` cross-checks the contract.

## Cross-references

- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/QUICK_START.md](QUICK_START.md)
- [docs/CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](../README.md)
