# Structured Outputs

> Producing LLM outputs in machine-parseable formats. JSON, XML, YAML, or custom schemas. The discipline that makes prompt pipelines reliable.

## Why structured outputs matter

Prose outputs are great for humans. They're disastrous for downstream code. Structured outputs let you:

- Parse without regex archaeology
- Validate against a schema
- Compose with other prompts (the output is the next prompt's input)
- Catch failures explicitly (parse error = bad output)

## Format choice

| Format | When |
|--------|------|
| JSON | Default. Universal. Schema-checkable with JSON Schema / Pydantic / Zod. |
| YAML | When humans will edit the output (configs, plans). More forgiving than JSON. |
| XML / tag-soup | When output is mostly prose but needs structural anchors (e.g., `<answer></answer>`) |
| Markdown with strict structure | When humans read AND code parses (with discipline) |
| Custom DSL | Rarely. Costs in parser maintenance. |

Default to JSON. Move off it only with reason.

## The "JSON only" prompt pattern

The recurring problem: model adds preamble ("Here's the JSON:") that breaks parsing.

The fix:

```
Respond with valid JSON conforming to this schema:

{
  "field1": "string description",
  "field2": "type description",
  ...
}

Do not include any text outside the JSON. Do not wrap in markdown code fences.
Start your response with `{` and end with `}`.
```

Three reinforcements:
1. "Do not include any text outside"
2. "Do not wrap in markdown code fences"
3. "Start with `{` and end with `}`"

Each catches a different failure mode the model defaults to.

## Schema specification

### Pattern: Type-script-style schema in prompt

```
Respond with JSON of this type:

  type Response = {
    summary: string;       // 1-2 sentence summary
    severity: "low" | "medium" | "high" | "critical";
    affected_files: string[];
    suggested_fix: string;
  };
```

Familiar to most developers; the model handles it well.

### Pattern: JSON Schema explicit

```
Respond with JSON validating against this schema:

  {
    "type": "object",
    "required": ["summary", "severity"],
    "properties": {
      "summary": {"type": "string"},
      "severity": {"enum": ["low", "medium", "high", "critical"]},
      ...
    }
  }
```

More verbose but unambiguous. Use when the consuming code uses JSON Schema validation.

### Pattern: Example output

```
Example of valid output:

  {
    "summary": "SQL injection in user lookup endpoint",
    "severity": "high",
    "affected_files": ["src/api/users.py", "src/db/queries.py"],
    "suggested_fix": "Use parameterized queries via the orm.execute() method"
  }

Now produce the same shape for this input: ...
```

Example-driven beats schema-driven for many tasks. The model imitates the example exactly.

## Validating output

After parsing, validate:

```python
import json
from pydantic import BaseModel, ValidationError

class Response(BaseModel):
    summary: str
    severity: Literal["low", "medium", "high", "critical"]
    affected_files: list[str]
    suggested_fix: str

try:
    raw = llm_call(...)
    parsed = Response.model_validate_json(raw)
    # use parsed.summary, parsed.severity, etc.
except (json.JSONDecodeError, ValidationError) as e:
    # The model failed to produce valid output
    # Retry with the schema reminder, OR fail loudly
```

The pattern:
1. Parse JSON — catch JSONDecodeError
2. Validate schema — catch ValidationError
3. On failure, retry with a tighter format reminder OR fail to the caller

## Retry strategies

When the model fails to produce valid output:

### Strategy 1: Re-prompt with the error

```
The previous output was not valid JSON. Specific error:
  <error message>

Re-respond with valid JSON conforming to the schema. Output starts with `{`,
ends with `}`, no other text.
```

Usually fixes on retry. Cap at 2 retries; if it still fails, the prompt is the problem.

### Strategy 2: Strip prefix/suffix and re-parse

If the model added preamble despite instructions, strip aggressively:

```python
def extract_json(raw: str) -> dict:
    raw = raw.strip()
    # Strip markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json\n").rstrip()
    # Find the first { and last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    return json.loads(raw[start:end+1])
```

Lenient parsing recovers from common preamble failures.

### Strategy 3: Tag-soup fallback

For tasks where JSON is unreliable, use XML-style tags:

```
Output your response as:

<summary>One sentence</summary>
<severity>low | medium | high | critical</severity>
<affected_files>
  <file>path/to/file</file>
  ...
</affected_files>
<suggested_fix>Multi-line fix description</suggested_fix>
```

Models often handle tag-soup more reliably than JSON when the output contains complex nested prose. Extract via regex: `re.search(r'<summary>(.*?)</summary>', ...)`.

## Compositional outputs

When prompt-1's output is prompt-2's input:

```
prompt-1 → JSON output → prompt-2 (consumes structured input)
```

The structured output is the protocol between prompts. Document the schema once; both prompts reference it.

This is the Claude-to-Claude pipeline pattern. See `skills/create-meta-prompts/` for the discipline.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| "JSON output preferred" | Model treats as optional | "Respond with JSON only. No other text." |
| Schema specified once at start | Easily forgotten by end | Restate schema at end |
| No retry on parse failure | One model hiccup breaks the pipeline | Retry with error feedback |
| Trusting model output without validation | Schema drift silently breaks consumers | Validate every parsed output |
| Tag-soup AND JSON in one prompt | Model picks the wrong one | Pick one format per prompt |

## Cross-references

- `skills/prompt-engineer/` — parent skill
- `references/prompt-patterns.md` — sibling pattern catalog
- `references/system-prompts.md` — sibling system-prompt design
- `references/evaluation-frameworks.md` — how to verify output quality
- `skills/prompt-engineering-patterns/references/prompt-templates.md` — templates for structured-output prompts
- `skills/create-meta-prompts/` — pipeline-style composition
