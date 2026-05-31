---
name: create-meta-prompts
description: Create optimized prompts for Claude-to-Claude pipelines with research, planning, and execution stages. Use when building prompts that produce outputs for other prompts to consume, or when running multi-stage workflows (research -> plan -> implement).
---

<objective>
Create prompts optimized for Claude-to-Claude communication in multi-stage workflows. Outputs are structured with XML and metadata for efficient parsing by subsequent prompts.

Every execution produces a `SUMMARY.md` for quick human scanning without reading full outputs.

Each prompt gets its own folder in `.prompts/` with its output artifacts, enabling clear provenance and chain detection.
</objective>

<quick_start>
<workflow>
1. **Intake**: Determine purpose (Do/Plan/Research/Refine), gather requirements
2. **Chain detection**: Check for existing research/plan files to reference
3. **Generate**: Create prompt using purpose-specific patterns
4. **Save**: Create folder in `.prompts/{number}-{topic}-{purpose}/`
5. **Present**: Show decision tree for running
6. **Execute**: Run prompt(s) with dependency-aware execution engine
7. **Summarize**: Create SUMMARY.md for human scanning
</workflow>

<folder_structure>
```
.prompts/
├── 001-auth-research/
│   ├── completed/
│   │   └── 001-auth-research.md    # Prompt (archived after run)
│   ├── auth-research.md            # Full output (XML for Claude)
│   └── SUMMARY.md                  # Executive summary (markdown for human)
├── 002-auth-plan/
│   ├── completed/
│   │   └── 002-auth-plan.md
│   ├── auth-plan.md
│   └── SUMMARY.md
├── 003-auth-implement/
│   ├── completed/
│   │   └── 003-auth-implement.md
│   └── SUMMARY.md                  # Do prompts create code elsewhere
├── 004-auth-research-refine/
│   ├── completed/
│   │   └── 004-auth-research-refine.md
│   ├── archive/
│   │   └── auth-research-v1.md     # Previous version
│   └── SUMMARY.md
```
</folder_structure>
</quick_start>

<context>
Prompts directory: !`[ -d ./.prompts ] && echo "exists" || echo "missing"`
Existing research/plans: !`find ./.prompts -name "*-research.md" -o -name "*-plan.md" 2>/dev/null | head -10`
Next prompt number: !`ls -d ./.prompts/*/ 2>/dev/null | wc -l | xargs -I {} expr {} + 1`
</context>

<automated_workflow>

<step_0_intake_gate>
<title>Adaptive Requirements Gathering</title>

<critical_first_action>
**BEFORE analyzing anything**, check if context was provided.

IF no context provided (skill invoked without description):
→ **IMMEDIATELY use AskUserQuestion** with:

- header: "Purpose"
- question: "What is the purpose of this prompt?"
- options:
  - "Do" - Execute a task, produce an artifact
  - "Plan" - Create an approach, roadmap, or strategy
  - "Research" - Gather information or understand something
  - "Refine" - Improve an existing research or plan output

After selection, ask: "Describe what you want to accomplish" (they select "Other" to provide free text).

IF context was provided:
→ Check if purpose is inferable from keywords:
  - `implement`, `build`, `create`, `fix`, `add`, `refactor` → Do
  - `plan`, `roadmap`, `approach`, `strategy`, `decide`, `phases` → Plan
  - `research`, `understand`, `learn`, `gather`, `analyze`, `explore` → Research
  - `refine`, `improve`, `deepen`, `expand`, `iterate`, `update` → Refine

→ If unclear, ask the Purpose question above as first contextual question
→ If clear, proceed to adaptive_analysis with inferred purpose
</critical_first_action>

<adaptive_analysis>
Extract and infer:

- **Purpose**: Do, Plan, Research, or Refine
- **Topic identifier**: Kebab-case identifier for file naming (e.g., `auth`, `stripe-payments`)
- **Complexity**: Simple vs complex (affects prompt depth)
- **Prompt structure**: Single vs multiple prompts
- **Target** (Refine only): Which existing output to improve

If topic identifier not obvious, ask:
- header: "Topic"
- question: "What topic/feature is this for? (used for file naming)"
- Let user provide via "Other" option
- Enforce kebab-case (convert spaces/underscores to hyphens)

For Refine purpose, also identify target output from `.prompts/*/` to improve.
</adaptive_analysis>

<chain_detection>
Scan `.prompts/*/` for existing `*-research.md` and `*-plan.md` files.

If found:
1. List them: "Found existing files: auth-research.md (in 001-auth-research/), stripe-plan.md (in 005-stripe-plan/)"
2. Use AskUserQuestion:
   - header: "Reference"
   - question: "Should this prompt reference any existing research or plans?"
   - options: List found files + "None"
   - multiSelect: true

Match by topic keyword when possible (e.g., "auth plan" → suggest auth-research.md).
</chain_detection>

<contextual_questioning>
Generate 2-4 questions using AskUserQuestion based on purpose and gaps.

Load questions from: [references/question-bank.md](references/question-bank.md)

Route by purpose:
- Do → artifact type, scope, approach
- Plan → plan purpose, format, constraints
- Research → depth, sources, output format
- Refine → target selection, feedback, preservation
</contextual_questioning>

<decision_gate>
After receiving answers, present decision gate using AskUserQuestion:

- header: "Ready"
- question: "Ready to create the prompt?"
- options:
  - "Proceed" - Create the prompt with current context
  - "Ask more questions" - I have more details to clarify
  - "Let me add context" - I want to provide additional information

Loop until "Proceed" selected.
</decision_gate>

<finalization>
After "Proceed" selected, state confirmation:

"Creating a {purpose} prompt for: {topic}
Folder: .prompts/{number}-{topic}-{purpose}/
References: {list any chained files}"

Then proceed to generation.
</finalization>
</step_0_intake_gate>

<step_1_generate>
<title>Generate Prompt</title>

Load purpose-specific patterns:
- Do: [references/do-patterns.md](references/do-patterns.md)
- Plan: [references/plan-patterns.md](references/plan-patterns.md)
- Research: [references/research-patterns.md](references/research-patterns.md)
- Refine: [references/refine-patterns.md](references/refine-patterns.md)

Load intelligence rules: [references/intelligence-rules.md](references/intelligence-rules.md)

<prompt_structure>
All generated prompts include:

1. **Objective**: What to accomplish, why it matters
2. **Context**: Referenced files (@), dynamic context (!)
3. **Requirements**: Specific instructions for the task
4. **Output specification**: Where to save, what structure
5. **Metadata requirements**: For research/plan outputs, specify XML metadata structure
6. **SUMMARY.md requirement**: All prompts must create a SUMMARY.md file
7. **Success criteria**: How to know it worked

For Research and Plan prompts, output must include:
- `<confidence>` - How confident in findings
- `<dependencies>` - What's needed to proceed
- `<open_questions>` - What remains uncertain
- `<assumptions>` - What was assumed

All prompts must create `SUMMARY.md` with:
- **One-liner** - Substantive description of outcome
- **Version** - v1 or iteration info
- **Key Findings** - Actionable takeaways
- **Files Created** - (Do prompts only)
- **Decisions Needed** - What requires user input
- **Blockers** - External impediments
- **Next Step** - Concrete forward action
</prompt_structure>

<file_creation>
1. Create folder: `.prompts/{number}-{topic}-{purpose}/`
2. Create `completed/` subfolder
3. Write prompt to: `.prompts/{number}-{topic}-{purpose}/{number}-{topic}-{purpose}.md`
4. Prompt instructs output to: `.prompts/{number}-{topic}-{purpose}/{topic}-{purpose}.md`
</file_creation>
</step_1_generate>

<step_2_present>
<title>Present Decision Tree</title>

After saving prompt(s), present inline (not AskUserQuestion):

<single_prompt_presentation>
```
Prompt created: .prompts/{number}-{topic}-{purpose}/{number}-{topic}-{purpose}.md

What's next?

1. Run prompt now
2. Review/edit prompt first
3. Save for later
4. Other

Choose (1-4): _
```
</single_prompt_presentation>

<multi_prompt_presentation>
```
Prompts created:
- .prompts/001-auth-research/001-auth-research.md
- .prompts/002-auth-plan/002-auth-plan.md
- .prompts/003-auth-implement/003-auth-implement.md

Detected execution order: Sequential (002 references 001 output, 003 references 002 output)

What's next?

1. Run all prompts (sequential)
2. Review/edit prompts first
3. Save for later
4. Other

Choose (1-4): _
```
</multi_prompt_presentation>
</step_2_present>

<step_3_execute>
<title>Execution Engine</title>

<execution_modes>
<single_prompt>
Straightforward execution of one prompt.

1. Read prompt file contents
2. Spawn Task agent with subagent_type="general-purpose"
3. Include in task prompt:
   - The complete prompt contents
   - Output location: `.prompts/{number}-{topic}-{purpose}/{topic}-{purpose}.md`
4. Wait for completion
5. Validate output (see validation section)
6. Archive prompt to `completed/` subfolder
7. Report results with next-step options
</single_prompt>

<sequential_execution>
For chained prompts where each depends on previous output.

1. Build execution queue from dependency order
2. For each prompt in queue:
   a. Read prompt file
   b. Spawn Task agent
   c. Wait for completion
   d. Validate output
   e. If validation fails → stop, report failure, offer recovery options
   f. If success → archive prompt, continue to next
3. Report consolidated results

<progress_reporting>
Show progress during execution:
```
Executing 1/3: 001-auth-research... ✓
Executing 2/3: 002-auth-plan... ✓
Executing 3/3: 003-auth-implement... (running)
```
</progress_reporting>
</sequential_execution>

<parallel_execution>
For independent prompts with no dependencies.

1. Read all prompt files
2. **CRITICAL**: Spawn ALL Task agents in a SINGLE message
   - This is required for true parallel execution
   - Each task includes its output location
3. Wait for all to complete
4. Validate all outputs
5. Archive all prompts
6. Report consolidated results (successes and failures)

<failure_handling>
Unlike sequential, parallel continues even if some fail:
- Collect all results
- Archive successful prompts
- Report failures with details
- Offer to retry failed prompts
</failure_handling>
</parallel_execution>

<mixed_dependencies>
For complex DAGs (e.g., two parallel research → one plan).

1. Analyze dependency graph from @ references
2. Group into execution layers:
   - Layer 1: No dependencies (run parallel)
   - Layer 2: Depends only on layer 1 (run after layer 1 completes)
   - Layer 3: Depends on layer 2, etc.
3. Execute each layer:
   - Parallel within layer
   - Sequential between layers
4. Stop if any dependency fails (downstream prompts can't run)

<example>
```
Layer 1 (parallel): 001-api-research, 002-db-research
Layer 2 (after layer 1): 003-architecture-plan
Layer 3 (after layer 2): 004-implement
```
</example>
</mixed_dependencies>
</execution_modes>

<dependency_detection>
<automatic_detection>
Scan prompt contents for @ references to determine dependencies:

1. Parse each prompt for `@.prompts/{number}-{topic}/` patterns
2. Build dependency graph
3. Detect cycles (error if found)
4. Determine execution order

<inference_rules>
If no explicit @ references found, infer from purpose:
- Research prompts: No dependencies (can parallel)
- Plan prompts: Depend on same-topic research
- Do prompts: Depend on same-topic plan

Override with explicit references when present.
</inference_rules>
</automatic_detection>

<missing_dependencies>
If a prompt references output that doesn't exist:

1. Check if it's another prompt in this session (will be created)
2. Check if it exists in `.prompts/*/` (already completed)
3. If truly missing:
   - Warn user: "002-auth-plan references auth-research.md which doesn't exist"
   - Offer: Create the missing research prompt first? / Continue anyway? / Cancel?
</missing_dependencies>
</dependency_detection>

<validation>
<output_validation>
After each prompt completes, verify success:

1. **File exists**: Check output file was created
2. **Not empty**: File has content (> 100 chars)
3. **Metadata present** (for research/plan): Check for required XML tags
   - `<confidence>`
   - `<dependencies>`
   - `<open_questions>`
   - `<assumptions>`
4. **SUMMARY.md exists**: Check SUMMARY.md was created
5. **SUMMARY.md complete**: Has required sections (Key Findings, Decisions Needed, Blockers, Next Step)
6. **One-liner is substantive**: Not generic like "Research completed"

<validation_failure>
If validation fails:
- Report what's missing
- Offer options:
  - Retry the prompt
  - Continue anyway (for non-critical issues)
  - Stop and investigate
</validation_failure>
</output_validation>
</validation>

<failure_handling>
<sequential_failure>
Stop the chain immediately:
```
✗ Failed at 2/3: 002-auth-plan

Completed:
- 001-auth-research ✓ (archived)

Failed:
- 002-auth-plan: Output file not created

Not started:
- 003-auth-implement

What's next?
1. Retry 002-auth-plan
2. View error details
3. Stop here (keep completed work)
4. Other
```
</sequential_failure>

<parallel_failure>
Continue others, report all results:
```
Parallel execution completed with errors:

✓ 001-api-research (archived)
✗ 002-db-research: Validation failed - missing <confidence> tag
✓ 003-ui-research (archived)

What's next?
1. Retry failed prompt (002)
2. View error details
3. Continue without 002
4. Other
```
</parallel_failure>
</failure_handling>

<archiving>
<archive_timing>
- **Sequential**: Archive each prompt immediately after successful completion
  - Provides clear state if execution stops mid-chain
- **Parallel**: Archive all at end after collecting results
  - Keeps prompts available for potential retry

<archive_operation>
Move prompt file to completed subfolder:
```bash
mv .prompts/{number}-{topic}-{purpose}/{number}-{topic}-{purpose}.md \
   .prompts/{number}-{topic}-{purpose}/completed/
```

Output file stays in place (not moved).
</archive_operation>
</archiving>

<result_presentation>
<single_result>
```
✓ Executed: 001-auth-research
✓ Created: .prompts/001-auth-research/SUMMARY.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auth Research Summary

**JWT with jose library and httpOnly cookies recommended**

## Key Findings
• jose outperforms jsonwebtoken with better TypeScript support
• httpOnly cookies required (localStorage is XSS vulnerable)
• Refresh rotation is OWASP standard

## Decisions Needed
None - ready for planning

## Blockers
None

## Next Step
Create auth-plan.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What's next?
1. Create planning prompt (auth-plan)
2. View full research output
3. Done
4. Other
```

Display the actual SUMMARY.md content inline so user sees findings without opening files.
</single_result>

<chain_result>
```
✓ Chain completed: auth workflow

Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
001-auth-research
**JWT with jose library and httpOnly cookies recommended**
Decisions: None • Blockers: None

002-auth-plan
**4-phase implementation: types → JWT core → refresh → tests**
Decisions: Approve 15-min token expiry • Blockers: None

003-auth-implement
**JWT middleware complete with 6 files created**
Decisions: Review before Phase 2 • Blockers: None
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All prompts archived. Full summaries in .prompts/*/SUMMARY.md

What's next?
1. Review implementation
2. Run tests
3. Create new prompt chain
4. Other
```

For chains, show condensed one-liner from each SUMMARY.md with decisions/blockers flagged.
</chain_result>
</result_presentation>

<special_cases>
<re_running_completed>
If user wants to re-run an already-completed prompt:

1. Check if prompt is in `completed/` subfolder
2. Move it back to parent folder
3. Optionally backup existing output: `{output}.bak`
4. Execute normally
</re_running_completed>

<output_conflicts>
If output file already exists:

1. For re-runs: Backup existing → `{filename}.bak`
2. For new runs: Should not happen (unique numbering)
3. If conflict detected: Ask user - Overwrite? / Rename? / Cancel?
</output_conflicts>

<commit_handling>
After successful execution:

1. Do NOT auto-commit (user controls git workflow)
2. Mention what files were created/modified
3. User can commit when ready

Exception: If user explicitly requests commit, stage and commit:
- Output files created
- Prompts archived
- Any implementation changes (for Do prompts)
</commit_handling>

<recursive_prompts>
If a prompt's output includes instructions to create more prompts:

1. This is advanced usage - don't auto-detect
2. Present the output to user
3. User can invoke skill again to create follow-up prompts
4. Maintains user control over prompt creation
</recursive_prompts>
</special_cases>
</step_3_execute>

</automated_workflow>

<reference_guides>
**Prompt patterns by purpose:**
- [references/do-patterns.md](references/do-patterns.md) - Execution prompts + output structure
- [references/plan-patterns.md](references/plan-patterns.md) - Planning prompts + plan.md structure
- [references/research-patterns.md](references/research-patterns.md) - Research prompts + research.md structure
- [references/refine-patterns.md](references/refine-patterns.md) - Iteration prompts + versioning

**Shared templates:**
- [references/summary-template.md](references/summary-template.md) - SUMMARY.md structure and field requirements
- [references/metadata-guidelines.md](references/metadata-guidelines.md) - Confidence, dependencies, open questions, assumptions

**Supporting references:**
- [references/question-bank.md](references/question-bank.md) - Intake questions by purpose
- [references/intelligence-rules.md](references/intelligence-rules.md) - Extended thinking, parallel tools, depth decisions
</reference_guides>

<success_criteria>
**Prompt Creation:**
- Intake gate completed with purpose and topic identified
- Chain detection performed, relevant files referenced
- Prompt generated with correct structure for purpose
- Folder created in `.prompts/` with correct naming
- Output file location specified in prompt
- SUMMARY.md requirement included in prompt
- Metadata requirements included for Research/Plan outputs
- Quality controls included for Research outputs (verification checklist, QA, pre-submission)
- Streaming write instructions included for Research outputs
- Decision tree presented

**Execution (if user chooses to run):**
- Dependencies correctly detected and ordered
- Prompts executed in correct order (sequential/parallel/mixed)
- Output validated after each completion
- SUMMARY.md created with all required sections
- One-liner is substantive (not generic)
- Failed prompts handled gracefully with recovery options
- Successful prompts archived to `completed/` subfolder
- SUMMARY.md displayed inline in results
- Results presented with decisions/blockers flagged

**Research Quality (for Research prompts):**
- Verification checklist completed
- Quality report distinguishes verified from assumed claims
- Sources consulted listed with URLs
- Confidence levels assigned to findings
- Critical claims verified with official documentation
</success_criteria>


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `deepen-prompt-plan`

# Deepen Prompt & Plan

<objective>
Take any existing plan, prompt, or instruction set and make it stronger through targeted analysis, research, and rewriting. This is a second-pass confidence check — not a rewrite from scratch.

The input already exists. The question is: "Is this grounded enough for the complexity and risk involved?"

This skill identifies weak sections, runs targeted research for those sections, injects functional validation where missing, and strengthens the document in place — all using proper semantic XML formatting.
</objective>

<what_this_skill_does>
- Scores confidence gaps across every section of the input document
- Selects the weakest 2-5 sections for targeted deepening
- Runs research (web search, documentation lookup, codebase analysis) for weak sections
- Injects or strengthens functional validation gates (Iron Rule: no mocks, real-system proof)
- Reformats output with clean semantic XML where appropriate
- Preserves the document's existing structure and intent
- Produces a stronger document, not a longer one
</what_this_skill_does>

<what_this_skill_does_not_do>
- Rewrite documents from scratch (use create-plans or create-meta-prompts for that)
- Add implementation code (pseudo-code and DSL sketches are allowed)
- Invent new requirements or change scope without surfacing them as open questions
- Turn plans into implementation scripts
- Replace the original author's intent or architectural decisions
</what_this_skill_does_not_do>

<essential_principles>

<principle name="stress_test_not_inflate">
Deepening increases justified confidence. It does not make the document longer for its own sake. If a section is already strong, leave it alone. Every addition must earn its place by closing a specific confidence gap.
</principle>

<principle name="selective_depth">
Focus on the weakest 2-5 sections rather than enriching everything. A plan with 3 rock-solid sections and 2 strengthened weak points is better than a plan where every section got a thin coat of paint.
</principle>

<principle name="iron_rule_enforcement">
If the document describes something that will be built and run, it must have validation gates. The Iron Rule applies: if the real system doesn't work, fix the real system. Never create mocks, stubs, test doubles, or test files. Every gate must have specific, observable, measurable PASS criteria defined BEFORE execution.
</principle>

<principle name="xml_structure">
Use semantic XML tags for structured content. Tags should be descriptive and self-documenting. Use attributes for metadata. Nest tags to represent hierarchy. This makes documents parseable by both humans and downstream Claude instances.

Example:
```xml
<task id="1" priority="high">
  <description>Create the API endpoint</description>
  <validation_gate id="VG-1" blocking="true">
    <pass_criteria>HTTP 201 with valid JSON body containing "id" field</pass_criteria>
    <evidence_command>curl -s -X POST localhost:3000/api/users | tee evidence/vg1.json | jq .</evidence_command>
  </validation_gate>
</task>
```
</principle>

<principle name="research_before_opinion">
When a section needs strengthening, prefer evidence over opinion. Check documentation, search for current best practices, analyze the codebase. A decision backed by "the official docs recommend X because Y" is stronger than "X seems like a good idea."
</principle>

<principle name="preserve_planning_boundary">
No implementation code. No git command choreography. No exact test command recipes (validation gate commands are the exception — those ARE the test). Pseudo-code sketches and architecture diagrams are allowed.
</principle>

</essential_principles>

<workflow>

**Phase narration (mandatory):** At each phase boundary, tell the user which phase you are entering and what it does. This is NOT optional — the user must always know where they are in the 6-phase process. Keep it to one sentence. Examples:
- "**Phase 0: Loading and classifying** — reading the document and building a risk profile."
- "**Phase 2: Scoring confidence gaps** — identifying which sections are weakest."
- "**Phase 5: Synthesizing** — rewriting the selected sections with research findings."

## Phase 0: Load and Classify

### 0.1 — Locate the Document

Accept the document path as an argument, from the conversation context, or by scanning common locations:

```bash
# Check common plan/prompt locations
find . -maxdepth 3 -name "*.md" \( -path "*/plans/*" -o -path "*/.planning/*" -o -path "*/.prompts/*" -o -path "*/PLAN.md" -o -path "*/PROMPT.md" \) 2>/dev/null | head -20
```

If multiple candidates exist, ask the user which document to deepen. Do not proceed without a valid file path.

Read the document completely. If it references an origin document (brief, roadmap, spec), read that too.

### 0.2 — Classify Document Type and Risk

Determine the document type:

| Type | Signals | Deepening Focus |
|------|---------|-----------------|
| **Implementation Plan** | Tasks, phases, file paths, verification | Sequencing, validation gates, system impact |
| **Prompt / Instructions** | Role definition, workflows, output specs | Clarity, edge cases, validation criteria |
| **Roadmap** | Phases, milestones, dependencies | Phase gate criteria, risk treatment, ordering |
| **Research Plan** | Questions, sources, methodology | Completeness, source quality, gap coverage |
| **Agent Instructions** | Tools, workflows, decision trees | Edge case handling, failure modes, validation |

Build a risk profile. These are high-risk signals that warrant deeper treatment:

- Authentication, authorization, or security-sensitive behavior
- Payments, billing, or financial flows
- Data migrations, backfills, or persistent data changes
- External APIs or third-party integrations
- Privacy, compliance, or user data handling
- Cross-platform parity or multi-surface behavior
- Significant rollout, monitoring, or operational concerns
- Prompts that will be executed autonomously without human review

### 0.3 — Decide Whether to Deepen

Not every document needs deepening. Use this heuristic:

- **Simple / Low-risk**: Usually skip unless user explicitly requests it. Offer to proceed to execution instead.
- **Moderate complexity**: Often benefits when 1-2 important sections are thin.
- **High complexity or high risk**: Almost always benefits from a targeted second pass.

If the document is already well-grounded, say so. Recommend moving to execution. If the user insists, do a light pass on at most 1-2 sections.

## Phase 1: Parse Structure

Map the document into its constituent sections. Look for these or their equivalents:

<section_taxonomy>
**For Plans:**
- Overview / Objective
- Context / Background
- Requirements / Success Criteria
- Scope Boundaries
- Research / Sources
- Key Decisions (with rationale)
- Open Questions
- Technical Design (pseudo-code, diagrams, data flow)
- Tasks / Implementation Units
- System-Wide Impact
- Risks & Dependencies
- Validation / Verification
- Operational Notes

**For Prompts / Instructions:**
- Role / Identity
- Objective / Purpose
- Context / Background
- Workflows / Phases
- Decision Trees / Routing
- Output Specifications
- Validation Criteria / Success Criteria
- Edge Cases / Error Handling
- Constraints / Boundaries
- Examples (few-shot)

**For Roadmaps:**
- Vision / Goals
- Phase Definitions
- Phase Gate Criteria
- Dependencies Between Phases
- Risk Register
- Milestone Definitions
</section_taxonomy>

Collect metadata: which sections exist, which are absent, what references are cited, what validation exists.

## Phase 2: Score Confidence Gaps

For each section, compute a confidence gap score.

Load detailed scoring rubric: [references/_deepen-prompt-plan-confidence-scoring.md](references/_deepen-prompt-plan-confidence-scoring.md)

**Scoring formula per section:**

```
gap_score = trigger_count + risk_bonus + critical_section_bonus
```

Where:
- **trigger_count** = number of checklist problems that apply (from the rubric)
- **risk_bonus** = +1 if the topic is high-risk AND this section is materially relevant to the risk
- **critical_section_bonus** = +1 for Key Decisions, Tasks/Implementation, System Impact, Risks, Validation, or Workflows in moderate-to-complex documents

**Selection threshold:**
- Score ≥ 2: candidate for deepening
- Score = 1 in a high-risk domain AND section is materially important: also a candidate
- Select the top **2-5 sections** by score
- For light-pass deepening (user insisted on simple doc): cap at **1-2 sections**

**Present the scoring table to the user before proceeding.** Transparency about what was selected and why builds trust and lets the user adjust the selection. Show each section with its trigger count, bonuses, total score, and which specific triggers fired. Example:

```
Confidence Gap Scores:
| Section         | Triggers | Risk | Critical | Total | Deepen? |
|-----------------|----------|------|----------|-------|---------|
| Key Decisions   |    2     |  +1  |    +1    |   4   |  YES    |
|   → Decisions stated without tradeoff analysis                  |
|   → Obvious alternatives not addressed                          |
| Risks           |    2     |  +1  |    +1    |   4   |  YES    |
|   → Risks listed without mitigation                             |
|   → Security risks absent where they obviously apply            |
| Validation      |    2     |  +1  |    +1    |   4   |  YES    |
|   → No validation gates present                                 |
|   → PASS criteria vague                                         |
| Context         |    1     |   0  |     0    |   1   |  no     |
| Overview        |    0     |   0  |     0    |   0   |  no     |
```

Ask: "These are the sections I'll deepen. Want to adjust before I proceed?" If the user is running this non-interactively (pipeline, subagent), proceed with the top-scored sections automatically.

## Phase 3: Research Weak Sections

For each selected section, choose the smallest useful research approach. Do not research everything — only what closes the identified gap.

Load research strategies: [references/_deepen-prompt-plan-research-strategies.md](references/_deepen-prompt-plan-research-strategies.md)

**Research priority order** (prefer earlier sources):
1. **Codebase analysis** — grep, find, read existing code for patterns and conventions
2. **Existing documentation** — README, CLAUDE.md, architecture docs in the repo
3. **Origin documents** — brief, spec, roadmap that the plan derives from
4. **Official documentation** — framework docs, API references, library guides (use web search or context7 MCP)
5. **External best practices** — industry patterns, security guidelines, performance benchmarks

**Research execution:**
- Run searches in parallel when independent
- Keep findings focused: strongest evidence only
- For each finding, note: what it changes in the plan, and where the evidence came from
- If findings conflict, prefer repo-grounded evidence over generic advice; prefer official docs over blog posts

**Present a compact research summary before proceeding.** The user should see what evidence was found and how it will inform the rewrite. Use this format:

```xml
<research_summary>
  <finding section="Key Decisions" source="OWASP Session Management Cheat Sheet">
    JWT with short-lived access tokens + refresh rotation is recommended for stateless APIs.
    Impact: Adds rationale and source to D1 decision.
  </finding>
  <finding section="Risks" source="codebase: src/middleware/logger.ts">
    Logging middleware already redacts sensitive fields (line 23).
    Impact: Risk R3 mitigation can reference existing safeguard.
  </finding>
</research_summary>
```

Keep it brief — 1-3 lines per finding. The goal is transparency, not a research report. If no research was needed (gap closeable from the document itself), say so and skip.

## Phase 4: Inject or Strengthen Validation

This phase applies specifically to documents that describe something that will be built and executed. Skip for pure research plans or documentation.

Load deepening patterns: [references/_deepen-prompt-plan-deepening-patterns.md](references/_deepen-prompt-plan-deepening-patterns.md)

**If the document has NO validation gates:**

Inject the mock detection preamble at the top:

```xml
<mock_detection_protocol>
Before executing any task, check intent:
- Creating .test.*, _test.*, *Tests.*, test_* files → STOP
- Importing mock libraries → STOP
- Creating in-memory databases → STOP
- Adding TEST_MODE or NODE_ENV=test flags → STOP
Fix the REAL system instead. No exceptions.
</mock_detection_protocol>
```

Then inject validation gates after each task or logical unit:

```xml
<validation_gate id="VG-{N}" blocking="true">
  <prerequisites>[Dependencies started + health checked]</prerequisites>
  <execute>[Real system interaction]</execute>
  <capture>[Commands that save output to evidence/ files]</capture>
  <pass_criteria>[Specific, observable, measurable — defined NOW not during execution]</pass_criteria>
  <review>[READ the evidence: Read tool for images, cat for text, jq for JSON]</review>
  <verdict>PASS → next task | FAIL → fix real system → re-run from prerequisites</verdict>
  <mock_guard>IF tempted to mock → STOP → fix real system</mock_guard>
</validation_gate>
```

Append a gate manifest at the end:

```xml
<gate_manifest>
  <total_gates>{N}</total_gates>
  <sequence>VG-1 → VG-2 → ... → VG-N</sequence>
  <policy>All gates BLOCKING. No advancement on FAIL.</policy>
  <evidence_dir>evidence/</evidence_dir>
  <regression>If ANY gate FAILS: fix → re-run from failed gate → do NOT skip</regression>
</gate_manifest>
```

**If the document HAS validation gates:**

Audit existing gates against quality standards:
- Are PASS criteria specific and measurable (not "it works")?
- Does every gate capture evidence to disk (not ephemeral)?
- Does every gate review evidence (not just check file exists)?
- Is mock detection present?
- Are there phase-level regression gates (Phase 2 re-validates Phase 1)?

Strengthen any gates that fail these checks.

## Phase 5: Synthesize and Rewrite

Strengthen only the selected sections. Keep the document coherent and preserve its overall structure.

**Size budget:** Deepening should make the document stronger, not bloated. Use these heuristics:
- Documents under 500 words: up to 3x growth is acceptable (thin docs need the most enrichment)
- Documents 500-1500 words: aim for under 2x growth
- Documents over 1500 words: aim for under 30% growth — at this size, every addition must displace or replace weak content
- If the output is growing beyond budget, you are enriching too many sections. Tighten selection.

**Allowed changes:**
- Clarify or strengthen decision rationale
- Tighten requirements trace or success criteria
- Reorder or split tasks when sequencing is weak
- Add missing references, file paths, or verification outcomes
- Expand risk treatment, system impact, or operational notes where justified
- Reclassify open questions (resolved vs deferred) when evidence supports it
- Inject or strengthen validation gates per Phase 4
- Add or strengthen XML structure for machine-parseable sections
- Add `<confidence>`, `<assumptions>`, `<open_questions>` metadata where valuable

**Forbidden changes:**
- Adding implementation code (imports, exact signatures, framework syntax)
- Rewriting the entire document from scratch
- Inventing new product requirements or changing scope silently
- Adding generic "insights" subsections that don't close a specific gap
- Removing existing content that was correct

**XML formatting guidance:**
Use semantic XML for structured content. Tags should be self-documenting. Attributes carry metadata. Nest for hierarchy. Keep prose sections as regular markdown — XML is for structured, parseable content only.

```xml
<task id="2" depends_on="1" platform="ios">
  <description>Implement the authentication flow</description>
  <files>Sources/Auth/AuthManager.swift, Sources/Auth/TokenStore.swift</files>
  <approach>Follow existing AuthProvider protocol pattern in Sources/Auth/</approach>
  <validation_gate id="VG-2" blocking="true">
    <pass_criteria>
      Simulator screenshot shows login screen → enter credentials → 
      dashboard appears with user name displayed in nav bar
    </pass_criteria>
  </validation_gate>
</task>
```

## Phase 6: Final Checks and Write

Before writing the updated document:

1. **Stronger, not longer** — confirm additions close specific gaps and the document stays within the size budget from Phase 5
2. **Planning boundary intact** — no implementation code leaked in
3. **Correct sections targeted** — the weakest sections were actually the ones deepened
4. **Origin intent preserved** — the document still serves its original purpose
5. **Validation gates present** — if building something, every task has a gate with measurable criteria
6. **XML well-formed** — tags open and close correctly, attributes are quoted

Write the updated document in place by default. If the user requests a separate file, append `-deepened` before `.md`.

</workflow>

<post_deepening>
After writing, present next steps:

**If substantive changes were made:**
1. **View diff** — show what changed and why
2. **Deepen further** — run another targeted pass on specific sections
3. **Execute** — begin implementing the plan
4. **Transform to gated prompt** — convert the full document into a validation-gated execution prompt (use transform-validation-prompt skill)

**If no substantive changes were warranted:**
- Say the document is already well-grounded
- Recommend execution as the next step
</post_deepening>

<reference_index>
All in `references/`:

- **confidence-scoring.md** — Detailed checklist triggers for every section type (plans, prompts, roadmaps), scoring rubric, and examples of gap identification
- **research-strategies.md** — Research source priority, execution patterns, conflict resolution, and evidence quality standards
- **deepening-patterns.md** — Platform-specific validation gate templates, XML formatting patterns, prompt strengthening patterns, and before/after examples
</reference_index>

<success_criteria>
A deepened document succeeds when:
- Only weak sections were modified (selective, not blanket)
- Every addition closes a specific, identified confidence gap
- Decisions have evidence-backed rationale (not opinion)
- Validation gates have specific, observable, measurable PASS criteria
- No mocks, stubs, or test files introduced
- XML structure is well-formed and semantically meaningful
- The document is stronger and roughly the same size (not bloated)
- Original intent and scope are preserved
- Open questions are surfaced, not silently resolved
</success_criteria>
