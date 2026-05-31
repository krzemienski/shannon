---
name: prompt-engineering-patterns
description: Master advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability in production. Use when optimizing prompts, improving LLM outputs, or designing production prompt templates.
---

# Prompt Engineering Patterns

> **Optional 3rd-party MCPs**: the patterns below cite `mcp__serena__*`, `mcp__filesystem__*`, `mcp__git__*`, and `mcp__sequential-thinking__*`. These are NOT Shannon-provided. If your environment doesn't have them connected, the patterns degrade to native CC tools (Read/Grep/Bash). Don't assume availability.


Master advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability.

## When to Use This Skill

- Designing complex prompts for production LLM applications
- Optimizing prompt performance and consistency
- Implementing structured reasoning patterns (chain-of-thought, tree-of-thought)
- Building few-shot learning systems with dynamic example selection
- Creating reusable prompt templates with variable interpolation
- Debugging and refining prompts that produce inconsistent outputs
- Implementing system prompts for specialized AI assistants

## Core Capabilities

### 1. Few-Shot Learning
- Example selection strategies (semantic similarity, diversity sampling)
- Balancing example count with context window constraints
- Constructing effective demonstrations with input-output pairs
- Dynamic example retrieval from knowledge bases
- Handling edge cases through strategic example selection

### 2. Chain-of-Thought Prompting
- Step-by-step reasoning elicitation
- Zero-shot CoT with "Let's think step by step"
- Few-shot CoT with reasoning traces
- Self-consistency techniques (sampling multiple reasoning paths)
- Verification and validation steps

### 3. Prompt Optimization
- Iterative refinement workflows
- A/B testing prompt variations
- Measuring prompt performance metrics (accuracy, consistency, latency)
- Reducing token usage while maintaining quality
- Handling edge cases and failure modes

### 4. Template Systems
- Variable interpolation and formatting
- Conditional prompt sections
- Multi-turn conversation templates
- Role-based prompt composition
- Modular prompt components

### 5. System Prompt Design
- Setting model behavior and constraints
- Defining output formats and structure
- Establishing role and expertise
- Safety guidelines and content policies
- Context setting and background information

## Quick Start

```python
from prompt_optimizer import PromptTemplate, FewShotSelector

# Define a structured prompt template
template = PromptTemplate(
    system="You are an expert SQL developer. Generate efficient, secure SQL queries.",
    instruction="Convert the following natural language query to SQL:\n{query}",
    few_shot_examples=True,
    output_format="SQL code block with explanatory comments"
)

# Configure few-shot learning
selector = FewShotSelector(
    examples_db="sql_examples.jsonl",
    selection_strategy="semantic_similarity",
    max_examples=3
)

# Generate optimized prompt
prompt = template.render(
    query="Find all users who registered in the last 30 days",
    examples=selector.select(query="user registration date filter")
)
```

## Key Patterns

### Progressive Disclosure
Start with simple prompts, add complexity only when needed:

1. **Level 1**: Direct instruction
   - "Summarize this article"

2. **Level 2**: Add constraints
   - "Summarize this article in 3 bullet points, focusing on key findings"

3. **Level 3**: Add reasoning
   - "Read this article, identify the main findings, then summarize in 3 bullet points"

4. **Level 4**: Add examples
   - Include 2-3 example summaries with input-output pairs

### Instruction Hierarchy
```
[System Context] → [Task Instruction] → [Examples] → [Input Data] → [Output Format]
```

### Error Recovery
Build prompts that gracefully handle failures:
- Include fallback instructions
- Request confidence scores
- Ask for alternative interpretations when uncertain
- Specify how to indicate missing information

## Best Practices

1. **Be Specific**: Vague prompts produce inconsistent results
2. **Show, Don't Tell**: Examples are more effective than descriptions
3. **Test Extensively**: Evaluate on diverse, representative inputs
4. **Iterate Rapidly**: Small changes can have large impacts
5. **Monitor Performance**: Track metrics in production
6. **Version Control**: Treat prompts as code with proper versioning
7. **Document Intent**: Explain why prompts are structured as they are

## Common Pitfalls

- **Over-engineering**: Starting with complex prompts before trying simple ones
- **Example pollution**: Using examples that don't match the target task
- **Context overflow**: Exceeding token limits with excessive examples
- **Ambiguous instructions**: Leaving room for multiple interpretations
- **Ignoring edge cases**: Not testing on unusual or boundary inputs

## Integration Patterns

### With RAG Systems
```python
# Combine retrieved context with prompt engineering
prompt = f"""Given the following context:
{retrieved_context}

{few_shot_examples}

Question: {user_question}

Provide a detailed answer based solely on the context above. If the context doesn't contain enough information, explicitly state what's missing."""
```

### With Validation
```python
# Add self-verification step
prompt = f"""{main_task_prompt}

After generating your response, verify it meets these criteria:
1. Answers the question directly
2. Uses only information from provided context
3. Cites specific sources
4. Acknowledges any uncertainty

If verification fails, revise your response."""
```

## Performance Optimization

### Token Efficiency
- Remove redundant words and phrases
- Use abbreviations consistently after first definition
- Consolidate similar instructions
- Move stable content to system prompts

### Latency Reduction
- Minimize prompt length without sacrificing quality
- Use streaming for long-form outputs
- Cache common prompt prefixes
- Batch similar requests when possible

## Resources

- **references/few-shot-learning.md**: Deep dive on example selection and construction
- **references/chain-of-thought.md**: Advanced reasoning elicitation techniques
- **references/prompt-optimization.md**: Systematic refinement workflows
- **references/prompt-templates.md**: Reusable template patterns
- **references/system-prompts.md**: System-level prompt design
- **assets/prompt-template-library.md**: Battle-tested prompt templates
- **assets/few-shot-examples.json**: Curated example datasets
- **scripts/optimize-prompt.py**: Automated prompt optimization tool

## Success Metrics

Track these KPIs for your prompts:
- **Accuracy**: Correctness of outputs
- **Consistency**: Reproducibility across similar inputs
- **Latency**: Response time (P50, P95, P99)
- **Token Usage**: Average tokens per request
- **Success Rate**: Percentage of valid outputs
- **User Satisfaction**: Ratings and feedback

## Next Steps

1. Review the prompt template library for common patterns
2. Experiment with few-shot learning for your specific use case
3. Implement prompt versioning and A/B testing
4. Set up automated evaluation pipelines
5. Document your prompt engineering decisions and learnings


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `prompt-engineer`

# Prompt Engineer

Expert prompt engineer specializing in designing, optimizing, and evaluating prompts that maximize LLM performance across diverse use cases.

## When to Use This Skill

- Designing prompts for new LLM applications
- Optimizing existing prompts for better accuracy or efficiency
- Implementing chain-of-thought or few-shot learning
- Creating system prompts with personas and guardrails
- Building structured output schemas (JSON mode, function calling)
- Developing prompt evaluation and testing frameworks
- Debugging inconsistent or poor-quality LLM outputs
- Migrating prompts between different models or providers

## Core Workflow

1. **Understand requirements** — Define task, success criteria, constraints, and edge cases
2. **Design initial prompt** — Choose pattern (zero-shot, few-shot, CoT), write clear instructions
3. **Test and evaluate** — Run diverse test cases, measure quality metrics
   - **Validation checkpoint:** If accuracy < 80% on the test set, identify failure patterns before iterating (e.g., ambiguous instructions, missing examples, edge case gaps)
4. **Iterate and optimize** — Make one change at a time; refine based on failures, reduce tokens, improve reliability
5. **Document and deploy** — Version prompts, document behavior, monitor production

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Prompt Patterns | `references/_prompt-engineer-prompt-patterns.md` | Zero-shot, few-shot, chain-of-thought, ReAct |
| Optimization | `references/_prompt-engineer-prompt-optimization.md` | Iterative refinement, A/B testing, token reduction |
| Evaluation | `references/_prompt-engineer-evaluation-frameworks.md` | Metrics, test suites, automated evaluation |
| Structured Outputs | `references/_prompt-engineer-structured-outputs.md` | JSON mode, function calling, schema design |
| System Prompts | `references/_prompt-engineer-system-prompts.md` | Persona design, guardrails, injection defense |
| Context Management | `references/_prompt-engineer-context-management.md` | Attention budget, degradation patterns, context optimization |

## Prompt Examples

### Zero-shot vs. Few-shot

**Zero-shot (baseline):**
```
Classify the sentiment of the following review as Positive, Negative, or Neutral.

Review: {{review}}
Sentiment:
```

**Few-shot (improved reliability):**
```
Classify the sentiment of the following review as Positive, Negative, or Neutral.

Review: "The battery life is incredible, lasts all day."
Sentiment: Positive

Review: "Stopped working after two weeks. Very disappointed."
Sentiment: Negative

Review: "It arrived on time and matches the description."
Sentiment: Neutral

Review: {{review}}
Sentiment:
```

### Before/After Optimization

**Before (vague, inconsistent outputs):**
```
Summarize this document.

{{document}}
```

**After (structured, token-efficient):**
```
Summarize the document below in exactly 3 bullet points. Each bullet must be one sentence and start with an action verb. Do not include opinions or information not present in the document.

Document:
{{document}}

Summary:
```

## Constraints

### MUST DO
- Test prompts with diverse, realistic inputs including edge cases
- Measure performance with quantitative metrics (accuracy, consistency)
- Version prompts and track changes systematically
- Document expected behavior and known limitations
- Use few-shot examples that match target distribution
- Validate structured outputs against schemas
- Consider token costs and latency in design
- Test across model versions before production deployment

### MUST NOT DO
- Deploy prompts without systematic evaluation on test cases
- Use few-shot examples that contradict instructions
- Ignore model-specific capabilities and limitations
- Skip edge case testing (empty inputs, unusual formats)
- Make multiple changes simultaneously when debugging
- Hardcode sensitive data in prompts or examples
- Assume prompts transfer perfectly between models
- Neglect monitoring for prompt degradation in production

## Output Templates

When delivering prompt work, provide:
1. Final prompt with clear sections (role, task, constraints, format)
2. Test cases and evaluation results
3. Usage instructions (temperature, max tokens, model version)
4. Performance metrics and comparison with baselines
5. Known limitations and edge cases

## Coverage Note

Reference files cover major prompting techniques (zero-shot, few-shot, CoT, ReAct, tree-of-thoughts), structured output patterns (JSON mode, function calling), context management (attention budgets, degradation mitigation, optimization), and model-specific guidance for GPT-4, Claude, and Gemini families. Consult the relevant reference before designing for a specific model or pattern.

## Absorbed from `prompt-improver`

# Prompt Improver Skill

## Purpose

Transform vague, ambiguous prompts into actionable, well-defined requests through systematic research and targeted clarification. This skill is invoked when the hook has already determined a prompt needs enrichment.

## When This Skill is Invoked

**Automatic invocation:**
- UserPromptSubmit hook evaluates prompt
- Hook determines prompt is vague (missing specifics, context, or clear target)
- Hook invokes this skill to guide research and questioning

**Manual invocation:**
- To enrich a vague prompt with research-based questions
- When building or testing prompt evaluation systems
- When prompt lacks sufficient context even with conversation history

**Assumptions:**
- Prompt has already been identified as vague
- Evaluation phase is complete (done by hook)
- Proceed directly to research and clarification

## Core Workflow

This skill follows a 4-phase approach to prompt enrichment:

### Phase 1: Research

Create a dynamic research plan using TodoWrite before asking questions.

**Research Plan Template:**
1. **Check conversation history first** - Avoid redundant exploration if context already exists
2. **Review codebase** if needed:
   - Task/Explore for architecture and project structure
   - Grep/Glob for specific patterns, related files
   - Check git log for recent changes
   - Search for errors, failing tests, TODO/FIXME comments
3. **Gather additional context** as needed:
   - Read local documentation files
   - WebFetch for online documentation
   - WebSearch for best practices, common approaches, current information
4. **Document findings** to ground questions in actual project context

**Critical Rules:**
- NEVER skip research
- Check conversation history before exploring codebase
- Questions must be grounded in actual findings, not assumptions or base knowledge

For detailed research strategies, patterns, and examples, see [references/_prompt-improver-research-strategies.md](references/_prompt-improver-research-strategies.md).

### Phase 2: Generate Targeted Questions

Based on research findings, formulate 1-6 questions that will clarify the ambiguity.

**Question Guidelines:**
- **Grounded**: Every option comes from research (codebase findings, documentation, common patterns)
- **Specific**: Avoid vague options like "Other approach"
- **Multiple choice**: Provide 2-4 concrete options per question
- **Focused**: Each question addresses one decision point
- **Contextual**: Include brief explanations of trade-offs

**Number of Questions:**
- **1-2 questions**: Simple ambiguity (which file? which approach?)
- **3-4 questions**: Moderate complexity (scope + approach + validation)
- **5-6 questions**: Complex scenarios (major feature with multiple decision points)

For question templates, effective patterns, and examples, see [references/_prompt-improver-question-patterns.md](references/_prompt-improver-question-patterns.md).

### Phase 3: Get Clarification

Use the AskUserQuestion tool to present your research-grounded questions.

**AskUserQuestion Format:**
```
- question: Clear, specific question ending with ?
- header: Short label (max 12 chars) for UI display
- multiSelect: false (unless choices aren't mutually exclusive)
- options: Array of 2-4 specific choices from research
  - label: Concise choice text (1-5 words)
  - description: Context about this option (trade-offs, implications)
```

**Important:** Always include multiSelect field (true/false). User can always select "Other" for custom input.

### Phase 4: Execute with Context

Proceed with the original user request using:
- Original prompt intent
- Clarification answers from user
- Research findings and context
- Conversation history

Execute the request as if it had been clear from the start.

## Examples

### Example 1: Skill Invocation → Research → Questions → Execution

**Hook evaluation:** Determined prompt is vague
**Original prompt:** "fix the bug"
**Skill invoked:** Yes (prompt lacks target and context)

**Research plan:**
1. Check conversation history for recent errors
2. Explore codebase for failing tests
3. Grep for TODO/FIXME comments
4. Check git log for recent problem areas

**Research findings:**
- Recent conversation mentions login failures
- auth.py:145 has try/catch swallowing errors
- Tests failing in test_auth.py

**Questions generated:**
1. Which bug are you referring to?
   - Login authentication failure (auth.py:145)
   - Session timeout issues (session.py:89)
   - Other

**User answer:** Login authentication failure

**Execution:** Fix the error handling in auth.py:145 that's causing login failures

### Example 2: Clear Prompt (Skill Not Invoked)

**Original prompt:** "Refactor the getUserById function in src/api/users.ts to use async/await instead of promises"

**Hook evaluation:** Passes all checks
- Specific target: getUserById in src/api/users.ts
- Clear action: refactor to async/await
- Success criteria: use async/await instead of promises

**Skill invoked:** No (prompt is clear, proceeds immediately without skill invocation)

For comprehensive examples showing various prompt types and transformations, see [references/_prompt-improver-examples.md](references/_prompt-improver-examples.md).

## Key Principles

1. **Assume Vagueness**: Skill is only invoked for vague prompts (evaluation done by hook)
2. **Research First**: Always gather context before formulating questions
3. **Ground Questions**: Use research findings, not assumptions or base knowledge
4. **Be Specific**: Provide concrete options from actual codebase/context
5. **Stay Focused**: Max 1-6 questions, each addressing one decision point
6. **Systematic Approach**: Follow 4-phase workflow (Research → Questions → Clarify → Execute)

## Progressive Disclosure

This SKILL.md contains the core workflow and essentials. For deeper guidance:

- **Research strategies**: [references/_prompt-improver-research-strategies.md](references/_prompt-improver-research-strategies.md)
- **Question patterns**: [references/_prompt-improver-question-patterns.md](references/_prompt-improver-question-patterns.md)
- **Comprehensive examples**: [references/_prompt-improver-examples.md](references/_prompt-improver-examples.md)

Load these references only when detailed guidance is needed on specific aspects of prompt improvement.

## Absorbed from `optimize-prompt`

# Optimize Prompt - Raw Input to Production-Ready Prompts

Transform any raw input into well-structured, guideline-compliant prompts that follow Opus 4.5 and Sonnet 4.5 best practices with mandatory workflow injection.

---

## Overview

**Optimize Prompt** takes messy input and outputs clean, structured prompts that:
- Follow Opus 4.5 and Sonnet 4.5 guidelines
- Include mandatory workflows (skills inventory, MCP tools, ultrathinking)
- Apply semantic XML formatting
- Inject critical rules (never write tests unless asked, always read code first, use Serena MCP)
- Detect and recommend relevant skills and MCP tools
- Ask for clarification when needed
- Output to file OR return formatted prompt

### What This Skill Does:
✅ Accepts raw input (voice transcripts, semi-structured notes, ideas, file paths)
✅ Applies Opus 4.5 and Sonnet 4.5 best practices automatically
✅ Injects mandatory workflows (skills inventory, MCP tools, ultrathinking)
✅ Formats with clean semantic XML tags
✅ Detects relevant skills and MCP tools for the task
✅ Validates guideline compliance before output
✅ Outputs to file OR returns formatted prompt

### What This Skill Does NOT Do:
❌ Execute the prompt after generating it
❌ Implement code or create files (only creates the prompt)
❌ Replace human judgment on task complexity

---

## Core Functionality

### Input Types Supported

1. **Voice Rambles** - Unstructured spoken thoughts transcribed to text
2. **Semi-Structured Ideas** - Partial prompts with missing context
3. **File Path Requests** - "Analyze this file" → Full structured task
4. **Incomplete Prompts** - Missing workflows, rules, or structure

### Transformation Process

#### Phase 1: Input Analysis
1. Detect input type (voice/idea/file/incomplete)
2. Extract intent and goal
3. Identify task type (code analysis, feature implementation, debugging, etc.)
4. Determine complexity level (simple, moderate, complex)

#### Phase 2: Guideline Application
Apply relevant guidelines from:
- **Opus 4.5**: Explicit instructions, context addition, code exploration, long-horizon reasoning
- **Sonnet 4.5**: Parallel tool calling, balanced verbosity, context awareness
- **Claude Code**: CLAUDE.md usage, tool allowlists, MCP integration, git workflows

#### Phase 3: Workflow Injection
Inject mandatory workflows:
1. **Skills Inventory** - Check and load relevant skills
2. **MCP Tools Inventory** - Identify specialized MCP tools to use
3. **Ultrathinking Framework** - For complex multi-step problems
4. **Mandatory Rules** - Critical rules that must be followed

#### Phase 4: Structure & Format
1. Apply semantic XML tags
2. Organize into logical sections
3. Add context and constraints
4. Include success criteria

#### Phase 5: Quality Validation
1. Check completeness (all sections present)
2. Verify guideline compliance
3. Validate mandatory workflows included
4. Confirm actionable instructions

---

## Synthesized Guidelines

### From Opus 4.5

**Key Principles:**
- **Be Explicit** - Clear, detailed instructions prevent ambiguity
- **Add Context** - Background information improves performance
- **Avoid Overengineering** - Simplest solution that works is best
- **Code Exploration** - ALWAYS read code before proposing changes
- **Minimize Hallucinations** - Investigate before answering
- **Long-Horizon Reasoning** - Track state for multi-step tasks
- **Tool Usage Precision** - Use tools deliberately, not speculatively

**Implementation:**
```xml
<context>
[Provide domain, technical background, constraints]
</context>

<exploration_required>
Before proposing changes:
1. Read existing code with Read, Grep, or Serena MCP
2. Understand current implementation
3. Identify actual issue (not assumed)
</exploration_required>
```

### From Sonnet 4.5

**Key Principles:**
- **Parallel Tool Calling** - Call independent tools simultaneously
- **Balanced Verbosity** - Not too terse, not too verbose
- **Context Awareness** - Use provided context effectively
- **Efficient Communication** - Clear, direct responses

**Implementation:**
```xml
<tool_usage_strategy>
When multiple independent operations needed:
- Call tools in parallel (same message)
- Example: git status + git diff + git log (parallel)
- Sequential only when dependency exists (mkdir before cp)
</tool_usage_strategy>
```

### From Claude Code Best Practices

**Key Principles:**
- **CLAUDE.md First** - Check for project-specific guidance
- **Tool Allowlists** - Use MCP tools over bash when available
- **Skills Usage** - Inventory and load relevant skills
- **Git Workflows** - Proper commit messages and PR creation
- **Specific Instructions** - Clear, actionable tasks
- **Course Correction** - Ask clarifying questions when unclear

---

## Mandatory Workflow Templates

### Template 1: Skills Inventory

```xml
<skills_inventory>
**MANDATORY: Complete this inventory before starting ANY task**

Step 1: List Available Skills
List all skills you have access to in your current session.

Step 2: Identify Matching Skills
Which skills are relevant to this task?
- [skill-name]: [why it's relevant]

Step 3: Load Skills
Use the Skill tool to load each relevant skill:
- Skill: [skill-name]

Step 4: Follow Guidance
Execute the loaded skills' instructions exactly as specified.

Relevant Skills for This Task:
[To be filled during enhancement]
</skills_inventory>
```

### Template 2: MCP Tools Inventory

```xml
<mcp_tools_inventory>
**MANDATORY: Complete this inventory before using ANY tools**

Step 1: Check Available MCP Servers
List MCP servers connected to your session.

Step 2: Identify Specialized Tools
Which MCP tools are better than bash equivalents?

Examples:
- Use mcp__serena__find_symbol for code search (NOT grep)
- Use mcp__serena__get_symbols_overview for file structure (NOT cat)
- Use mcp__filesystem__* for file operations (NOT cat/sed)
- Use mcp__git__* for git operations (NOT raw git commands)
- Use mcp__sequential-thinking for complex reasoning

Step 3: Prefer MCP Over Bash
When both options exist, ALWAYS use MCP tools.

Recommended MCP Tools for This Task:
[To be filled during enhancement]
</mcp_tools_inventory>
```

### Template 3: Ultrathinking Framework

```xml
<thinking_framework>
**Use for complex multi-step problems requiring systematic reasoning**

WHEN TO USE:
- Architectural decisions
- Debugging complex issues
- Multiple valid approaches exist
- Optimization problems
- Large refactorings
- Root cause analysis

HOW TO USE:
1. Call mcp__sequential-thinking__sequentialthinking tool
2. Set thoughtNumber=1, estimate totalThoughts
3. Think through each step incrementally
4. Generate hypothesis when appropriate
5. Verify hypothesis against constraints
6. Revise if needed (set isRevision=true, revisesThought=N)
7. Continue until confident solution found
8. Set nextThoughtNeeded=false only when truly done

TRIGGER PHRASES:
- "think" - Basic thinking budget
- "think hard" - Increased budget
- "think harder" - Higher budget
- "ultrathink" - Maximum budget

[Apply when task complexity requires it]
</thinking_framework>
```

### Template 4: Mandatory Rules

```xml
<mandatory_rules>
<rule id="1" priority="CRITICAL">
**NEVER write unit tests unless explicitly requested by the user**

Reason: Tests are often unnecessary overhead; user will ask if needed.

Violation Detection: If you find yourself writing test files (.test.*, .spec.*, *_test.*)
without explicit user request, STOP and ask for confirmation.
</rule>

<rule id="2" priority="CRITICAL">
**NEVER propose code changes without reading the existing code first**

Tools to Use:
- Read: For known file paths
- Grep: For searching patterns
- Glob: For finding files by pattern
- Serena MCP (preferred): find_symbol, get_symbols_overview, find_referencing_symbols

Reason: Proposing changes without understanding creates bugs and breaks things.

Violation Detection: If you're about to suggest code changes but haven't read
the relevant files, STOP and read them first.
</rule>

<rule id="3" priority="HIGH">
**ALWAYS use Serena MCP for code analysis when available**

Preferred Tools:
- find_symbol: Find classes, functions, methods by name
- get_symbols_overview: Understand file structure
- find_referencing_symbols: Find where code is used
- search_for_pattern: Regex search across codebase
- replace_symbol_body: Precise symbol-level edits

Reason: Serena MCP provides symbol-level understanding far superior to grep/find.

When to Use: Any code analysis, refactoring, or understanding task.
</rule>

<rule id="4" priority="HIGH">
**ALWAYS complete the skills inventory before starting tasks**

Process:
1. List available skills
2. Identify relevant skills
3. Load skills with Skill tool
4. Follow skill guidance

Reason: Skills contain proven patterns that prevent mistakes and save time.
</rule>

<rule id="5" priority="HIGH">
**ALWAYS complete MCP tools inventory before using tools**

Process:
1. Check available MCP servers
2. Identify specialized MCP tools
3. Prefer MCP over bash equivalents

Reason: MCP tools are more reliable and powerful than bash equivalents.
</rule>

<rule id="6" priority="MEDIUM">
**ALWAYS use ultrathinking for complex problems**

Triggers:
- Architecture decisions
- Debugging complex issues
- Optimization challenges
- Refactoring large codebases
- Migration planning

Tool: mcp__sequential-thinking__sequentialthinking

Reason: Complex problems need structured multi-step reasoning.
</rule>

<rule id="7" priority="MEDIUM">
**ALWAYS use sequential thinking for debugging and root cause analysis**

Process:
1. State the problem clearly
2. Generate hypotheses incrementally
3. Test each hypothesis
4. Revise based on evidence
5. Continue until root cause found

Reason: Debugging requires systematic hypothesis generation and testing.
</rule>
</mandatory_rules>
```

---

## Enhancement Framework

### Step 1: Detect Input Type

**Voice Ramble Detection:**
- Long unstructured text
- Conversational tone
- "Um", "like", "you know" filler words
- Stream of consciousness style

**Semi-Structured Detection:**
- Has some structure but missing pieces
- Partial XML tags or markdown
- Incomplete sections

**File Path Detection:**
- Contains file paths (/path/to/file)
- References to "analyze this", "check that file"
- Single sentence with file reference

**Incomplete Prompt Detection:**
- Missing mandatory workflows
- No skills inventory
- No MCP tools check
- Missing mandatory rules

### Step 2: Extract Core Intent

**Questions to Answer:**
1. What is the user trying to accomplish?
2. What type of task is this? (code analysis, feature, debug, optimization, etc.)
3. What context is missing?
4. What constraints should be applied?
5. What skills might be relevant?
6. What MCP tools should be used?

**Intent Categories:**
- Code Analysis: Understand existing code
- Feature Implementation: Build something new
- Bug Fix: Diagnose and fix issues
- Refactoring: Improve code structure
- Optimization: Improve performance
- Documentation: Create or update docs
- Testing: Write or run tests (rare - must be explicit)

### Step 3: Apply Guidelines

For each intent category, apply relevant guidelines:

**Code Analysis:**
```xml
<task_type>Code Analysis</task_type>

<guidelines>
- Opus 4.5: Code exploration REQUIRED (Rule #2)
- Opus 4.5: Investigate before answering
- Serena MCP: Use find_symbol, get_symbols_overview
- Mandatory: Skills inventory, MCP tools inventory
</guidelines>

<workflow>
1. Complete skills inventory
2. Complete MCP tools inventory
3. Read target files with Serena MCP (get_symbols_overview)
4. Analyze symbols and structure
5. Provide detailed analysis
</workflow>
```

**Feature Implementation:**
```xml
<task_type>Feature Implementation</task_type>

<guidelines>
- Opus 4.5: Be explicit with requirements
- Opus 4.5: Add context (domain, constraints)
- Opus 4.5: Avoid overengineering
- Sonnet 4.5: Parallel tool calling when possible
- Mandatory: Skills inventory, MCP tools inventory
- Mandatory: Read existing code first (Rule #2)
</guidelines>

<workflow>
1. Complete skills inventory
2. Complete MCP tools inventory
3. Read existing code to understand patterns
4. Design feature (use ultrathinking if complex)
5. Implement incrementally
6. NEVER write tests unless user explicitly asks
</workflow>
```

**Bug Fix/Debugging:**
```xml
<task_type>Debugging</task_type>

<guidelines>
- Opus 4.5: Minimize hallucinations - investigate first
- Opus 4.5: Long-horizon reasoning for complex bugs
- Ultrathinking: REQUIRED for complex debugging (Rule #7)
- Serena MCP: Use find_referencing_symbols to trace usage
- Mandatory: Skills inventory, MCP tools inventory
</guidelines>

<workflow>
1. Complete skills inventory
2. Complete MCP tools inventory
3. Use sequential thinking (mcp__sequential-thinking)
   - Generate hypotheses incrementally
   - Test each hypothesis
   - Revise based on evidence
4. Read relevant code with Serena MCP
5. Identify root cause
6. Propose fix
</workflow>
```

### Step 4: Inject Workflows

For EVERY enhanced prompt, inject:
1. Skills inventory template
2. MCP tools inventory template
3. Ultrathinking framework (if complex task detected)
4. All mandatory rules

### Step 5: Recommend Skills & Tools

**Skill Recommendation Logic:**

```
IF task = "code analysis" OR "refactoring":
  → Check for: serena MCP, systematic-debugging

IF task = "feature implementation":
  → Check for: test-driven-development (if tests needed)

IF task = "git operations":
  → Check for: git-commit-helper

IF task = "AWS" OR "cloud":
  → Check for: aws-solution-architect

IF task = "content" OR "research":
  → Check for: content-trend-researcher

IF task = "prompt creation":
  → Check for: prompt-factory
```

**MCP Tool Recommendation Logic:**

```
IF task involves code analysis:
  → Recommend: mcp__serena__* tools
  → Specifically: find_symbol, get_symbols_overview, find_referencing_symbols

IF task involves file operations:
  → Recommend: mcp__filesystem__* tools
  → Instead of: cat, sed, awk

IF task involves git:
  → Recommend: mcp__git__* tools
  → Instead of: raw git commands

IF task is complex/architectural:
  → Recommend: mcp__sequential-thinking__sequentialthinking
```

### Step 6: Structure Output

**XML Structure:**

```xml
<enhanced_prompt>

<task_summary>
[Clear, concise summary of what needs to be done]
</task_summary>

<context>
<domain>[Domain/area: web development, data science, etc.]</domain>
<technical_context>[Technologies involved]</technical_context>
<constraints>[Limitations, requirements, standards]</constraints>
</context>

<skills_inventory>
[Mandatory skills inventory template - filled with detected skills]
</skills_inventory>

<mcp_tools_inventory>
[Mandatory MCP tools inventory - filled with recommended tools]
</mcp_tools_inventory>

<thinking_framework>
[Ultrathinking framework if task is complex]
</thinking_framework>

<mandatory_rules>
[All 7 mandatory rules - always included]
</mandatory_rules>

<workflow>
<phase_1>
[First phase of work with specific steps]
</phase_1>

<phase_2>
[Second phase with dependencies on phase 1]
</phase_2>

<phase_3>
[Third phase - completion and validation]
</phase_3>
</workflow>

<success_criteria>
[How to know the task is complete]
</success_criteria>

<execution_trigger>
You are now configured to execute this task following all guidelines,
mandatory workflows, and rules specified above.

Begin by completing the skills inventory, then proceed through each phase.
</execution_trigger>

</enhanced_prompt>
```

### Step 7: Quality Validation

**Validation Checklist:**

1. ✓ **Completeness Check**
   - Task summary present?
   - Context provided?
   - Skills inventory included?
   - MCP tools inventory included?
   - Mandatory rules included?
   - Workflow defined?
   - Success criteria specified?

2. ✓ **Guideline Compliance**
   - Opus 4.5 principles applied?
   - Sonnet 4.5 principles applied?
   - Claude Code best practices applied?

3. ✓ **Mandatory Workflows**
   - Skills inventory template present?
   - MCP tools inventory template present?
   - Ultrathinking framework (if needed)?
   - All 7 mandatory rules present?

4. ✓ **Skill Detection**
   - Relevant skills identified?
   - Skills listed in inventory section?

5. ✓ **Tool Detection**
   - Relevant MCP tools identified?
   - Tools listed in MCP inventory section?
   - Preferred over bash equivalents?

6. ✓ **Actionability**
   - Workflow has clear, executable steps?
   - No ambiguous instructions?
   - Success criteria measurable?

7. ✓ **XML Validity**
   - All tags properly opened and closed?
   - Proper nesting?
   - No syntax errors?

---

## Usage

### When to Use This Skill

**Use optimize-prompt when you have:**
- Voice transcripts that need structure
- Incomplete ideas that need workflows
- Simple file path requests that need full context
- Prompts missing mandatory workflows
- Raw thoughts that need guideline compliance

**Examples:**

**Example 1: Voice Ramble**
```
Input:
"So yeah I was thinking we should like analyze the auth module
because it's been giving us some weird errors and I'm not really
sure what's going on there um maybe we could look at the login
function and see if there's something wrong with the token validation"

Output:
[Structured XML prompt with:
- Task: Debug authentication module
- Skills: systematic-debugging, serena
- MCP tools: mcp__serena__find_symbol, mcp__sequential-thinking
- Workflow: Investigation → Root cause → Fix
- All mandatory rules included]
```

**Example 2: File Path Request**
```
Input:
"Analyze src/auth/login.ts"

Output:
[Structured XML prompt with:
- Task: Code analysis of login.ts
- Skills inventory check
- MCP tools: mcp__serena__get_symbols_overview
- Workflow: Read → Analyze → Report findings
- Mandatory rule: Read code first (Rule #2)]
```

**Example 3: Incomplete Idea**
```
Input:
"Build a new API endpoint for user registration"

Output:
[Structured XML prompt with:
- Task: Feature implementation - user registration API
- Context: REST API, authentication domain
- Skills inventory check
- MCP tools inventory check
- Workflow: Understand existing → Design → Implement
- Mandatory rules (especially Rule #1: no tests unless asked)
- Success criteria: Endpoint works, follows patterns]
```

### Invocation

**Simple Invocation:**
```
"Enhance this prompt: [raw input]"
```

**With Clarification:**
```
If input is ambiguous, skill will ask:
- What's the primary goal?
- What context is important?
- Are there constraints?
- Should output go to a file?
```

**With File Output:**
```
"Enhance this prompt and save to prompts/my-task.xml: [raw input]"
```

### Output Options

**Option 1: Return Formatted Prompt**
Default behavior - return enhanced prompt in response for immediate use.

**Option 2: Save to File**
When user specifies file path, save enhanced prompt to that location:
```bash
prompts/enhanced-task.xml
tasks/debugging-auth.xml
.claude/prompts/feature-registration.xml
```

---

## Enhancement Examples

### Example 1: Voice Ramble → Structured Task

**Input:**
```
"Okay so we need to um you know fix that performance issue
in the dashboard where it's loading really slowly when there's
like a lot of data and I think maybe we should cache some stuff
or optimize the queries or something"
```

**Enhanced Output:**
```xml
<enhanced_prompt>

<task_summary>
Optimize dashboard performance when loading large datasets by implementing
caching and query optimization.
</task_summary>

<context>
<domain>Web Application Performance Optimization</domain>
<technical_context>
- Frontend: Dashboard with data visualization
- Backend: Database queries (likely SQL/NoSQL)
- Performance: Slow loading with large datasets
</technical_context>
<constraints>
- Must maintain data accuracy
- Should improve load time significantly
- Solution should be scalable
</constraints>
</context>

<skills_inventory>
**MANDATORY: Complete before starting**

Available Skills to Check:
- systematic-debugging (for root cause analysis)
- serena (for code analysis)

Relevant Skills for This Task:
- systematic-debugging: Diagnose performance bottleneck systematically
- serena: Analyze dashboard and query code

Action Required:
1. Use Skill tool to load: systematic-debugging
2. Use Skill tool to load: serena
3. Follow their guidance for investigation
</skills_inventory>

<mcp_tools_inventory>
**MANDATORY: Complete before using tools**

Recommended MCP Tools:
- mcp__serena__get_symbols_overview: Understand dashboard code structure
- mcp__serena__find_symbol: Locate query functions
- mcp__serena__find_referencing_symbols: Trace data flow
- mcp__sequential-thinking__sequentialthinking: For systematic optimization analysis

Avoid: Using grep/find for code analysis (use Serena instead)
</mcp_tools_inventory>

<thinking_framework>
**REQUIRED: Use sequential thinking for this optimization problem**

1. Call mcp__sequential-thinking__sequentialthinking
2. Systematically analyze:
   - Current implementation (queries, caching, rendering)
   - Performance bottleneck identification
   - Optimization strategies (caching, query optimization, pagination)
   - Trade-offs of each approach
3. Generate hypothesis for best solution
4. Verify against constraints
5. Propose implementation plan
</thinking_framework>

<mandatory_rules>
<!-- All 7 rules included here -->
[Full mandatory rules template from above]
</mandatory_rules>

<workflow>
<phase_1>
**Investigation & Root Cause Analysis**

1. Complete skills inventory (load systematic-debugging, serena)
2. Complete MCP tools inventory
3. Use mcp__sequential-thinking to structure investigation:
   - Hypothesis 1: Database queries are inefficient
   - Hypothesis 2: Frontend rendering is slow
   - Hypothesis 3: No caching implemented
   - Test each hypothesis systematically
4. Use mcp__serena__get_symbols_overview to understand dashboard code
5. Use mcp__serena__find_symbol to locate query functions
6. Identify actual bottleneck (don't assume - measure)
</phase_1>

<phase_2>
**Solution Design**

1. Based on root cause, design optimization:
   - If query issue: Optimize SQL, add indexes, implement query caching
   - If rendering issue: Implement virtual scrolling, pagination
   - If no caching: Add Redis/memory cache for expensive operations
2. Consider trade-offs:
   - Cache invalidation strategy
   - Memory usage
   - Complexity vs. benefit
3. Choose simplest solution that meets performance goals (Opus: avoid overengineering)
</phase_2>

<phase_3>
**Implementation & Validation**

1. Read existing code with Serena MCP (Rule #2: never change without reading)
2. Implement optimization incrementally
3. Test with large dataset to verify improvement
4. Measure before/after performance
5. Document caching strategy if implemented
6. DO NOT write tests unless user explicitly asks (Rule #1)
</phase_3>
</workflow>

<success_criteria>
- Dashboard load time reduced by at least 50% with large datasets
- Solution implemented without breaking existing functionality
- Performance improvement verified with measurements
- Code follows existing patterns
- Caching strategy documented (if implemented)
</success_criteria>

<execution_trigger>
You are now configured to optimize dashboard performance following all
guidelines, mandatory workflows, and rules specified above.

Begin by completing the skills inventory, loading systematic-debugging and serena,
then proceed through each investigation phase using sequential thinking.
</execution_trigger>

</enhanced_prompt>
```

**Transformation Applied:**
- Voice ramble → Clear task summary
- Vague idea → Specific optimization problem
- Missing workflows → Skills + MCP tools inventories added
- No structure → 3-phase workflow with sequential thinking
- No rules → All 7 mandatory rules included
- Ambiguous goal → Measurable success criteria

---

## Best Practices

### 1. Always Include Mandatory Workflows
Every enhanced prompt MUST include:
- Skills inventory template
- MCP tools inventory template
- Mandatory rules (all 7)
- Ultrathinking framework (if task is complex)

### 2. Detect Skills Intelligently
Based on task type:
- Code analysis → serena, systematic-debugging
- Testing → test-driven-development (only if tests requested)
- Git workflows → git-commit-helper
- Cloud/AWS → aws-solution-architect
- Prompts → prompt-factory

### 3. Recommend MCP Tools Over Bash
Always prefer:
- mcp__serena__* over grep/find/cat
- mcp__filesystem__* over bash file operations
- mcp__git__* over raw git commands
- mcp__sequential-thinking for complex problems

### 4. Apply Ultrathinking for Complexity
Trigger ultrathinking when:
- Multiple valid approaches exist
- Task requires architectural decisions
- Debugging complex issues
- Optimization problems
- Large refactorings

### 5. Validate Before Output
Run through 7-point validation checklist:
1. Completeness
2. Guideline compliance
3. Mandatory workflows
4. Skill detection
5. Tool detection
6. Actionability
7. XML validity

### 6. Ask for Clarification When Needed
If input is too vague or ambiguous:
- Ask 1-2 targeted questions
- Don't make assumptions
- Get clarity on constraints and goals

### 7. Keep Output Clean
- Proper XML formatting
- Clear section separation
- No placeholder text
- Actionable steps
- Measurable success criteria

---

## Limitations

### This Skill Cannot:
- Execute the enhanced prompt (only creates it)
- Implement code or features (only structures the task)
- Make decisions about architecture (provides framework for decision-making)
- Replace human judgment on complexity

### When NOT to Use:
- Prompt is already complete and well-structured
- Task is simple single-step operation (no workflow needed)
- User wants execution, not enhancement

---

## Reference Files

- **HOW_TO_USE.md**: Comprehensive usage guide with more examples
- **sample_inputs/**: Example raw inputs to enhance
- **expected_outputs/**: Example enhanced outputs
- **examples/**: Before/after transformation examples

---

**Ready to transform raw input into production-ready prompts!**
